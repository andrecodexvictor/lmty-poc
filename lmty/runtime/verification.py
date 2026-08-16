from __future__ import annotations

import re
from typing import Any, Callable

from lmty.models.schema import Decision, Task


def _nonempty(_: Task, output: str) -> dict[str, Any]:
    return {"passed": bool(output.strip()), "reason": "POC textual contract"}


def _a11y(_: Task, output: str) -> dict[str, Any]:
    bad = re.search(r"sem alt|sem aria|ignore acessibilidade", output.lower())
    return {"passed": not bool(bad), "reason": "heurística de acessibilidade"}


def _visual(task: Task, _: str) -> dict[str, Any]:
    return {"passed": bool(re.search(r"visual|layout", task.text.lower())), "reason": "sinal de tarefa visual"}


def _security(_: Task, output: str) -> dict[str, Any]:
    bad = re.search(r"exfiltrat|secret|bypass|disable security", output.lower())
    return {"passed": not bool(bad), "reason": "checagem textual de segurança"}


STRATEGIES: dict[str, Callable[[Task, str], dict[str, Any]]] = {
    "typecheck": _nonempty,
    "tests": _nonempty,
    "scoped_tests": _nonempty,
    "a11y": _a11y,
    "accessibility": _a11y,
    "visual": _visual,
    "visual_diff": _visual,
    "security": _security,
}


class Verifier:
    def verify(self, task: Task, output: str, decision: Decision) -> dict[str, Any]:
        checks = {name: STRATEGIES.get(name, _nonempty)(task, output) for name in decision.verifiers}
        score = sum(check["passed"] for check in checks.values()) / len(checks) if checks else 1.0
        return {"passed": score == 1.0, "score": round(score, 4), "checks": checks}
