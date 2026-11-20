"""Real subprocess tests using one authored Python fixture and synthetic bytes."""

import hashlib
import json
import os
import signal
import subprocess
import sys
import time
import traceback
from dataclasses import replace
from pathlib import Path

import pytest

from workers.parser import process_guard
from workers.parser.process_guard import WorkerError, WorkerLimits, WorkerProgram, run_worker


pytestmark = pytest.mark.skipif(os.name != "posix", reason="Authored guard fixtures require POSIX")
SCRIPT = Path(__file__).parent / "fixtures" / "process_guard_child.py"
PRIVATE_MARKER = "synthetic-private-child-marker"
REAL_POPEN = subprocess.Popen


class FixtureWallTimeout(BaseException):
    """Keep a broken watchdog from hanging the local test runner."""


@pytest.fixture
def authored_program():
    script = SCRIPT.resolve()
    return WorkerProgram(
        executable=sys.executable,
        script=str(script),
        script_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),
    )


@pytest.fixture
def spawned(monkeypatch):
    records = []

    def record(argv, **options):
        child = REAL_POPEN(argv, **options)
        records.append((child, argv, options))
        return child

    monkeypatch.setattr(process_guard.subprocess, "Popen", record)
    previous_handler = signal.getsignal(signal.SIGALRM)

    def expire(signum, frame):
        raise FixtureWallTimeout("Authored process fixture exceeded its test budget")

    signal.signal(signal.SIGALRM, expire)
    signal.setitimer(signal.ITIMER_REAL, 8)
    try:
        yield records
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
        for child, _, options in records:
            if child.returncode is None:
                try:
                    if options.get("start_new_session") and os.getpgid(child.pid) == child.pid:
                        os.killpg(child.pid, signal.SIGKILL)
                    else:
                        child.kill()
                except ProcessLookupError:
                    pass
                child.wait(timeout=2)
            for stream in (child.stdin, child.stdout, child.stderr):
                if stream is not None:
                    stream.close()


def reject_spawning(monkeypatch):
    def unexpected_spawn(*args, **kwargs):
        pytest.fail("An invalid configuration reached subprocess creation")

    monkeypatch.setattr(process_guard.subprocess, "Popen", unexpected_spawn)


def assert_cleaned(records):
    assert len(records) == 1
    child, _, options = records[0]
    assert child.returncode is not None
    with pytest.raises(ChildProcessError):
        os.waitpid(child.pid, os.WNOHANG)
    assert all(stream is not None and stream.closed for stream in (child.stdin, child.stdout, child.stderr))
    assert not Path(options["cwd"]).exists()


def assert_private_failure(error):
    reason = str(error)
    assert 0 < len(reason) <= 120
    assert PRIVATE_MARKER not in reason
    assert PRIVATE_MARKER not in "".join(traceback.format_exception(error))


def test_factory_unavailable_and_invalid_payload_fail_before_spawn(monkeypatch, authored_program):
    reject_spawning(monkeypatch)
    with pytest.raises(WorkerError):
        run_worker(b"")
    for invalid in ("echo", bytearray(b"echo"), b"x" * 65537):
        with pytest.raises(WorkerError):
            run_worker(invalid, program=authored_program)


@pytest.mark.parametrize("changes", [
    {"executable": "python"},
    {"script": "test.py"},
    {"script_sha256": "0" * 64},
    {"script_sha256": "Z" * 64},
])
def test_invalid_reviewed_program_is_never_spawned(monkeypatch, authored_program, changes):
    reject_spawning(monkeypatch)
    with pytest.raises(WorkerError):
        run_worker(b"", program=replace(authored_program, **changes))


