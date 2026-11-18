"""Local private-object PoC adapter. No client filename or public serving path."""
from contextlib import contextmanager
from pathlib import Path
import hashlib,os,time
from uuid import UUID
from .contracts import MAX_BYTES


class PrivateObjects:
    def __init__(self,root):
        self.root=Path(root)
        if self.root.is_symlink():raise ValueError('Private root cannot be a symlink')
        self.root.mkdir(mode=0o700,parents=True,exist_ok=True)
        self.root=self.root.resolve()
        self.root.chmod(0o700)

    def path(self,object_id,suffix='blob'):
        if str(UUID(str(object_id)))!=str(object_id) or suffix not in ['blob','manifest']:raise ValueError('Server object identity required')
        return self.root/(str(object_id)+'.'+suffix)

    def put(self,object_id,chunks,expected_bytes):
        target=self.path(object_id)
        fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        count=0;digest=hashlib.sha256();prefix=b'';started=time.monotonic();parts=0
        try:
            with os.fdopen(fd,'wb') as output:
                for chunk in chunks:
                    parts+=1
                    if parts>8192 or time.monotonic()-started>10:raise ValueError('Upload processing deadline/chunk bound exceeded')
                    if not isinstance(chunk,bytes) or len(chunk)>65536:raise ValueError('Invalid bounded upload chunk')
                    count+=len(chunk)
                    if count>MAX_BYTES or count>expected_bytes:raise ValueError('Upload exceeds declared/absolute bound')
                    if len(prefix)<16:prefix=(prefix+chunk)[:16]
                    digest.update(chunk);output.write(chunk)
                output.flush();os.fsync(output.fileno())
            if count!=expected_bytes:raise ValueError('Upload byte count differs')
            return {'byte_count':count,'sha256':digest.hexdigest(),'prefix':prefix}
        except BaseException:
            target.unlink(missing_ok=True)
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
        # unlink removes a substituted symlink itself, never follows it.
        for suffix in ['blob','manifest']:self.path(object_id,suffix).unlink(missing_ok=True)
