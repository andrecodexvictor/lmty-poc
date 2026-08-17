from __future__ import annotations

import argparse
import gzip
import json
import os
import time
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).parents[1]
DATA = ROOT / "vendor/human-eval/data/HumanEval.jsonl.gz"


def load_tasks(limit: int) -> list[dict]:
    with gzip.open(DATA, "rt", encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle]
    return rows[:limit]


def prompt_for(task: dict) -> str:
    return "Complete the following Python function. Return only the completed code, without markdown fences.\n\n" + task["prompt"]


def static_score(task: dict, output: str) -> dict[str, object]:
    signature = task["entry_point"]
    has_signature = f"def {signature}" in output
    has_fence = "```" in output
    nonempty = bool(output.strip())
    score = sum((nonempty, has_signature, not has_fence)) / 3
    return {"nonempty": nonempty, "has_signature": has_signature, "has_markdown_fence": has_fence, "static_score": round(score, 4)}


def evaluate(limit: int, model: str) -> dict[str, object]:
    client = OpenAI()
    results = []
    for task in load_tasks(limit):
        started = time.perf_counter()
        response = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt_for(task)}], max_completion_tokens=800)
        output = response.choices[0].message.content or ""
        usage = response.usage
        results.append({
            "task_id": task["task_id"],
            "entry_point": task["entry_point"],
            "model": model,
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "prompt_tokens": getattr(usage, "prompt_tokens", None),
            "completion_tokens": getattr(usage, "completion_tokens", None),
            "static": static_score(task, output),
            "completion": output,
        })
    mean_score = sum(item["static"]["static_score"] for item in results) / len(results) if results else 0.0
    return {"source": "openai/human-eval", "source_file": str(DATA.relative_to(ROOT)), "model": model, "tasks": len(results), "mean_static_score": round(mean_score, 4), "execution": "disabled_for_safety", "results": results}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--model", default=os.getenv("LMTY_CODING_MODEL", "gpt-5-mini"))
    args = parser.parse_args()
    report = evaluate(args.limit, args.model)
    output = ROOT / "reports/public_coding_eval.json"
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("source", "model", "tasks", "mean_static_score", "execution")}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
