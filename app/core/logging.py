import logging
import sys
from pathlib import Path

import colorlog


# ==========================================
# CREATE LOG DIRECTORY
# ==========================================
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"


# ==========================================
# LOG FORMATTERS
# ==========================================
LOG_FORMAT = (
    "%(log_color)s"
    "[%(asctime)s] "
    "[%(levelname)s] "
    "[%(name)s] "
    "%(message)s"
)

FILE_LOG_FORMAT = (
    "[%(asctime)s] "
    "[%(levelname)s] "
    "[%(name)s] "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ==========================================
# CONSOLE HANDLER
# ==========================================
console_handler = logging.StreamHandler(sys.stdout)

console_formatter = colorlog.ColoredFormatter(
    LOG_FORMAT,
    datefmt=DATE_FORMAT,
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }
)

console_handler.setFormatter(console_formatter)


# ==========================================
# FILE HANDLER
# ==========================================
file_handler = logging.FileHandler(LOG_FILE)

file_formatter = logging.Formatter(
    FILE_LOG_FORMAT,
    datefmt=DATE_FORMAT
)

file_handler.setFormatter(file_formatter)


# ==========================================
# ROOT LOGGER CONFIG
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        console_handler,
        file_handler
    ]
)


# ==========================================
# LOGGER FACTORY
# ==========================================
def get_logger(name: str):
    return logging.getLogger(name)