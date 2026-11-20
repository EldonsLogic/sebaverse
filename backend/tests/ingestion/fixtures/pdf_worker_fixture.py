"""Guarded PDF transport fixture with a fixed fake document factory."""

import signal
import sys
from pathlib import Path


JOB_KEY = b"authored-job-fixture-key".ljust(32, b" ")
SCAN_KEY = b"authored-scan-fixture-key".ljust(32, b" ")
SCANNER_ID = "authored-scanner.v1"
NOW = 100


class AuthoredDocument:
    """A one-page, one-text-handle stand-in for the SDK shape."""

    def __init__(self, data):
        self.text = data[data.rindex(b"\n") + 1:].decode("utf-8", errors="strict")

    def __len__(self):
        return 1

    def get_page(self, index):
        assert index == 0
        return self

    def get_textpage(self):
        return self

    def count_chars(self):
        return len(self.text)

    def get_text_range(self, *, index, count, errors):
        assert errors == "strict"
        return self.text[index:index + count]

    def close(self):
        pass


def main():
    signal.alarm(5)
    # The isolated interpreter omits the checkout from its search path.
    root = Path(__file__).resolve().parents[4]
    sys.path[:0] = [str(root), str(root / "backend")]

    from modules.ingestion.contracts import canonical
    from workers.parser.digital_pdf import ExtractionError, run_job
    from workers.parser.input_transport import InputTransportError, read_request

    try:
        data, expected, job, scan = read_request(sys.stdin.buffer)
        result = run_job(
            data, job, JOB_KEY, expected, scan, SCAN_KEY, SCANNER_ID,
            document_factory=AuthoredDocument, now=NOW,
        )
    except (InputTransportError, ExtractionError):
        return 2

    sys.stdout.buffer.write(canonical(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
