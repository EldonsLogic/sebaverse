"""Local private-object PoC adapter. No client filename or public serving path."""
from contextlib import ExitStack, contextmanager
from pathlib import Path
import hashlib,os,time
import stat
from uuid import UUID, uuid4
from .contracts import MAX_BYTES

try:
    import fcntl
except ImportError:
    fcntl = None


WRITER_PROTOCOL = 'local-flock-v1'
_NAMESPACE = '.source-writer-v1'
_STRIPES = 64


class WriterClosureUnavailable(OSError):
    """The adapter could not prove closure of the named attempt."""


def _identity(info):
    return [info.st_dev, info.st_ino]


def _canonical_uuid(value):
    try:
        return type(value) is str and str(UUID(value)) == value
    except ValueError:
        return False


class _SourceGuard:
    def __init__(self, store, object_id, directory, identities, *, exclusive):
        self._store = store
        self._object_id = object_id
        self._directory = directory
        self._identities = identities
        self._exclusive = exclusive
        self._used = False

    def binding(self, generation, attempt_uuid):
        if self._directory is None or self._exclusive:
            raise RuntimeError('Source writer guard required')
        return {
            'protocol': WRITER_PROTOCOL,
            'object': self._object_id,
            'generation': generation,
            'attempt': str(attempt_uuid),
            **self._identities,
        }

    def put(self, chunks, expected_bytes):
        if self._directory is None or self._exclusive or self._used:
            raise RuntimeError('Unused source writer guard required')
        self._used = True
        return self._store._put_source(self._object_id, chunks, expected_bytes, self._directory)

    def purge_confirmed(self):
        if self._directory is None or not self._exclusive:
            raise RuntimeError('Source closure guard required')
        return self._store._purge_confirmed(self._object_id, self._directory)


