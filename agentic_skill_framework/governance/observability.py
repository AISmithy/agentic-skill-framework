import time
from typing import Optional

class ObservabilityManager:
    def __init__(self):
        self._metrics: dict[str, list[dict]] = {}
        self._traces: dict[str, dict] = {}
        self._evals: list[dict] = []

    def record_metric(self, name: str, value: float, labels: dict = None) -> None:
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append({"value": value, "labels": labels or {}, "timestamp": time.time()})

    def get_metrics(self, name: str = None) -> dict:
        if name:
            return {name: self._metrics.get(name, [])}
        return dict(self._metrics)

    def start_trace(self, trace_id: str, operation: str) -> dict:
        trace = {"trace_id": trace_id, "operation": operation, "start_time": time.time(), "end_time": None, "status": "running", "duration_ms": None}
        self._traces[trace_id] = trace
        return trace

    def end_trace(self, trace_id: str, status: str = "ok") -> dict:
        trace = self._traces.get(trace_id, {})
        if trace:
            trace["end_time"] = time.time()
            trace["status"] = status
            trace["duration_ms"] = (trace["end_time"] - trace["start_time"]) * 1000
        return trace

    def record_eval(self, eval_id: str, metric: str, score: float, details: dict = None) -> None:
        self._evals.append({"eval_id": eval_id, "metric": metric, "score": score, "details": details or {}})

    def get_evals(self, eval_id: str = None) -> list[dict]:
        if eval_id:
            return [e for e in self._evals if e["eval_id"] == eval_id]
        return list(self._evals)

    def summary(self) -> dict:
        return {
            "total_metrics": len(self._metrics),
            "total_traces": len(self._traces),
            "total_evals": len(self._evals),
            "metric_names": list(self._metrics.keys()),
            "trace_ids": list(self._traces.keys())
        }
