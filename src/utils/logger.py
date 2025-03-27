import logging
import logging.config
import sys
from pathlib import Path
from src.utils.config import config

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging_config = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": sys.stdout,
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": logs_dir / "app.log",
            "mode": "a",
        },
    },
    "root": {
        "level": config.LOG_LEVEL,
        "handlers": ["console", "file"],
    },
}

# Apply logging configuration
logging.config.dictConfig(logging_config)

# Create a logger instance
logger = logging.getLogger(__name__)
