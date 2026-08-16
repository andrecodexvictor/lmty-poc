from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable

from lmty.models.schema import Task
from lmty.runtime.engine import AttachmentRuntime


@dataclass
class Candidate:
    name: str
    context_budget: int
    max_tool_calls: int
    retry_policy: str
    required_tools: list[str]
    route_overrides: dict[str, list[str]]


@dataclass
class Score:
    candidate: str
    quality: float
    reliability: float
    tokens: float
    latency: float
    complexity: float
    reward: float


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _operational_metrics(candidate: Candidate, runtime: AttachmentRuntime, responses: list[Any]) -> tuple[float, float, float]:
    quality = _mean([response.verification["score"] for response in responses])
    reliability = _mean([float(response.verification["passed"]) for response in responses])
    tokens = candidate.context_budget + len(candidate.required_tools) * 18 + candidate.max_tool_calls * 4
    latency = _mean([trace["latency_ms"] for trace in runtime.export_traces()])
    return quality, reliability, round(tokens + latency, 2)


def _reward(candidate: Candidate, quality: float, reliability: float, operational: float) -> tuple[float, float, float]:
    complexity = len(candidate.route_overrides) * 2 + len(candidate.required_tools) + candidate.max_tool_calls / 10
    tokens = candidate.context_budget + len(candidate.required_tools) * 18 + candidate.max_tool_calls * 4
    latency = max(operational - tokens, 0.0)
    reward = 0.45 * quality + 0.35 * reliability - 0.0005 * tokens - 0.001 * latency - 0.01 * complexity
    return round(tokens, 2), round(latency, 2), round(reward, 4)


def score_candidate(candidate: Candidate, runtime_factory: Callable[[Candidate], AttachmentRuntime], tasks: list[Task]) -> Score:
    runtime = runtime_factory(candidate)
    responses = [runtime.infer(task) for task in tasks]
    quality, reliability, operational = _operational_metrics(candidate, runtime, responses)
    tokens, latency, reward = _reward(candidate, quality, reliability, operational)
    complexity = len(candidate.route_overrides) * 2 + len(candidate.required_tools) + candidate.max_tool_calls / 10
    return Score(candidate.name, round(quality, 4), round(reliability, 4), tokens, latency, round(complexity, 2), reward)


def _dominates(left: Score, right: Score) -> bool:
    weak = (left.reward >= right.reward, left.complexity <= right.complexity)
    strict = (left.reward > right.reward, left.complexity < right.complexity)
    return all(weak) and any(strict)


def pareto_select(scores: list[Score]) -> list[Score]:
    frontier = [item for item in scores if not any(_dominates(other, item) for other in scores if other is not item)]
    return sorted(frontier, key=lambda item: item.reward, reverse=True)


def compile_policy(candidates: list[Candidate], scores: list[Score], output_path: str | Path) -> dict[str, Any]:
    best = max(scores, key=lambda item: item.reward)
    candidate = next(item for item in candidates if item.name == best.candidate)
    artifact = {"compiler": "lmty-poc-0.1", "selected": asdict(best), "policy": asdict(candidate)}
    Path(output_path).write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
    return artifact
