import logging


class MetadataOnlyFormatter(logging.Formatter):
    """Exclude message, request path/body and exception text from default logs."""

    def format(self, record):
        return f"{record.levelname} {record.name}"
