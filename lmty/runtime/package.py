from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lmty.models.schema import AttachmentManifest, AttachmentPackage


class PackageError(ValueError):
    pass


def _read_json(root: Path, relative: str, default: Any) -> Any:
    path = root / relative
    text = path.read_text(encoding="utf-8") if path.exists() else None
    return default if text is None else _parse_json(text, path)


def _parse_json(text: str, path: Path) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise PackageError(f"JSON inválido em {path}: {exc}") from exc


def _manifest(data: dict[str, Any]) -> AttachmentManifest:
    required = ["name", "version", "abi", "minimum_access", "preferred_backend"]
    missing = [key for key in required if key not in data]
    if missing:
        raise PackageError(f"Campos obrigatórios ausentes: {', '.join(missing)}")
    return AttachmentManifest(
        name=data["name"], version=str(data["version"]), abi=data["abi"],
        minimum_access=data.get("minimum_access", "B0"), preferred_backend=data.get("preferred_backend", "behavioral"),
        fallback=data.get("fallback", "generalist"), context_budget=int(data.get("context_budget", 512)),
        max_tool_calls=int(data.get("max_tool_calls", 8)), capabilities=list(data.get("capabilities", [])),
        verification=list(data.get("verification", [])), compatibility=dict(data.get("compatibility", {})), policy=dict(data.get("policy", {})),
    )


def load_package(path: str | Path) -> AttachmentPackage:
    root = Path(path)
    manifest = _manifest(_read_json(root, "manifest.json", {}))
    return AttachmentPackage(
        root=str(root), manifest=manifest, policy=_read_json(root, "policy/policy.json", {}),
        routes=_read_json(root, "policy/routes.json", {}), tool_policy=_read_json(root, "policy/tool-policy.json", {}),
        verifier_policy=_read_json(root, "policy/verifier-policy.json", {}), memory_policy=_read_json(root, "policy/memory-policy.json", {}),
    )
