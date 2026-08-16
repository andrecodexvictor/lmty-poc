from __future__ import annotations

from typing import Any

from lmty.models.schema import Task
from lmty.runtime.engine import AttachmentRuntime


FRONTEND_TASKS = [
    Task("ui-001", "Implementar um formulário React responsivo com validação TypeScript", "implementation"),
    Task("ui-002", "Corrigir bug de hydration em uma interface React", "bug"),
    Task("ui-003", "Reproduzir layout visual responsivo para desktop e mobile", "visual_ui"),
    Task("ui-004", "Melhorar acessibilidade com teclado, ARIA e contraste", "accessibility"),
    Task("ui-005", "Investigar performance de bundle e re-renderizações", "performance"),
    Task("ui-006", "Criar componente de tabela com estados de loading e erro", "implementation"),
]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _summary(responses: list[Any], traces: list[dict[str, Any]]) -> dict[str, float]:
    return {
        "quality_mean": round(_mean([response.verification["score"] for response in responses]), 4),
        "reliability": round(_mean([float(response.verification["passed"]) for response in responses]), 4),
        "output_chars_mean": round(_mean([len(response.output) for response in responses]), 2),
        "latency_ms_mean": round(_mean([trace["latency_ms"] for trace in traces]), 3),
    }


def evaluate_runtime(runtime: AttachmentRuntime, tasks: list[Task] | None = None) -> dict[str, Any]:
    selected = tasks or FRONTEND_TASKS
    responses = [runtime.infer(task) for task in selected]
    traces = runtime.export_traces()[-len(selected):]
    result = {"tasks": len(selected), **_summary(responses, traces)}
    result["routes"] = {task.id: response.route for task, response in zip(selected, responses)}
    return result
