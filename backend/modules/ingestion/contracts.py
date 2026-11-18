"""Bounded ingress/result contracts; signature screening is not malware clearance."""
import hashlib,hmac,json,re,time
from uuid import UUID

MAX_BYTES=8*1024*1024
MAX_PAGES=30
MAX_OUTPUT=1024*1024
MAX_TEXT=200000
MIMES={'application/pdf':b'%PDF-','image/png':b'\x89PNG\r\n\x1a\n','image/jpeg':b'\xff\xd8\xff'}


def integer(value,low,high):
    if type(value) is not int or not low<=value<=high:raise ValueError('Invalid bounded integer')


def declaration(data):
    if type(data) is not dict or set(data)!={'byte_count','media_type','rights_claim'}:raise ValueError('Unsupported declaration fields')
    integer(data['byte_count'],1,MAX_BYTES)
    if not isinstance(data['media_type'],str) or data['media_type'] not in MIMES:raise ValueError('Unsupported upload type')
    if not isinstance(data['rights_claim'],str) or not data['rights_claim'].strip() or len(data['rights_claim'])>2000:raise ValueError('Rights claim required; claim is not clearance')
    return dict(data)


def detect_type(prefix,claimed):
    if not isinstance(prefix,bytes) or claimed not in MIMES or not prefix.startswith(MIMES[claimed]):raise ValueError('Signature/type mismatch')
    return claimed


def canonical(data):return json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')


def validate_result(result,expected):
    fields={'object_id','source_sha256','generation','dispatch_id','parser_id','media_type','page_count','quality','blocks'}
    if type(result) is not dict or set(result)!=fields or len(canonical(result))>MAX_OUTPUT:raise ValueError('Invalid or oversized parser result')
    for key in ['object_id','source_sha256','generation','dispatch_id','parser_id','media_type']:
        if result[key]!=expected[key]:raise ValueError('Parser provenance mismatch')
    integer(result['generation'],1,2**31-1)
    integer(result['page_count'],1,MAX_PAGES)
    UUID(result['object_id']);UUID(result['dispatch_id'])
    if not re.fullmatch('[0-9a-f]{64}',result['source_sha256']) or result['quality']!='needs_review':raise ValueError('Source hash/quality invalid')
    blocks=result['blocks'];seen=set();total=0
    if type(blocks) is not list or not 1<=len(blocks)<=1000:raise ValueError('Invalid block count')
    for block in blocks:
        if type(block) is not dict or set(block)!={'page','anchor','text'}:raise ValueError('Unsupported block fields')
        integer(block['page'],1,result['page_count'])
        if not isinstance(block['anchor'],str) or not re.fullmatch('[a-z0-9._-]{1,64}',block['anchor']) or block['anchor'] in seen:raise ValueError('Invalid or duplicate anchor')
        seen.add(block['anchor'])
        if not isinstance(block['text'],str) or not 1<=len(block['text'])<=2000 or any(ord(c)<32 and c not in '\n\r\t' for c in block['text']):raise ValueError('Invalid block text')
        total+=len(block['text'])
    if total>MAX_TEXT:raise ValueError('Parser text exceeds bound')
    return result


def sign_manifest(payload,key):
    if not isinstance(key,bytes) or len(key)<32:raise ValueError('Dedicated job key required')
    return {'payload':payload,'signature':hmac.new(key,canonical(payload),hashlib.sha256).hexdigest()}


def verify_manifest(envelope,key,expected,now=None):
    if type(envelope) is not dict or set(envelope)!={'payload','signature'}:raise ValueError('Invalid signed manifest')
    actual=sign_manifest(envelope['payload'],key)['signature']
    if not isinstance(envelope['signature'],str) or not hmac.compare_digest(actual,envelope['signature']):raise ValueError('Manifest signature mismatch')
    payload=envelope['payload']
    if type(payload) is not dict or set(payload)!=set(expected)|{'expires_at'}:raise ValueError('Manifest fields differ')
    for name,value in expected.items():
        if payload[name]!=value or type(payload[name]) is not type(value):raise ValueError('Manifest scope/provenance mismatch')
    current=int(time.time() if now is None else now)
    integer(payload['expires_at'],current+1,current+120)
    return payload
