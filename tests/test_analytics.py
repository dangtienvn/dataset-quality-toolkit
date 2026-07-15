from saas_starter.knowledge.stats import DatasetAnalytics

def test_stats():
    da = DatasetAnalytics()
    res = da.compute_stats(["hello", "world"])
    assert res["total_chunks"] == 2
