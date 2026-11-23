"""Hold a real local writer guard in an authored child, without a database."""

import json
import os
from pathlib import Path
import sys
from uuid import uuid4


SOURCE = b'%PDF-' + b'z' * 16_384


def main(root, object_id, stage):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from modules.ingestion.storage import PrivateObjects

    store = PrivateObjects(root, writer_recovery=True)
    with store.source_writer(object_id) as guard:
        binding = guard.binding(1, uuid4())

        def ready():
            print(json.dumps(binding), flush=True)
            sys.stdin.buffer.read(1)

        if stage == 'before-open':
            ready()
        elif stage == 'partial':
            def chunks():
                yield SOURCE
                ready()
                yield b'x'

            guard.put(chunks(), len(SOURCE) + 1)
        elif stage == 'after-close':
            guard.put([SOURCE], len(SOURCE))
            ready()
        elif stage == 'inherited':
            # Leave a duplicate open file description in an authored descendant.
            # Closing the test pipe lets that descendant exit without a signal.
            if os.fork() == 0:
                sys.stdin.buffer.read(1)
                return
            print(json.dumps(binding), flush=True)
        else:
            raise ValueError('Unexpected writer fixture stage')


if __name__ == '__main__':
    main(*sys.argv[1:])
