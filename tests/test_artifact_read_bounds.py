from __future__ import annotations

import tracemalloc
from io import BytesIO
from pathlib import Path

import pytest

from developer_lens_lab.artifacts import ArtifactError, ArtifactStore


@pytest.mark.parametrize("operation", ["get", "put"])
@pytest.mark.parametrize(
    ("payload", "stored"),
    [
        pytest.param(b"x", b"x", id="exact"),
        pytest.param(b"x", b"x" * 4096, id="oversized"),
        pytest.param(b"xy", b"x", id="truncated"),
        pytest.param(b"x", b"y", id="wrong-digest"),
        pytest.param(b"", b"", id="empty"),
        pytest.param(b"", b"x" * 4096, id="empty-oversized"),
    ],
)
def test_object_reads_are_bounded_by_expected_payload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
    payload: bytes,
    stored: bytes,
) -> None:
    store = ArtifactStore(tmp_path / ".dllab")
    reference = store.put_bytes("scope_demo", payload, "application/json")
    digest = reference.sha256.removeprefix("sha256:")
    object_path = store.scope_root("scope_demo") / "objects" / digest[:2] / digest
    object_path.write_bytes(stored)
    limit = len(payload) + 1
    reads: list[int | None] = []
    consumed = 0

    class GuardedStream(BytesIO):
        def read(self, size: int | None = -1) -> bytes:
            nonlocal consumed
            reads.append(size)
            assert size is not None and 0 <= size <= limit - consumed, (
                f"unbounded or excessive read({size})"
            )
            result = super().read(size)
            consumed += len(result)
            return result

    def open_object(path: Path, mode: str = "r", **kwargs: object) -> GuardedStream:
        assert path == object_path
        assert mode == "rb"
        return GuardedStream(stored)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "open", open_object)
        if stored != payload:
            with pytest.raises(ArtifactError, match="verification"):
                if operation == "get":
                    store.get_bytes("scope_demo", reference)
                else:
                    store.put_bytes("scope_demo", payload, "application/json")
        elif operation == "get":
            assert store.get_bytes("scope_demo", reference) == payload
        else:
            assert store.put_bytes("scope_demo", payload, "application/json") == reference

    assert len(reads) == 1
    assert consumed == min(len(stored), limit)
    assert object_path.read_bytes() == stored


def test_forged_size_does_not_size_the_read_buffer(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / ".dllab")
    reference = store.put_bytes("scope_demo", b"x", "application/json")
    forged = reference.model_copy(update={"size_bytes": 2_000_000_000})

    tracemalloc.start()
    try:
        with pytest.raises(ArtifactError, match="verification"):
            store.get_bytes("scope_demo", forged)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    assert peak < 10_000_000