class PrivateObjects:
    def __init__(self,root, *, writer_recovery=False):
        self.root=Path(root)
        if self.root.is_symlink():raise ValueError('Private root cannot be a symlink')
        self.root.mkdir(mode=0o700,parents=True,exist_ok=True)
        self.root=self.root.resolve()
        self.root.chmod(0o700)
        self.writer_recovery = writer_recovery is True
        if self.writer_recovery:
            if fcntl is None:
                raise WriterClosureUnavailable('Local writer locks unavailable')
            self._writer_namespace = self._initialize_writer_namespace()

    @contextmanager
    def _directory(self):
        fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            yield fd
        finally:
            os.close(fd)

    @staticmethod
    @contextmanager
    def _lock_file(directory, name, flags):
        fd = os.open(name, flags | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=directory)
        try:
            info = os.fstat(fd)
            if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.geteuid()
                    or info.st_mode & 0o077):
                raise WriterClosureUnavailable('Invalid local writer lock file')
            yield fd
        finally:
            os.close(fd)

    @staticmethod
    def _stripe(index):
        return f'{_NAMESPACE}-{index:02d}'

    def _initialize_writer_namespace(self):
        with self._directory() as directory, self._lock_file(directory, _NAMESPACE, os.O_RDWR | os.O_CREAT) as marker:
            root = os.fstat(directory)
            if root.st_uid != os.geteuid() or root.st_mode & 0o077:
                raise WriterClosureUnavailable('Invalid local writer root')
            fcntl.flock(marker, fcntl.LOCK_EX | fcntl.LOCK_NB)
            value = os.read(marker, 37)
            if value:
                namespace = value.decode('ascii', errors='replace')
                if not _canonical_uuid(namespace):
                    raise WriterClosureUnavailable('Invalid local writer namespace')
                return namespace, _identity(root)
            # An empty marker represents interrupted setup. Publish a new nonce
            # only after the stable lock files exist. Existing nonempty markers
            # never authorize creating a missing stripe.
            for index in range(_STRIPES):
                with self._lock_file(directory, self._stripe(index), os.O_RDWR | os.O_CREAT):
                    pass
            os.fsync(directory)
            value = str(uuid4()).encode('ascii')
            if os.write(marker, value) != len(value):
                raise WriterClosureUnavailable('Could not create local writer namespace')
            os.fsync(marker)
            return value.decode('ascii'), _identity(root)

    @contextmanager
    def _source_guard(self, object_id, *, exclusive, binding=None):
        if not self.writer_recovery or not _canonical_uuid(object_id):
            raise WriterClosureUnavailable('Local writer locks unavailable')
        name = self._stripe(UUID(object_id).int % _STRIPES)
        with self._directory() as directory, self._lock_file(directory, name, os.O_RDWR) as lock:
            mode = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            fcntl.flock(lock, mode | fcntl.LOCK_NB)
            guard_info = _identity(os.fstat(lock))
            if guard_info != _identity(os.stat(name, dir_fd=directory, follow_symlinks=False)):
                raise WriterClosureUnavailable('Local writer lock changed')
            with self._lock_file(directory, _NAMESPACE, os.O_RDONLY) as marker:
                namespace = os.read(marker, 37).decode('ascii', errors='replace')
            root = _identity(os.fstat(directory))
            if (namespace, root) != self._writer_namespace:
                raise WriterClosureUnavailable('Local writer namespace changed')
            identities = {'namespace': namespace, 'root': root, 'stripe': guard_info}
            if binding is not None:
                if (type(binding) is not dict or binding.keys() != {
                        'protocol', 'object', 'generation', 'attempt', *identities}
                        or binding['protocol'] != WRITER_PROTOCOL or binding['object'] != object_id
                        or type(binding['generation']) is not int or binding['generation'] < 1
                        or not _canonical_uuid(binding['attempt'])
                        or any(type(binding[key]) is not list or len(binding[key]) != 2
                               or any(type(part) is not int for part in binding[key])
                               for key in ('root', 'stripe'))
                        or any(binding[key] != value for key, value in identities.items())):
                    raise WriterClosureUnavailable('Local writer binding mismatch')
            guard = _SourceGuard(self, object_id, directory, identities, exclusive=exclusive)
            try:
                yield guard
            finally:
                guard._directory = None

    def source_writer(self, object_id):
        return self._source_guard(object_id, exclusive=False)

    @contextmanager
    def closed_writer(self, object_id, binding):
        # Translate acquisition failures only. Purge errors retain their own outcome.
        if type(binding) is not dict:
            raise WriterClosureUnavailable('Local writer binding mismatch')
        with ExitStack() as stack:
            try:
                guard = stack.enter_context(self._source_guard(object_id, exclusive=True, binding=binding))
            except OSError as error:
                raise WriterClosureUnavailable('Source writer closure unavailable') from error
            yield guard

    def path(self,object_id,suffix='blob'):
        if str(UUID(str(object_id)))!=str(object_id) or suffix not in ['blob','manifest']:raise ValueError('Server object identity required')
        return self.root/(str(object_id)+'.'+suffix)

    def put(self,object_id,chunks,expected_bytes):
        if self.writer_recovery:
            raise RuntimeError('Protected source write requires a writer guard')
        with self._directory() as directory:
            return self._put_source(object_id, chunks, expected_bytes, directory)

    def _put_source(self, object_id, chunks, expected_bytes, directory):
        target=self.path(object_id).name
        count=0;digest=hashlib.sha256();prefix=b'';started=time.monotonic();parts=0
        fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
        try:
            try:
                with os.fdopen(fd, 'wb', closefd=False) as output:
                    for chunk in chunks:
                        parts+=1
                        if parts>8192 or time.monotonic()-started>10:raise ValueError('Upload processing deadline/chunk bound exceeded')
                        if not isinstance(chunk,bytes) or len(chunk)>65536:raise ValueError('Invalid bounded upload chunk')
                        count+=len(chunk)
                        if count>MAX_BYTES or count>expected_bytes:raise ValueError('Upload exceeds declared/absolute bound')
                        if len(prefix)<16:prefix=(prefix+chunk)[:16]
                        digest.update(chunk);output.write(chunk)
                    output.flush();os.fsync(output.fileno())
            finally:
                os.close(fd)
            if count!=expected_bytes:raise ValueError('Upload byte count differs')
            return {'byte_count':count,'sha256':digest.hexdigest(),'prefix':prefix}
        except BaseException:
            try:
                os.unlink(target, dir_fd=directory)
            except FileNotFoundError:
                pass
            raise

    def read(self,object_id,suffix='blob',maximum=MAX_BYTES):
        fd=os.open(self.path(object_id,suffix),os.O_RDONLY|os.O_NOFOLLOW)
        with os.fdopen(fd,'rb') as stream:data=stream.read(maximum+1)
        if len(data)>maximum:raise ValueError('Private object exceeds bound')
        return data

    def put_manifest(self,object_id,data):
        from .contracts import MAX_OUTPUT
        if not isinstance(data,bytes) or len(data)>MAX_OUTPUT:raise ValueError('Invalid manifest bytes')
        target=self.path(object_id,'manifest')
        fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:
            with os.fdopen(fd,'wb') as stream:
                stream.write(data);stream.flush();os.fsync(stream.fileno())
        except BaseException:
            target.unlink(missing_ok=True)
            raise

    def purge(self,object_id):
        if self.writer_recovery:
            self.purge_confirmed(object_id)
            return
        # unlink removes a substituted symlink itself, never follows it.
        for suffix in ['blob','manifest']:self.path(object_id,suffix).unlink(missing_ok=True)

    def purge_confirmed(self,object_id):
        """Unlink both names, request directory durability and confirm absence.

        This is the local adapter's completion receipt, not a hardware or backup
        erasure certification. Unsupported directory sync fails without credit.
        """
        if self.writer_recovery:
            with self._source_guard(str(object_id), exclusive=True) as guard:
                return guard.purge_confirmed()
        with self._directory() as directory:
            return self._purge_confirmed(object_id, directory)

    def _purge_confirmed(self, object_id, directory):
        names=tuple(self.path(object_id,suffix).name for suffix in ('blob','manifest'))
        for name in names:
            try:os.unlink(name,dir_fd=directory)
            except FileNotFoundError:pass
        os.fsync(directory)
        for name in names:
            try:os.stat(name,dir_fd=directory,follow_symlinks=False)
            except FileNotFoundError:continue
            raise OSError('Private object remains after purge')
        return True
