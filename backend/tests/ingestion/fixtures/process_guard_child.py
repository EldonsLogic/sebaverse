"""Authored child for watchdog tests. It uses only local standard-library I/O."""

import fcntl
import hashlib
import json
import os
import signal
import sys
import time
from pathlib import Path


PRIVATE_MARKER = b"synthetic-private-child-marker"
CHUNK = b"x" * 65536


def hold_pipes_after_leader_exit():
    pid = os.fork()
    if pid == 0:
        signal.alarm(5)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        with Path("descendant.lock").open("wb") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            Path("ready").write_text(str(os.getpgrp()))
            time.sleep(4)
        os._exit(0)

    # Let the parent test observe the locked handle before reaping the leader.
    while not Path("observed").exists():
        time.sleep(0.01)
    sys.stdout.buffer.write(b"leader-output")


def main():
    # The fixture always exits even if the guard under test fails to clean it up.
    signal.alarm(5)
    mode = sys.stdin.buffer.readline().strip()
    if mode == b"inspect":
        cwd = Path.cwd()
        details = {
            "cwd": str(cwd),
            "cwd_permissions": cwd.stat().st_mode & 0o777,
            "cwd_files": sorted(os.listdir()),
            "env_keys": sorted(os.environ),
            "isolated": sys.flags.isolated,
            "session_leader": os.getsid(0) == os.getpid(),
        }
        sys.stdout.buffer.write(json.dumps(details).encode())
    elif mode == b"duplex":
        # Fill both output pipes before consuming the rest of a large input.
        sys.stdout.buffer.write(CHUNK * 4)
        sys.stderr.buffer.write(CHUNK[:60000])
        sys.stdout.buffer.write(hashlib.sha256(sys.stdin.buffer.read()).digest())
    elif mode in (b"flood_stdout", b"flood_stderr"):
        stream = sys.stdout.buffer if mode == b"flood_stdout" else sys.stderr.buffer
        stream.write(PRIVATE_MARKER * 4096)
        time.sleep(4)
    elif mode == b"sleep":
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        Path("ready").touch()
        sys.stdout.buffer.write(PRIVATE_MARKER)
        sys.stderr.buffer.write(PRIVATE_MARKER)
        time.sleep(4)
    elif mode == b"descendant":
        hold_pipes_after_leader_exit()
    elif mode == b"fail":
        sys.stdout.buffer.write(PRIVATE_MARKER)
        sys.stderr.buffer.write(PRIVATE_MARKER)
        raise SystemExit(17)
    elif mode == b"echo":
        sys.stdout.buffer.write(sys.stdin.buffer.read())
    elif not mode:
        sys.stdout.buffer.write(b"empty")
    else:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
