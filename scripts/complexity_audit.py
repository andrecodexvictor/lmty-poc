from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def complexity(node: ast.AST) -> int:
    branches = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler)
    bool_ops = (ast.And, ast.Or)
    return 1 + sum(isinstance(child, branches) for child in ast.walk(node)) + sum(
        isinstance(child, bool_ops) for child in ast.walk(node)
    )


def audit_file(path: Path) -> list[dict[str, object]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            findings.append({"file": str(path.relative_to(ROOT)), "function": node.name, "line": node.lineno, "complexity": complexity(node)})
    return findings


findings = []
for path in sorted((ROOT / "lmty").rglob("*.py")):
    findings.extend(audit_file(path))
summary = {
    "target": 2,
    "functions": len(findings),
    "max_complexity": max((item["complexity"] for item in findings), default=0),
    "mean_complexity": round(sum(item["complexity"] for item in findings) / len(findings), 3) if findings else 0,
    "over_target": [item for item in findings if item["complexity"] > 2],
    "details": findings,
}
print(json.dumps(summary, indent=2, ensure_ascii=False))
