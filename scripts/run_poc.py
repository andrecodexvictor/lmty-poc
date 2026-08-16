from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parents[1]))

from lmty.compiler.optimizer import Candidate, compile_policy, pareto_select, score_candidate
from lmty.evals.benchmark import FRONTEND_TASKS, evaluate_runtime
from lmty.runtime.engine import AttachmentRuntime
from lmty.runtime.package import load_package

ROOT = Path(__file__).parents[1]
PACKAGE_PATH = ROOT / "examples" / "frontend.lmty"
REPORTS = ROOT / "reports"


def runtime_factory(candidate: Candidate) -> AttachmentRuntime:
    package = load_package(PACKAGE_PATH)
    package.manifest.context_budget = candidate.context_budget
    package.manifest.max_tool_calls = candidate.max_tool_calls
    package.policy["retry_policy"] = candidate.retry_policy
    if candidate.required_tools:
        package.tool_policy["allowed"] = candidate.required_tools
    return AttachmentRuntime(package)


def main() -> None:
    package = load_package(PACKAGE_PATH)
    runtime = AttachmentRuntime(package)
    benchmark = evaluate_runtime(runtime)
    candidates = [
        Candidate("baseline-general", 900, 12, "none", [], {}),
        Candidate("frontend-balanced", 420, 8, "verify_then_retry", ["filesystem", "browser", "test_runner", "typecheck", "visual_verify", "accessibility"], {}),
        Candidate("frontend-compact", 280, 4, "verify_then_retry", ["filesystem", "test_runner", "typecheck"], {"visual_ui": ["inspect_repo", "render", "visual_verify"]}),
    ]
    scores = [score_candidate(candidate, runtime_factory, FRONTEND_TASKS) for candidate in candidates]
    pareto = pareto_select(scores)
    artifact = compile_policy(candidates, scores, REPORTS / "frontend.compiled.lmty.json")
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "benchmark.json").write_text(json.dumps(benchmark, indent=2, ensure_ascii=False), encoding="utf-8")
    (REPORTS / "optimizer_scores.json").write_text(json.dumps([s.__dict__ for s in scores], indent=2, ensure_ascii=False), encoding="utf-8")
    (REPORTS / "pareto_frontier.json").write_text(json.dumps([s.__dict__ for s in pareto], indent=2, ensure_ascii=False), encoding="utf-8")
    (REPORTS / "runtime_traces.json").write_text(json.dumps(runtime.export_traces(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"benchmark": benchmark, "scores": [s.__dict__ for s in scores], "pareto": [s.__dict__ for s in pareto], "artifact": artifact}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
