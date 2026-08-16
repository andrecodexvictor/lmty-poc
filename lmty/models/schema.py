from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Task:
    id: str
    text: str
    kind: str = "general"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AttachmentManifest:
    name: str
    version: str
    abi: str
    minimum_access: str
    preferred_backend: str
    fallback: str
    context_budget: int
    max_tool_calls: int
    capabilities: list[str]
    verification: list[str]
    compatibility: dict[str, Any] = field(default_factory=dict)
    policy: dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    route: str
    context_budget: int
    tools_enabled: list[str]
    verifiers: list[str]
    confidence_threshold: float = 0.0
    retry_policy: str = "none"


@dataclass
class AttachmentPackage:
    root: str
    manifest: AttachmentManifest
    policy: dict[str, Any]
    routes: dict[str, list[str]]
    tool_policy: dict[str, Any]
    verifier_policy: dict[str, Any]
    memory_policy: dict[str, Any]


@dataclass
class RuntimeResponse:
    task_id: str
    attachment: str
    route: str
    output: str
    decision: Decision
    verification: dict[str, Any]
    trace_id: str
    fallback: bool = False
