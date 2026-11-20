"""Bounded process transport for reviewed POSIX worker programs.

The controller owns and reaps its direct child. Callers must not install an
automatic or competing child reaper. A process group cannot contain a worker
that creates its own session. A qualified composition still needs filesystem,
network, CPU, memory and process isolation and an immutable program location.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import select
import selectors
import signal
import stat
import subprocess
import sys
import tempfile
import time
from contextlib import closing, contextmanager, suppress
from dataclasses import dataclass
from pathlib import Path

_MIB = 1024 * 1024
_MAX_SCRIPT_BYTES = 256 * 1024
_IO_CHUNK = 16 * 1024
_POLL_SECONDS = 0.025
_SHA256 = re.compile(r"[0-9a-f]{64}")


class WorkerError(ValueError):
    """A bounded worker failure without program, payload or stderr details."""


@dataclass(frozen=True)
class WorkerProgram:
    executable: str | Path
    script: str | Path
    script_sha256: str


@dataclass(frozen=True)
class WorkerLimits:
    timeout_seconds: float = 10
    input_bytes: int = 65536
    output_bytes: int = _MIB
    error_bytes: int = 16384


@dataclass(frozen=True)
class WorkerResult:
    output: bytes
    stderr_bytes: int
    elapsed_seconds: float


def _validate_limits(limits):
    if type(limits) is not WorkerLimits:
        raise WorkerError("invalid_limits")
    if type(limits.timeout_seconds) not in (int, float) or not 0 < limits.timeout_seconds <= 30:
        raise WorkerError("invalid_limits")
    for count, maximum in (
        (limits.input_bytes, _MIB), (limits.output_bytes, _MIB), (limits.error_bytes, 65536),
    ):
        if type(count) is not int or not 0 <= count <= maximum:
            raise WorkerError("invalid_limits")


def _verified_paths(program):
    if type(program) is not WorkerProgram:
        raise WorkerError("invalid_program")
    digest = program.script_sha256
    if type(digest) is not str or not _SHA256.fullmatch(digest):
        raise WorkerError("invalid_program")

    def open_script(path, flags):
        return os.open(path, flags | os.O_NOFOLLOW | os.O_NONBLOCK)

    try:
        executable, script = Path(program.executable), Path(program.script)
        if not executable.is_absolute() or not script.is_absolute():
            raise WorkerError("invalid_program")
        executable = executable.resolve(strict=True)
        if not executable.is_file() or not os.access(executable, os.X_OK):
            raise WorkerError("invalid_program")
        with open(script, "rb", opener=open_script) as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > _MAX_SCRIPT_BYTES:
                raise WorkerError("invalid_program")
            source = stream.read(_MAX_SCRIPT_BYTES + 1)
    except (OSError, RuntimeError, TypeError, ValueError):
        pass
    else:
        if len(source) <= _MAX_SCRIPT_BYTES and hmac.compare_digest(hashlib.sha256(source).hexdigest(), digest):
            return executable, script
    raise WorkerError("invalid_program")


def _checkpoint(deadline, cancelled):
    stopped = False
    if cancelled is not None:
        try:
            stopped = bool(cancelled())
        except BaseException:
            # The predicate is a callback boundary. Even a request to exit
            # there must stop the child without exporting the callback's text.
            stopped = None
    if stopped is None:
        raise WorkerError("controller_failed")
    if stopped:
        raise WorkerError("worker_cancelled")
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise WorkerError("worker_timeout")
    return min(remaining, _POLL_SECONDS)


@contextmanager
def _observe_exit(pid):
    # Observing exit without reaping keeps this PID reserved until group cleanup.
    if hasattr(os, "waitid"):
        yield lambda: os.waitid(os.P_PID, pid, os.WEXITED | os.WNOHANG | os.WNOWAIT) is not None
        return

    with closing(select.kqueue()) as events:
        watch = select.kevent(
            pid, filter=select.KQ_FILTER_PROC, flags=select.KQ_EV_ADD | select.KQ_EV_ONESHOT,
            fflags=select.KQ_NOTE_EXIT,
        )
        try:
            events.control([watch], 0, 0)
        except ProcessLookupError:
            # A fast child can exit before its watch is registered.
            yield lambda: True
        else:
            yield lambda: bool(events.control(None, 1, 0))


def _kill_group(pid):
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except PermissionError:
        # Darwin can report EPERM on a group with only an unreaped zombie.
        if sys.platform == "darwin":
            try:
                os.getpgid(pid)
            except ProcessLookupError:
                return
        raise


def _reap_and_close(process):
    try:
        if process.returncode is None:
            try:
                _kill_group(process.pid)
            except OSError:
                process.kill()
                raise
            finally:
                process.wait()
    finally:
        for pipe in (process.stdin, process.stdout, process.stderr):
            with suppress(OSError):
                pipe.close()


def _transport(process, payload, limits, deadline, cancelled):
    output = bytearray()
    stderr_bytes = 0
    unsent = memoryview(payload)
    with selectors.DefaultSelector() as io, _observe_exit(process.pid) as exited:
        for pipe in (process.stdout, process.stderr):
            os.set_blocking(pipe.fileno(), False)
            io.register(pipe, selectors.EVENT_READ)
        if unsent:
            os.set_blocking(process.stdin.fileno(), False)
            io.register(process.stdin, selectors.EVENT_WRITE)
        else:
            process.stdin.close()

        while io.get_map() or process.returncode is None:
            delay = _checkpoint(deadline, cancelled)
            if process.returncode is None and exited():
                _kill_group(process.pid)
                if process.wait() != 0:
                    raise WorkerError("worker_failed")
                if unsent:
                    raise WorkerError("input_incomplete")
            if not io.get_map():
                if process.returncode is None:
                    time.sleep(delay)
                continue

            for key, _ in io.select(delay):
                pipe = key.fileobj
                if pipe is process.stdin:
                    try:
                        unsent = unsent[os.write(key.fd, unsent[:_IO_CHUNK]):]
                    except BlockingIOError:
                        continue
                    except BrokenPipeError:
                        pass
                    else:
                        if unsent:
                            continue
                    io.unregister(pipe)
                    pipe.close()
                    continue

                is_stdout = pipe is process.stdout
                available = limits.output_bytes - len(output) if is_stdout else limits.error_bytes - stderr_bytes
                try:
                    chunk = os.read(key.fd, min(_IO_CHUNK, available + 1))
                except BlockingIOError:
                    continue
                if not chunk:
                    io.unregister(pipe)
                    pipe.close()
                elif len(chunk) > available:
                    raise WorkerError("output_limit" if is_stdout else "error_limit")
                elif is_stdout:
                    output.extend(chunk)
                else:
                    stderr_bytes += len(chunk)
    return bytes(output), stderr_bytes


def run_worker(payload, *, program=None, limits=None, cancelled=None):
    """Run a fixed reviewed script, returning only a complete bounded pipe result.

    Cancellation predicates are trusted and must return promptly. The watchdog
    cannot interrupt a blocked spawn syscall or make a killable process from a
    task blocked in the kernel. Program bytes are checked before spawn. A
    qualified image must prevent filesystem substitution between check and use.
    """
    started = time.monotonic()
    if program is None:
        raise WorkerError("worker_unavailable")
    if os.name != "posix" or not (hasattr(os, "waitid") or hasattr(select, "KQ_NOTE_EXIT")):
        raise WorkerError("unsupported_platform")
    if signal.getsignal(signal.SIGCHLD) == signal.SIG_IGN:
        raise WorkerError("unsupported_child_reaping")
    limits = WorkerLimits() if limits is None else limits
    _validate_limits(limits)
    if type(payload) is not bytes or len(payload) > limits.input_bytes:
        raise WorkerError("invalid_input")
    if cancelled is not None and not callable(cancelled):
        raise WorkerError("controller_failed")

    deadline = started + limits.timeout_seconds
    executable, script = _verified_paths(program)
    try:
        with tempfile.TemporaryDirectory(prefix="sebaverse-worker-") as cwd:
            _checkpoint(deadline, cancelled)
            process = None
            try:
                process = subprocess.Popen(
                    [str(executable), "-I", "-u", str(script)], stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0, shell=False,
                    close_fds=True, start_new_session=True, cwd=cwd, env={"LC_ALL": "C"},
                )
                output, stderr_bytes = _transport(process, payload, limits, deadline, cancelled)
            finally:
                if process is not None:
                    _reap_and_close(process)
        _checkpoint(deadline, cancelled)
        return WorkerResult(output, stderr_bytes, time.monotonic() - started)
    except WorkerError:
        raise
    except Exception:
        pass
    raise WorkerError("controller_failed")
