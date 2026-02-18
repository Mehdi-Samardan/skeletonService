import logging
import sys


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("skeleton_service")

    logger.setLevel(logging.INFO)

    # Prevent duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


logger = setup_logger()
