from saas_starter.core.rate_limit import TokenBucketRateLimiter

def test_rate_limiter():
    limiter = TokenBucketRateLimiter(capacity=2, refill_rate=0.1)
    assert limiter.consume() is True
    assert limiter.consume() is True
    assert limiter.consume() is False
