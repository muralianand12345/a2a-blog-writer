import os
import sys
import logging
from logging.handlers import RotatingFileHandler

from config import LOG_LEVEL

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("blog_writer_client")
logger.setLevel(getattr(logging, LOG_LEVEL))

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(getattr(logging, LOG_LEVEL))
console_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(console_format)

file_handler = RotatingFileHandler(
    "logs/blog_writer_client.log",
    maxBytes=10485760,  # 10MB
    backupCount=5,
)
file_handler.setLevel(getattr(logging, LOG_LEVEL))
file_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_format)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
