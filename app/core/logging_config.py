"""Core application helpers for logging config."""

import logging
import logging.handlers
import sys
import os
from pathlib import Path

DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
APP_LOG_DIR = Path(os.getenv("APP_LOG_DIR", str(DEFAULT_LOG_DIR)))

try:
    APP_LOG_DIR.mkdir(parents=True, exist_ok=True)
except OSError as e:
    print(
        f"CRITICAL WARNING: Could not create log directory {APP_LOG_DIR.resolve()}. "
        f"File logging WILL FAIL. Error: {e}",
        file=sys.stderr,
        flush=True,
    )


def setup_logging(
    log_level_console_str: str = "DEBUG",
    log_level_file_str: str = "DEBUG",
    clear_existing_handlers: bool = True,
    log_filename_base: str = "app_backend",
):
    """Configure root logger with a console handler and a rotating file handler.

    Each process (backend, scheduler) should pass its own ``log_filename_base``
    so logs are written to separate files (e.g. ``app_backend.log``,
    ``app_scheduler.log``).
    """
    log_levels = {
        "CRITICAL": logging.CRITICAL, "ERROR": logging.ERROR, "WARNING": logging.WARNING,
        "INFO": logging.INFO, "DEBUG": logging.DEBUG, "NOTSET": logging.NOTSET,
    }

    console_level = log_levels.get(log_level_console_str.upper(), logging.INFO)
    file_level = log_levels.get(log_level_file_str.upper(), logging.DEBUG)

    log_format_str = (
        "%(asctime)s - %(levelname)-8s - %(name)-25s - "
        "[%(module)s.%(funcName)s:%(lineno)d] - "
        "RID:%(request_id)s - UID:%(user_identifier)s - %(message)s"
    )
    formatter = logging.Formatter(log_format_str, datefmt="%Y-%m-%d %H:%M:%S")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if clear_existing_handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()

    context_filter = None
    try:
        from app.core.context import request_id_var, user_identifier_var

        class ContextualLogFilter(logging.Filter):
            def filter(self, record: logging.LogRecord) -> bool:
                record.request_id = request_id_var.get() if request_id_var.get() is not None else "-"
                record.user_identifier = user_identifier_var.get()
                return True

        context_filter = ContextualLogFilter()
    except ImportError:
        pass

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    if context_filter:
        console_handler.addFilter(context_filter)
    root_logger.addHandler(console_handler)

    # Rotating file handler — one file per process
    log_file_path = APP_LOG_DIR / f"{log_filename_base}.log"
    try:
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_file_path, when="H", interval=1, backupCount=24 * 3,
            encoding="utf-8", delay=False, utc=True,
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        if context_filter:
            file_handler.addFilter(context_filter)
        root_logger.addHandler(file_handler)
        log_file_path_str = str(log_file_path.resolve())
    except Exception as e:
        log_file_path_str = f"DISABLED ({e})"

    # Quiet noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("semantic_kernel").setLevel(logging.INFO)
    logging.getLogger("apscheduler").setLevel(logging.INFO)

    root_logger.info(
        "Logging configured — process=%s console=%s file=%s log=%s",
        log_filename_base,
        logging.getLevelName(console_level),
        logging.getLevelName(file_level),
        log_file_path_str,
    )
