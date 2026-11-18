"""Negative fixtures first: uploaded data can never grant authority."""
import copy
import hashlib
from uuid import uuid4
import pytest
from modules.ingestion.contracts import declaration,validate_result,detect_type,MAX_BYTES


@pytest.mark.parametrize('field,value', [('byte_count',True),('byte_count',0),('byte_count',MAX_BYTES+1),
                                         ('media_type','application/zip'),('rights_claim',''),('filename','../../secret'),
                                         ('approved',True),('training_allowed',True)])
def test_invalid_or_authority_expanding_upload_declaration_rejected(field,value):
    value_dict={'byte_count':100,'media_type':'application/pdf','rights_claim':'fixture permission claim'}
    value_dict[field]=value
    with pytest.raises(ValueError):declaration(value_dict)


@pytest.mark.parametrize('data,mime',[(b'PK\x03\x04zip','application/pdf'),(b'<script>','image/png'),(b'%PDF-1.7\n','image/jpeg'),(b'\x89PNG\r\n\x1a\n','application/pdf')])
def test_signature_mismatch_and_archives_are_not_accepted(data,mime):
    with pytest.raises(ValueError):detect_type(data,mime)


def valid():
    source=b'authored fixture'
    expected={'object_id':str(uuid4()),'source_sha256':hashlib.sha256(source).hexdigest(),
              'generation':1,'dispatch_id':str(uuid4()),'parser_id':'fixture-parser.v1','media_type':'application/pdf'}
    result={**expected,'page_count':1,'quality':'needs_review','blocks':[{'page':1,'anchor':'p1.b1','text':'German, maths or science fixture.'}]}
    return expected,result


@pytest.mark.parametrize('field,value',[('source_sha256','0'*64),('generation',2),('parser_id','unreviewed'),
                                         ('page_count',True),('page_count',100000),('quality','approved'),
                                         ('blocks',[{'page':2,'anchor':'b','text':'wrong page'}]),('publish',True)])
def test_broker_rejects_wrong_provenance_unbounded_or_authority_expanding_result(field,value):
    expected,result=valid();result[field]=value
    with pytest.raises(ValueError):validate_result(result,expected)


def test_result_is_bounded_review_required_and_retains_source_notation():
    expected,result=valid();result['blocks'][0]['text']='س + ٢ = ٧ — Ich lerne Deutsch.'
    assert validate_result(result,expected)['blocks'][0]['text']==result['blocks'][0]['text']


def test_padded_rights_claim_cannot_exceed_database_limit():
    with pytest.raises(ValueError):
        declaration({'byte_count':10,'media_type':'application/pdf','rights_claim':' '+('x'*1999)+' '})
