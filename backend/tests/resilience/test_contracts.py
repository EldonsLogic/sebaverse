from dataclasses import replace
import pytest
from modules.providers.contracts import Request, Receipt, ProviderFailure, choose, validate_receipt
from modules.operations.transitions import may_claim, may_finish, retry_delay


@pytest.mark.parametrize('field,value', [('max_input',True),('max_input',-1),('max_output',0),
                                         ('max_output',100001),('audio_ms',-1),('task','shell'),('schema','anything')])
def test_unbounded_or_unsupported_request_denied(field,value):
    with pytest.raises(ValueError): replace(Request(),**{field:value}).validate()


@pytest.mark.parametrize('field,value', [('input_tokens',True),('cached_tokens',11),('output_tokens',101),
                                         ('audio_ms',1),('request_id',''),('charge_units',-1)])
def test_bad_usage_receipt_cannot_settle(field,value):
    r=Receipt('mock.request',10,0,10,0,20,'mock-v1')
    with pytest.raises(ValueError): validate_receipt(replace(r,**{field:value}),Request(max_input=10,max_output=100))


def test_eligibility_precedes_cheapest_candidate():
    with pytest.raises(ValueError): choose([{'id':'unknown','eligible':True,'cost':0}])
    assert choose([{'id':'mock-a','eligible':False,'cost':0},{'id':'mock-b','eligible':True,'cost':1}])=='mock-b'


@pytest.mark.parametrize('status',['succeeded','failed','cancelled','unknown','running'])
def test_terminal_or_running_work_cannot_be_claimed(status):
    assert not may_claim(status,0,3,True)


@pytest.mark.parametrize('same_fence,live,authorized',[(False,True,True),(True,False,True),(True,True,False)])
def test_stale_expired_or_revoked_work_cannot_complete(same_fence,live,authorized):
    assert not may_finish('running',same_fence,live,authorized)


def test_unknown_billing_is_not_a_retryable_free_failure():
    assert not ProviderFailure('timeout',True,'unknown').safe_to_retry
    assert ProviderFailure('unavailable',True,'not_billed').safe_to_retry
    assert [retry_delay(n) for n in [1,2,3]]==[2,4,8]


def test_provider_substitution_preserves_normalized_usage_and_cancel_contract():
    from modules.providers.mock import MockProvider,AlternateMockProvider
    for adapter in [MockProvider(),AlternateMockProvider()]:
        receipt=adapter.generate(Request(),'fixture-dispatch')
        assert validate_receipt(receipt,Request()).charge_units==20
        assert adapter.cancel('fixture-dispatch')['status']=='cancel_requested'


def test_outer_transaction_blocks_dispatch_before_claim_or_provider_effect(monkeypatch):
    from django.db import connection
    from modules.operations.service import run_once,Conflict
    from modules.providers.mock import MockProvider
    monkeypatch.setattr(connection,'in_atomic_block',True)
    with pytest.raises(Conflict):run_once('not-a-database-id',MockProvider())
