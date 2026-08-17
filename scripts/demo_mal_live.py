from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1]))

from lmty.models.schema import Task
from lmty.runtime.engine import AttachmentRuntime
from lmty.runtime.package import load_package

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "examples/frontend.lmty"
SESSION = "mal-live-demo"
AVAILABLE_TOOLS = ["filesystem", "test_runner", "typecheck"]


def main() -> None:
    runtime = AttachmentRuntime(load_package(PACKAGE))
    first = runtime.infer(Task("mal-live-001", "Investigar bug de hydration e reproduzir o erro", "bug"), AVAILABLE_TOOLS, ["o projeto usa React e TypeScript"], SESSION)
    second = runtime.infer(Task("mal-live-002", "Continuar o diagnóstico e preparar teste de regressão", "bug"), AVAILABLE_TOOLS, ["a primeira execução já identificou a classe bug"], SESSION)
    report = {
        "session": SESSION,
        "attachment": first.attachment,
        "capability_boundary": {
            "available_tools": AVAILABLE_TOOLS,
            "browser_enabled": "browser" in first.decision.tools_enabled,
            "test_runner_enabled": "test_runner" in first.decision.tools_enabled,
        },
        "calls": [
            {"task_id": first.task_id, "route": first.route, "tools": first.decision.tools_enabled, "verification": first.verification, "trace_id": first.trace_id},
            {"task_id": second.task_id, "route": second.route, "tools": second.decision.tools_enabled, "verification": second.verification, "trace_id": second.trace_id},
        ],
        "persistent_state": runtime.state[SESSION],
        "invariants": {
            "same_session": first.trace_id != second.trace_id and runtime.state[SESSION]["calls"] == 2,
            "browser_not_granted": "browser" not in first.decision.tools_enabled,
            "verification_passed": first.verification["passed"] and second.verification["passed"],
            "trace_count": len(runtime.export_traces()),
        },
        "traces": runtime.export_traces(),
    }
    output = ROOT / "reports/mal_live_demo.json"
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
