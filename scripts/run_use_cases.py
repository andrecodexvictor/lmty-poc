from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1]))

from lmty.models.schema import Task
from lmty.runtime.engine import AttachmentRuntime
from lmty.runtime.package import load_package

ROOT = Path(__file__).parents[1]


def run_case(runtime: AttachmentRuntime, case: dict) -> dict:
    result = runtime.infer(Task(case["id"], case["task"], case["kind"]), session_id=case["layer"])
    route_ok = runtime.policy.classify(Task(case["id"], case["task"], case["kind"])) == case["expected_route"]
    tools_ok = all(tool in result.decision.tools_enabled for tool in case["required_tools"])
    return {"id": case["id"], "layer": case["layer"], "route_ok": route_ok, "tools_ok": tools_ok, "verification": result.verification["passed"], "trace_id": result.trace_id}


def main() -> None:
    cases = json.loads((ROOT / "tests/use_cases.json").read_text(encoding="utf-8"))
    runtime = AttachmentRuntime(load_package(ROOT / "examples/frontend.lmty"))
    results = [run_case(runtime, case) for case in cases]
    report = {"total": len(results), "passed": sum(all(item[key] for key in ("route_ok", "tools_ok", "verification")) for item in results), "results": results}
    (ROOT / "reports/use_cases.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
