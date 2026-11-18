import hashlib,os
from uuid import uuid4
import pytest
from modules.ingestion.storage import PrivateObjects
from modules.ingestion.contracts import sign_manifest,verify_manifest


def test_private_objects_have_no_caller_filename_and_reject_paths(tmp_path):
    store=PrivateObjects(tmp_path/'private')
    with pytest.raises(ValueError):store.path('../../secret')
    key=str(uuid4());r=store.put(key,[b'%PDF-fixture'],12)
    assert r['sha256']==hashlib.sha256(b'%PDF-fixture').hexdigest()
    assert store.path(key).stat().st_mode&0o777==0o600
    assert store.root.stat().st_mode&0o777==0o700
    assert store.read(key)==b'%PDF-fixture'
    store.purge(key);store.purge(key)
    assert not store.path(key).exists()


@pytest.mark.parametrize('chunks,expected', [([b'ab'],1),([b'ab'],3),([b'x'*65537],65537),(['not bytes'],9)])
def test_failed_stream_does_not_leave_an_object(tmp_path,chunks,expected):
    store=PrivateObjects(tmp_path/'private');key=str(uuid4())
    with pytest.raises(ValueError):store.put(key,chunks,expected)
    assert not store.path(key).exists()


def test_symlink_read_never_follows_another_private_file(tmp_path):
    store=PrivateObjects(tmp_path/'private');key=str(uuid4())
    victim=tmp_path/'victim';victim.write_bytes(b'private marker')
    store.path(key).symlink_to(victim)
    with pytest.raises(OSError):store.read(key)
    store.purge(key)
    assert victim.read_bytes()==b'private marker'


def test_signed_manifest_is_scoped_expiring_and_not_a_replay_token():
    key=b'x'*32;expected={'object_id':str(uuid4()),'generation':1,'dispatch_id':str(uuid4())}
    envelope=sign_manifest({**expected,'expires_at':120},key)
    assert verify_manifest(envelope,key,expected,now=100)['generation']==1
    for changed in [{**expected,'generation':2},{**expected,'dispatch_id':str(uuid4())}]:
        with pytest.raises(ValueError):verify_manifest(envelope,key,changed,now=100)
    with pytest.raises(ValueError):verify_manifest(envelope,key,expected,now=120)
    with pytest.raises(ValueError):verify_manifest(envelope,b'y'*32,expected,now=100)


def test_empty_chunk_flood_is_bounded_and_cleaned(tmp_path):
    store=PrivateObjects(tmp_path/'private');key=str(uuid4())
    with pytest.raises(ValueError):store.put(key,(b'' for _ in range(8193)),1)
    assert not store.path(key).exists()


def test_chunk_processing_deadline_is_bounded_and_cleaned(tmp_path,monkeypatch):
    values=iter([0,20])
    monkeypatch.setattr('modules.ingestion.storage.time.monotonic',lambda:next(values))
    store=PrivateObjects(tmp_path/'private');key=str(uuid4())
    with pytest.raises(ValueError):store.put(key,[b'x'],1)
    assert not store.path(key).exists()