def test_program_rejects_symlink_nonexecutable_and_oversized_script(
    monkeypatch, authored_program, tmp_path,
):
    reject_spawning(monkeypatch)
    linked = tmp_path / "link.py"
    linked.symlink_to(authored_program.script)
    not_executable = tmp_path / "interpreter"
    not_executable.write_bytes(b"# authored fixture without execute permission\n")
    not_executable.chmod(0o600)
    oversized = tmp_path / "oversized.py"
    oversized.write_bytes(b"#" + b"x" * (256 * 1024))
    for program in (
        replace(authored_program, script=str(linked)),
        replace(authored_program, executable=str(not_executable)),
        replace(
            authored_program, script=str(oversized),
            script_sha256=hashlib.sha256(oversized.read_bytes()).hexdigest(),
        ),
    ):
        with pytest.raises(WorkerError):
            run_worker(b"", program=program)


@pytest.mark.parametrize("changes", [
    {"timeout_seconds": True},
    {"timeout_seconds": 0},
    {"timeout_seconds": float("inf")},
    {"timeout_seconds": float("nan")},
    {"timeout_seconds": 31},
    {"input_bytes": -1},
    {"input_bytes": 1048577},
    {"output_bytes": True},
    {"output_bytes": 1.25},
    {"output_bytes": 1048577},
    {"error_bytes": 65537},
])
def test_invalid_limits_are_rejected_before_spawn(monkeypatch, authored_program, changes):
    reject_spawning(monkeypatch)
    with pytest.raises(WorkerError):
        run_worker(b"", program=authored_program, limits=replace(WorkerLimits(), **changes))


def test_success_uses_fixed_spawn_contract_and_private_fresh_cwd(monkeypatch, authored_program, spawned):
    inherited = {
        "PGPASSWORD", "POSTGRES_PASSWORD", "SEBAVERSE_TOKEN", "PYTHONPATH", "PYTHONSTARTUP",
        "LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "GUARD_FIXTURE_PRIVATE",
    }
    for name in inherited:
        monkeypatch.setenv(name, "/nonexistent-authored-guard-sentinel")
    result = run_worker(b"inspect\n", program=authored_program)
    details = json.loads(result.output)
    assert details["cwd_permissions"] == 0o700
    assert details["cwd_files"] == []
    assert inherited.isdisjoint(details["env_keys"])
    assert details["isolated"] == 1
    assert details["session_leader"]
    assert result.stderr_bytes == 0
    assert 0 <= result.elapsed_seconds < 2
    _, argv, options = spawned[0]
    assert list(argv) == [str(Path(authored_program.executable).resolve()), "-I", "-u", authored_program.script]
    assert options.get("shell", False) is False
    assert options["close_fds"] is True
    assert options["start_new_session"] is True
    assert Path(details["cwd"]).resolve() == Path(options["cwd"]).resolve()
    assert_cleaned(spawned)


@pytest.mark.parametrize("payload, expected", [
    (b"", b"empty"), (b"echo\n\x00\xffpayload", b"\x00\xffpayload"),
])
def test_empty_and_binary_inputs_are_delivered(authored_program, spawned, payload, expected):
    result = run_worker(payload, program=authored_program, limits=WorkerLimits(output_bytes=len(expected)))
    assert result.output == expected
    assert result.stderr_bytes == 0
    assert_cleaned(spawned)


def test_large_input_and_output_before_input_are_drained_concurrently(authored_program, spawned):
    body = b"\x00\xffdata" * 84000
    result = run_worker(
        b"duplex\n" + body,
        program=authored_program,
        limits=WorkerLimits(timeout_seconds=3, input_bytes=524288, error_bytes=65536),
    )
    assert result.output == b"x" * 262144 + hashlib.sha256(body).digest()
    assert result.stderr_bytes == 60000
    assert_cleaned(spawned)


@pytest.mark.parametrize("mode", [b"flood_stdout", b"flood_stderr"])
def test_flood_limits_abort_before_deadline_and_discard_partial_output(authored_program, spawned, mode):
    start = time.monotonic()
    with pytest.raises(WorkerError) as caught:
        run_worker(
            mode + b"\n", program=authored_program,
            limits=WorkerLimits(timeout_seconds=3, output_bytes=2048, error_bytes=2048),
        )
    assert time.monotonic() - start < 2
    assert_private_failure(caught.value)
    assert_cleaned(spawned)


