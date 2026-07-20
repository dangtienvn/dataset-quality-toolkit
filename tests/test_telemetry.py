from saas_starter.core.telemetry import MetricsCollector

def test_metrics():
    m = MetricsCollector()
    m.increment_counter("queries")
    assert m.metrics["queries"] == 1
