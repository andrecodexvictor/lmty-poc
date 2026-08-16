from __future__ import annotations

import re
from typing import Any

from lmty.models.schema import AttachmentPackage, Decision, Task


class PolicyEngine:
    def __init__(self, package: AttachmentPackage):
        self.package = package
        self.routes = package.routes
        self.tool_policy = package.tool_policy
        self.policy = package.policy

    def classify(self, task: Task) -> str:
        if task.kind != "general":
            return task.kind
        patterns = {
            "visual_ui": r"layout|responsive|visual|css|interface|ui|design",
            "bug": r"bug|erro|falha|quebrou|debug|hydration|race condition",
            "performance": r"performance|lento|latência|bundle|renderiza|otimiza",
            "accessibility": r"acessibilidade|accessibility|aria|teclado|contraste",
            "implementation": r"implementar|criar|componente|react|typescript|feature",
        }
        return next((kind for kind, pattern in patterns.items() if re.search(pattern, task.text.lower())), "general")

    def _enabled_tools(self, route: str, available: list[str]) -> list[str]:
        configured = self.tool_policy.get("allowed", self.package.manifest.capabilities)
        required = self.tool_policy.get("required_by_route", {}).get(route, [])
        names = list(dict.fromkeys(configured + required))
        return [tool for tool in names if tool in available][: self.package.manifest.max_tool_calls]

    def decide(self, task: Task, available_tools: list[str], state: dict[str, Any]) -> Decision:
        route_name = self.classify(task)
        steps = self.routes.get(route_name, self.routes.get("general", []))
        return Decision(
            route=" -> ".join(steps) or route_name,
            context_budget=self.package.manifest.context_budget,
            tools_enabled=self._enabled_tools(route_name, available_tools),
            verifiers=self.package.verifier_policy.get("by_route", {}).get(route_name, self.package.manifest.verification),
            confidence_threshold=float(self.policy.get("confidence_threshold", 0.0)),
            retry_policy=self.policy.get("retry_policy", "verify_then_retry"),
        )

    def _evidence_block(self, evidence: list[str]) -> list[str]:
        if not evidence:
            return []
        return ["EVIDÊNCIAS RELEVANTES:\n" + "\n".join(f"- {item}" for item in evidence)]

    @staticmethod
    def _join_or(names: list[str], fallback: str) -> str:
        return ", ".join(names) if names else fallback

    def compile_context(self, task: Task, decision: Decision, evidence: list[str]) -> str:
        base = [
            f"DOMÍNIO: {self.package.manifest.name}",
            f"ROTA: {decision.route}",
            f"TAREFA: {task.text}",
            f"FERRAMENTAS AUTORIZADAS: {self._join_or(decision.tools_enabled, 'nenhuma')}",
            f"VERIFICADORES OBRIGATÓRIOS: {self._join_or(decision.verifiers, 'nenhum')}",
        ]
        return "\n".join(base + self._evidence_block(evidence))
