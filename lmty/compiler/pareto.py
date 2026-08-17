from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable


@dataclass(frozen=True)
class Point:
    name: str
    quality: float
    reliability: float
    tokens: float
    latency: float
    complexity: float


def _better_or_equal(left: Point, right: Point) -> bool:
    values = (left.quality >= right.quality, left.reliability >= right.reliability, left.tokens <= right.tokens, left.latency <= right.latency, left.complexity <= right.complexity)
    return all(values)


def _strictly_better(left: Point, right: Point) -> bool:
    values = (left.quality > right.quality, left.reliability > right.reliability, left.tokens < right.tokens, left.latency < right.latency, left.complexity < right.complexity)
    return any(values)


def dominates(left: Point, right: Point) -> bool:
    return _better_or_equal(left, right) and _strictly_better(left, right)


def frontier(points: Iterable[Point]) -> list[dict[str, float | str]]:
    values = list(points)
    result = [point for point in values if not any(dominates(other, point) for other in values if other != point)]
    return [asdict(point) for point in result]
