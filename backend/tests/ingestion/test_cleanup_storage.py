import errno
import os
import stat
from uuid import uuid4

import pytest

from modules.ingestion.storage import PrivateObjects


def test_confirmed_purge_unlinks_both_entries_before_sync_and_syncs_on_replay(tmp_path, monkeypatch):
    store = PrivateObjects(tmp_path / 'private')
    key = str(uuid4())
    source = store.path(key)
    manifest = store.path(key, 'manifest')
    source.write_bytes(b'authored source')
    manifest.symlink_to(tmp_path / 'missing-target')
    sync_inode = []
    fsync = os.fsync

    def observe_sync(fd):
        directory = os.fstat(fd)
        assert stat.S_ISDIR(directory.st_mode)
        assert not os.path.lexists(source) and not os.path.lexists(manifest)
        sync_inode.append((directory.st_dev, directory.st_ino))
        fsync(fd)

    monkeypatch.setattr(os, 'fsync', observe_sync)
    store.purge_confirmed(key)
    store.purge_confirmed(key)

    root = store.root.stat()
    assert sync_inode == [(root.st_dev, root.st_ino)] * 2


def test_directory_sync_error_propagates_and_releases_the_directory_fd(tmp_path, monkeypatch):
    store = PrivateObjects(tmp_path / 'private')
    key = str(uuid4())
    store.path(key).write_bytes(b'authored source')
    store.path(key, 'manifest').write_bytes(b'authored manifest')
    directory_fds = []

    def fail_sync(fd):
        assert stat.S_ISDIR(os.fstat(fd).st_mode)
        directory_fds.append(fd)
        raise OSError(errno.EIO, 'fixture directory sync failure')

    with monkeypatch.context() as fault:
        fault.setattr(os, 'fsync', fail_sync)
        with pytest.raises(OSError, match='fixture directory sync failure'):
            store.purge_confirmed(key)
        assert len(directory_fds) == 1
        with pytest.raises(OSError) as closed:
            os.fstat(directory_fds[0])
        assert closed.value.errno == errno.EBADF

    store.purge_confirmed(key)
    assert not os.path.lexists(store.path(key))
    assert not os.path.lexists(store.path(key, 'manifest'))


def test_confirmed_purge_checks_entry_absence_even_after_directory_sync(tmp_path, monkeypatch):
    store = PrivateObjects(tmp_path / 'private')
    key = str(uuid4())
    source = store.path(key)
    source.write_bytes(b'authored source')
    fsync = os.fsync

    def restore_entry(fd):
        source.symlink_to(tmp_path / 'missing-target')
        fsync(fd)

    with monkeypatch.context() as fault:
        fault.setattr(os, 'fsync', restore_entry)
        with pytest.raises(OSError):
            store.purge_confirmed(key)
        assert source.is_symlink()

    store.purge_confirmed(key)
    assert not os.path.lexists(source)
