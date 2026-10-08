from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from pydantic import BaseModel

from developer_lens_lab.contracts import EvaluationBundle, ResearchPack

type SchemaModel = type[BaseModel]

SCHEMAS: tuple[tuple[Path, SchemaModel, str], ...] = (
    (
        Path("schemas/research-pack/v1/consumer.schema.json"),
        ResearchPack,
        "https://developer-lens-lab.invalid/schemas/research-pack/v1/consumer.schema.json",
    ),
    (
        Path("schemas/evaluation-bundle/v1/schema.json"),
        EvaluationBundle,
        "https://developer-lens-lab.invalid/schemas/evaluation-bundle/v1/schema.json",
    ),
)


def rendered_schemas(root: Path) -> dict[Path, str]:
    outputs: dict[Path, str] = {}
    for relative, model, schema_id in SCHEMAS:
        schema = model.model_json_schema(mode="validation")
        schema["$id"] = schema_id
        outputs[root / relative] = json.dumps(schema, indent=2, sort_keys=True) + "\n"
    return outputs


def render_schemas(root: Path) -> None:
    outputs = rendered_schemas(root)
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
    originals: dict[Path, bytes | None] = {}
    for path in outputs:
        try:
            originals[path] = path.read_bytes()
        except OSError:
            originals[path] = None
    staged: list[tuple[Path, Path]] = []
    try:
        for path, content in outputs.items():
            fd, tmp_name = tempfile.mkstemp(
                prefix=f"{path.name}.", suffix=".tmp", dir=str(path.parent)
            )
            tmp = Path(tmp_name)
            try:
                with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                    handle.write(content)
            except BaseException:
                try:
                    tmp.unlink(missing_ok=True)
                except OSError:
                    pass
                raise
            staged.append((path, tmp))
        for path in outputs:
            if path.exists():
                with open(path, "r+b"):
                    pass
        replaced: list[Path] = []
        try:
            for path, tmp in staged:
                os.replace(tmp, path)
                replaced.append(path)
        except OSError:
            for done in replaced:
                original = originals.get(done)
                try:
                    if original is None:
                        done.unlink(missing_ok=True)
                    else:
                        fd, tmp_name = tempfile.mkstemp(
                            prefix=f"{done.name}.",
                            suffix=".rollback.tmp",
                            dir=str(done.parent),
                        )
                        try:
                            with os.fdopen(fd, "wb") as handle:
                                handle.write(original)
                            os.replace(tmp_name, done)
                        except OSError:
                            try:
                                Path(tmp_name).unlink(missing_ok=True)
                            except OSError:
                                pass
                            raise
                except OSError:
                    pass
            raise
    finally:
        for _, tmp in staged:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass


def check_schemas(root: Path) -> tuple[str, ...]:
    failures: list[str] = []
    for path, expected in rendered_schemas(root).items():
        try:
            actual = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            failures.append(f"missing/unreadable generated schema: {path.relative_to(root)}")
        else:
            if actual != expected:
                failures.append(f"drifted generated schema: {path.relative_to(root)}")
    return tuple(failures)
