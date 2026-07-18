class MetricsCollector:
    def __init__(self):
        self.metrics = {}

    def increment_counter(self, name: str, value: int = 1):
        self.metrics[name] = self.metrics.get(name, 0) + value

    def record_latency(self, name: str, latency_ms: float):
        self.metrics[f"{name}_latency"] = latency_ms
