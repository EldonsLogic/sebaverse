from dataclasses import dataclass, asdict
import hashlib
import json
import re


def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError('Invalid bounded unit count')


@dataclass(frozen=True)
class Request:
    task: str = 'synthetic'
    schema: str = 'mock.v1'
    max_input: int = 100
    max_output: int = 100
    audio_ms: int = 0

    def validate(self):
        if self.task != 'synthetic' or self.schema != 'mock.v1':
            raise ValueError('Only reviewed synthetic tasks are enabled')
        integer(self.max_input,0,100000)
        integer(self.max_output,1,100000)
        integer(self.audio_ms,0,60000)
        return self

    @property
    def reserve(self):
        self.validate()
        return self.max_input+self.max_output+(self.audio_ms+999)//1000

    def digest(self, resource_id):
        self.validate()
        return hashlib.sha256(json.dumps({'resource':str(resource_id),**asdict(self)},sort_keys=True).encode()).hexdigest()


@dataclass(frozen=True)
class Receipt:
    request_id: str
    input_tokens: int
    cached_tokens: int
    output_tokens: int
    audio_ms: int
    charge_units: int
    price_version: str


def validate_receipt(receipt, request):
    request.validate()
    if not isinstance(receipt,Receipt) or not isinstance(receipt.request_id,str) or not re.fullmatch(r'[a-zA-Z0-9._-]{1,96}',receipt.request_id):
        raise ValueError('Invalid usage receipt')
    for value,limit in [(receipt.input_tokens,request.max_input),(receipt.cached_tokens,receipt.input_tokens),
                        (receipt.output_tokens,request.max_output),(receipt.audio_ms,request.audio_ms),
                        (receipt.charge_units,request.reserve)]:
        integer(value,0,limit)
    expected=receipt.input_tokens-receipt.cached_tokens+receipt.output_tokens+(receipt.audio_ms+999)//1000
    if receipt.price_version!='mock-v1' or receipt.charge_units!=expected:
        raise ValueError('Usage receipt tariff or total mismatch')
    return receipt


class ProviderFailure(Exception):
    def __init__(self,code,retryable,billing):
        if code not in {'timeout','unavailable','cancelled','invalid'} or type(retryable) is not bool or billing not in {'not_billed','unknown'}:
            raise ValueError('Invalid normalized provider failure')
        self.code,self.retryable,self.billing=code,retryable,billing
        super().__init__(code)

    @property
    def safe_to_retry(self):
        return self.retryable and self.billing=='not_billed'


def choose(candidates):
    eligible=[row for row in candidates if row.get('id') in {'mock-a','mock-b'} and row.get('eligible') is True]
    if not eligible:
        raise ValueError('No reviewed eligible mock provider')
    return min(eligible,key=lambda row:(row['cost'],row['id']))['id']
