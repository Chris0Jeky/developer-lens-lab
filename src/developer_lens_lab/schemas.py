from __future__ import annotations

import json
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
    for path, content in rendered_schemas(root).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")


def check_schemas(root: Path) -> tuple[str, ...]:
    failures: list[str] = []
    for path, expected in rendered_schemas(root).items():
        if not path.is_file():
            failures.append(f"missing generated schema: {path.relative_to(root)}")
        elif path.read_text(encoding="utf-8") != expected:
            failures.append(f"drifted generated schema: {path.relative_to(root)}")
    return tuple(failures)
