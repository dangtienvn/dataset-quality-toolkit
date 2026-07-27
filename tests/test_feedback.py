from saas_starter.copilot.feedback import FeedbackCollector

def test_feedback():
    fc = FeedbackCollector()
    res = fc.record_feedback("msg-1", 5)
    assert res["rating"] == 5
