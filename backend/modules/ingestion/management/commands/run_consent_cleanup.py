"""Run a bounded pass over committed consent cleanup intents on the local fixture store."""

from contextlib import contextmanager
import os
from pathlib import Path
import stat

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from modules.ingestion.cleanup import run_batch
from modules.ingestion.storage import PrivateObjects, _NAMESPACE


MAX_BATCHES = 4
TARGETS_PER_BATCH = 25


class _BoundCleanupStore:
    """Use the configured adapter's receipt against the already checked directory."""

    def __init__(self, store, directory):
        self.store = store
        self.directory = directory

    def purge_confirmed(self, object_id):
        return self.store._purge_confirmed(object_id, self.directory)


def _configured_store():
    if (getattr(settings, 'CONSENT_CLEANUP_ENABLED', False) is not True
            or getattr(settings, 'LOCAL_MODE', False) is not True):
        raise CommandError('Consent cleanup is disabled.')

    database = settings.DATABASES.get('default', {})
    if (set(settings.DATABASES) != {'default'} or settings.DATABASE_ROUTERS
            or database.get('ENGINE') != 'django.db.backends.postgresql'
            or database.get('HOST') not in ('localhost', '127.0.0.1', '::1')):
        raise CommandError('Consent cleanup requires the configured local fixture database.')

    store = getattr(settings, 'CONSENT_CLEANUP_STORE', None)
    if type(store) is not PrivateObjects or getattr(store, 'writer_recovery', None) is not False:
        raise CommandError('Consent cleanup requires the configured local fixture store.')
    return store


@contextmanager
def _existing_private_root(root):
    if (not isinstance(root, Path) or root.anchor != '/' or root == Path('/')
            or '..' in root.parts):
        raise ValueError('Invalid consent cleanup store root')
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    directory = os.open(root.anchor, flags)
    try:
        for part in root.parts[1:]:
            child = os.open(part, flags, dir_fd=directory)
            os.close(directory)
            directory = child
        info = os.fstat(directory)
        named = root.lstat()
        if ((info.st_dev, info.st_ino) != (named.st_dev, named.st_ino)
                or info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o700):
            raise ValueError('Invalid consent cleanup store root')
        try:
            os.stat(_NAMESPACE, dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise ValueError('Protected writer store not supported by consent cleanup command')
        yield directory
    finally:
        os.close(directory)


class Command(BaseCommand):
    help = 'Run up to four pending consent cleanup batches for the configured local synthetic store.'
    requires_system_checks = []
    requires_migrations_checks = False

    def create_parser(self, prog_name, subcommand, **kwargs):
        parser = super().create_parser(prog_name, subcommand, **kwargs)
        parser_error = parser.error

        def report_invalid_arguments(_message):
            parser_error('Invalid consent cleanup arguments.')

        parser.error = report_invalid_arguments
        return parser

    def handle(self, *args, **options):
        store = _configured_store()
        try:
            with _existing_private_root(store.root) as directory:
                return self._run(_BoundCleanupStore(store, directory))
        except (OSError, ValueError, AttributeError):
            raise CommandError('Consent cleanup requires an existing private fixture store.') from None

    def _run(self, store):
        counts = {'complete': 0, 'pending': 0, 'blocked': 0}
        stop = 'limit'
        try:
            for _ in range(MAX_BATCHES):
                result = run_batch(store, limit=TARGETS_PER_BATCH)
                if result is None:
                    stop = 'no_result'
                    break
                counts[result.status] += 1
        except Exception:
            raise CommandError('Consent cleanup stopped. Earlier batches may already have committed.') from None

        return (f"Cleanup batches={sum(counts.values())} complete={counts['complete']} "
                f"pending={counts['pending']} blocked={counts['blocked']} stop={stop}")
