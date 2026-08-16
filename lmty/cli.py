from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from lmty.evals.benchmark import evaluate_runtime
from lmty.models.schema import Task
from lmty.runtime.engine import AttachmentRuntime
from lmty.runtime.package import load_package


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lmty")
    parser.add_argument("--attachment", default="examples/frontend.lmty")
    sub = parser.add_subparsers(dest="command", required=True)
    infer = sub.add_parser("infer")
    infer.add_argument("text")
    infer.add_argument("--kind", default="general")
    sub.add_parser("benchmark")
    return parser


def _infer(args: Any, runtime: AttachmentRuntime) -> None:
    result = runtime.infer(Task("cli-task", args.text, args.kind))
    payload = {"output": result.output, "route": result.route, "verification": result.verification, "trace_id": result.trace_id}
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _benchmark(_: Any, runtime: AttachmentRuntime) -> None:
    result = evaluate_runtime(runtime)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    Path("reports").mkdir(exist_ok=True)
    Path("reports/runtime_traces.json").write_text(json.dumps(runtime.export_traces(), ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    args = _parser().parse_args()
    runtime = AttachmentRuntime(load_package(args.attachment))
    handlers: dict[str, Callable[[Any, AttachmentRuntime], None]] = {"infer": _infer, "benchmark": _benchmark}
    handlers[args.command](args, runtime)


if __name__ == "__main__":
    main()
