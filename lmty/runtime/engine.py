from __future__ import annotations

import time
import uuid
from typing import Any, Callable

from lmty.models.schema import AttachmentPackage, RuntimeResponse, Task
from lmty.runtime.policy import PolicyEngine
from lmty.runtime.verification import Verifier


class AttachmentRuntime:
    def __init__(self, package: AttachmentPackage, model: Callable[[str], str] | None = None):
        self.package = package
        self.policy = PolicyEngine(package)
        self.verifier = Verifier()
        self.model = model or self._default_model
        self.state: dict[str, dict[str, Any]] = {}
        self.traces: list[dict[str, Any]] = []

    @staticmethod
    def _default_model(prompt: str) -> str:
        return "POC response: tarefa processada com política de especialização, ferramentas limitadas e verificação externa."

    def _session(self, session_id: str) -> dict[str, Any]:
        return self.state.setdefault(session_id, {"calls": 0, "attachment": self.package.manifest.name})

    def _generate(self, context: str, task: Task, decision: Any) -> tuple[str, dict[str, Any]]:
        output = self.model(context)
        verification = self.verifier.verify(task, output, decision)
        return output, verification

    def _repair(self, context: str, task: Task, decision: Any, output: str, verification: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        should_retry = not verification["passed"] and decision.retry_policy != "none"
        retry_context = context + "\nREPARO: revise a resposta para satisfazer todos os verificadores."
        return self._generate(retry_context if should_retry else context, task, decision)

    def _trace(self, task: Task, decision: Any, verification: dict[str, Any], output: str, started: float, session_id: str) -> str:
        trace_id = str(uuid.uuid4())
        self.traces.append({
            "trace_id": trace_id,
            "task_id": task.id,
            "attachment": f"{self.package.manifest.name}@{self.package.manifest.version}",
            "session_id": session_id,
            "route": decision.route,
            "tools_enabled": decision.tools_enabled,
            "verifiers": decision.verifiers,
            "output_chars": len(output),
            "latency_ms": round((time.perf_counter() - started) * 1000, 3),
            "verification": verification,
            "state_calls": self.state[session_id]["calls"],
        })
        return trace_id

    @staticmethod
    def _value_or(value: list[str] | None, default: list[str]) -> list[str]:
        return value if value is not None else default

    def infer(self, task: Task, available_tools: list[str] | None = None, evidence: list[str] | None = None, session_id: str = "default") -> RuntimeResponse:
        started = time.perf_counter()
        tools = self._value_or(available_tools, self.package.manifest.capabilities)
        decision = self.policy.decide(task, tools, self._session(session_id))
        context = self.policy.compile_context(task, decision, self._value_or(evidence, []))
        output, verification = self._generate(context, task, decision)
        output, verification = self._repair(context, task, decision, output, verification)
        self.state[session_id]["calls"] += 1
        trace_id = self._trace(task, decision, verification, output, started, session_id)
        return RuntimeResponse(task.id, f"{self.package.manifest.name}@{self.package.manifest.version}", decision.route, output, decision, verification, trace_id)

    def export_traces(self) -> list[dict[str, Any]]:
        return list(self.traces)
