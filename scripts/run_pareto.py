from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1]))

from lmty.compiler.pareto import Point, frontier

ROOT = Path(__file__).parents[1]


def main() -> None:
    scores = json.loads((ROOT / "reports/optimizer_scores.json").read_text(encoding="utf-8"))
    points = [Point(item["candidate"], item["quality"], item["reliability"], item["tokens"], item["latency"], item["complexity"]) for item in scores]
    result = {"objectives": {"maximize": ["quality", "reliability"], "minimize": ["tokens", "latency", "complexity"]}, "frontier": frontier(points)}
    (ROOT / "reports/pareto_multidimensional.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
