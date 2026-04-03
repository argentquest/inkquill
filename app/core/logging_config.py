"""Core application helpers for logging config."""

# /story_app/app/core/logging_config.py
import logging
import logging.handlers
import sys
import os
from pathlib import Path

DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
APP_LOG_DIR = Path(os.getenv("APP_LOG_DIR", DEFAULT_LOG_DIR))
LOG_FILENAME_BASE = "app_backend"
LOG_FILE_PATH = APP_LOG_DIR / (LOG_FILENAME_BASE + ".log")

print(f"!!!!!!!!!! logging_config.py: LOG_FILE_PATH determined as: {LOG_FILE_PATH.resolve()} !!!!!!!!!!", file=sys.stderr, flush=True)

try:
    APP_LOG_DIR.mkdir(parents=True, exist_ok=True)
    print(f"logging_config.py: Log directory '{APP_LOG_DIR.resolve()}' ensured/created.", file=sys.stderr, flush=True)
except OSError as e:
    print(f"CRITICAL WARNING: Could not create log directory {APP_LOG_DIR.resolve()}. File logging WILL FAIL. Error: {e}", file=sys.stderr, flush=True)

def setup_logging(
    log_level_console_str: str = "DEBUG",
    log_level_file_str: str = "DEBUG",
    clear_existing_handlers: bool = True
):
    """Provide dependency and core support for setup logging."""
    print(f"--- ENTERING setup_logging ---", file=sys.stderr, flush=True)
    print(f"Requested console level string: {log_level_console_str}, file level string: {log_level_file_str}, clear handlers: {clear_existing_handlers}", file=sys.stderr, flush=True)

    log_levels = {
        "CRITICAL": logging.CRITICAL, "ERROR": logging.ERROR, "WARNING": logging.WARNING,
        "INFO": logging.INFO, "DEBUG": logging.DEBUG, "NOTSET": logging.NOTSET,
    }

    console_level = log_levels.get(log_level_console_str.upper(), logging.INFO)
    file_level = log_levels.get(log_level_file_str.upper(), logging.DEBUG)
    print(f"Determined console level: {logging.getLevelName(console_level)}, file level: {logging.getLevelName(file_level)}", file=sys.stderr, flush=True)

    log_format_str = '%(asctime)s - %(levelname)-8s - %(name)-25s - [%(module)s.%(funcName)s:%(lineno)d] - RID:%(request_id)s - UID:%(user_identifier)s - %(message)s'
    date_format_str = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(log_format_str, datefmt=date_format_str)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    print(f"Root logger level set to DEBUG. Current handlers: {root_logger.handlers}", file=sys.stderr, flush=True)

    if clear_existing_handlers:
        if root_logger.hasHandlers():
            print(f"Root logger has handlers: {root_logger.handlers}. Clearing them now.", file=sys.stderr, flush=True)
            for handler in root_logger.handlers[:]:
                print(f"Removing handler: {handler}", file=sys.stderr, flush=True)
                root_logger.removeHandler(handler)
                handler.close() 
            print(f"Handlers after clearing: {root_logger.handlers}", file=sys.stderr, flush=True)
        else:
            print("Root logger has no handlers to clear.", file=sys.stderr, flush=True)

    context_filter = None
    try:
        from app.core.context import request_id_var, user_identifier_var

        class ContextualLogFilter(logging.Filter):
            def filter(self, record: logging.LogRecord) -> bool:
                record.request_id = request_id_var.get() if request_id_var.get() is not None else "-"
                record.user_identifier = user_identifier_var.get()
                return True
        context_filter = ContextualLogFilter()
        print("ContextualLogFilter created.", file=sys.stderr, flush=True)
    except ImportError as e_ctx:
        print(f"WARNING: Could not import context variables for logging filter: {e_ctx}. RID/UID will be default.", file=sys.stderr, flush=True)
    except Exception as e_filter:
        print(f"ERROR creating ContextualLogFilter: {e_filter}", file=sys.stderr, flush=True)

    # Add Console Handler
    new_console_handler = logging.StreamHandler(sys.stdout)
    new_console_handler.setLevel(console_level)
    new_console_handler.setFormatter(formatter)
    if context_filter: new_console_handler.addFilter(context_filter)
    root_logger.addHandler(new_console_handler)
    
    # Add File Handler
    log_file_path_str = "File logging disabled."
    try:
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=LOG_FILE_PATH, when='H', interval=1, backupCount=24*3,
            encoding='utf-8', delay=False, utc=True
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        if context_filter: file_handler.addFilter(context_filter)
        root_logger.addHandler(file_handler)
        log_file_path_str = f"Current log file: {str(LOG_FILE_PATH.resolve())}"
    except Exception as e:
        print(f"CRITICAL WARNING: Could not set up TimedRotatingFileHandler for {LOG_FILE_PATH}. Error: {e}", file=sys.stderr, flush=True)

    # --- MODIFIED: More targeted and less aggressive third-party logging setup ---
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Specifically control SQLAlchemy logging level. Set to WARNING to hide SQL queries,
    # or INFO to see them.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Allow Semantic Kernel to be verbose for debugging purposes
    logging.getLogger("semantic_kernel").setLevel(logging.INFO)
    # --- END MODIFICATION ---

    final_log_message = (
        f"Logging system configured. Root Level: DEBUG. "
        f"Console Level: {logging.getLevelName(console_level)}. "
        f"File Level: {logging.getLevelName(file_level)}. "
        f"{log_file_path_str}"
    )
    root_logger.info(final_log_message) 