@pytest.mark.parametrize("stop, predicate_error", [
    pytest.param("deadline", None, id="deadline"),
    pytest.param("cancellation", None, id="cancellation"),
    pytest.param("controller-error", RuntimeError, id="runtime-error"),
    pytest.param("controller-error", SystemExit, id="system-exit"),
    pytest.param("controller-error", KeyboardInterrupt, id="keyboard-interrupt"),
])
def test_sleeping_child_is_reaped_even_when_it_ignores_termination(
    authored_program, spawned, stop, predicate_error,
):
    ready = False

    def observe():
        nonlocal ready
        if not spawned or not (Path(spawned[0][2]["cwd"]) / "ready").is_file():
            return False
        ready = True
        if predicate_error is not None:
            raise predicate_error(PRIVATE_MARKER)
        return stop == "cancellation"

    start = time.monotonic()
    with pytest.raises(WorkerError) as caught:
        run_worker(
            b"sleep\n", program=authored_program,
            limits=WorkerLimits(timeout_seconds=0.8 if stop == "deadline" else 3),
            cancelled=observe,
        )
    elapsed = time.monotonic() - start
    assert ready
    if stop == "deadline":
        assert elapsed >= 0.7
    if predicate_error is not None:
        assert str(caught.value) == "controller_failed"
    assert elapsed < 2
    assert_private_failure(caught.value)
    assert spawned[0][0].returncode == -signal.SIGKILL
    assert_cleaned(spawned)


def test_abnormal_exit_does_not_expose_stdout_or_stderr(authored_program, spawned):
    with pytest.raises(WorkerError) as caught:
        run_worker(b"fail\n", program=authored_program)
    assert_private_failure(caught.value)
    assert spawned[0][0].returncode == 17
    assert_cleaned(spawned)


def test_descendant_holding_pipes_after_leader_exit_is_cleaned(authored_program, spawned):
    import fcntl

    lock = None
    owned_group = None

    def observe():
        nonlocal lock, owned_group
        if spawned and lock is None:
            leader, _, options = spawned[0]
            cwd = Path(options["cwd"])
            ready = cwd / "ready"
            if ready.is_file() and ready.read_text() == str(leader.pid):
                lock = (cwd / "descendant.lock").open("rb")
                with pytest.raises(BlockingIOError):
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                owned_group = leader.pid
                (cwd / "observed").touch()
        return False

    start = time.monotonic()
    try:
        try:
            result = run_worker(
                b"descendant\n", program=authored_program,
                limits=WorkerLimits(timeout_seconds=1.25), cancelled=observe,
            )
        except WorkerError as error:
            assert_private_failure(error)
        else:
            assert result.output == b"leader-output"
        assert time.monotonic() - start < 2.5
        assert lock is not None
        assert spawned[0][0].returncode == 0
        assert_cleaned(spawned)
        deadline = time.monotonic() + 0.5
        while True:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                owned_group = None
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    pytest.fail("An authored descendant retained the worker lock after guard return")
                time.sleep(0.01)
    finally:
        if lock is not None:
            if owned_group is not None:
                # The authored descendant supplied this group and held the lock.
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    try:
                        os.killpg(owned_group, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
            lock.close()


def test_guard_does_not_signal_an_unrelated_owned_process(authored_program, spawned, tmp_path):
    unrelated = REAL_POPEN(
        [sys.executable, "-I", "-u", authored_program.script],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        cwd=tmp_path, env={}, start_new_session=True,
    )
    try:
        unrelated.stdin.write(b"sleep\n")
        unrelated.stdin.close()
        deadline = time.monotonic() + 1
        while not (tmp_path / "ready").exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert (tmp_path / "ready").is_file()
        with pytest.raises(WorkerError):
            run_worker(
                b"sleep\n", program=authored_program, limits=WorkerLimits(timeout_seconds=0.25),
            )
        assert_cleaned(spawned)
        assert unrelated.poll() is None
    finally:
        if unrelated.poll() is None:
            unrelated.kill()
        unrelated.wait(timeout=2)
