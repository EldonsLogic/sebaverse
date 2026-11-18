def may_claim(status,attempts,maximum,due):
    return status in {'queued','waiting_retry'} and due and attempts < maximum


def may_finish(status,same_fence,lease_live,authorized):
    return status=='running' and same_fence and lease_live and authorized


def retry_delay(attempt):
    if type(attempt) is not int or not 1 <= attempt <= 3:
        raise ValueError('Retry limit exceeded')
    return min(2**attempt,8)
