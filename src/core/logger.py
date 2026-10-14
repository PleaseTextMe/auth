import logging
import os
import re
from pathlib import Path

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DEFAULT_HANDLERS = ["console"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": LOG_FORMAT},
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file_warning": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": "logs/warnings.log",
            "formatter": "verbose",
        },
        "all_logs": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/all_logs.log",
            "formatter": "verbose",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
        },
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": LOG_DEFAULT_HANDLERS,
            "level": "INFO",
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "formatter": "verbose",
        "handlers": LOG_DEFAULT_HANDLERS,
    },
}

# Console logging works in fresh checkouts and containers without writable log files.
# Set LOG_DIR explicitly to enable additional file logs.
if os.environ.get("LOG_DIR"):
    log_dir = Path(os.environ["LOG_DIR"])
    log_dir.mkdir(parents=True, exist_ok=True)
    LOGGING["handlers"]["all_logs"]["filename"] = str(log_dir / "all_logs.log")
    LOGGING["handlers"]["file_warning"]["filename"] = str(log_dir / "warnings.log")
    LOG_DEFAULT_HANDLERS.extend(["all_logs", "file_warning"])
else:
    del LOGGING["handlers"]["all_logs"]
    del LOGGING["handlers"]["file_warning"]


class RedactTokens(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        def redact(value):
            if isinstance(value, str):
                return re.sub(r"([?&]token=)[^&\s\"']+", r"\1[REDACTED]", value)
            return value
        record.msg = redact(record.msg)
        if isinstance(record.args, tuple):
            record.args = tuple(redact(value) for value in record.args)
        elif isinstance(record.args, dict):
            record.args = {key: redact(value) for key, value in record.args.items()}
        return True


LOGGING["filters"] = {"redact_tokens": {"()": RedactTokens}}
for handler in LOGGING["handlers"].values():
    handler["filters"] = ["redact_tokens"]
