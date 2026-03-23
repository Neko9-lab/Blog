from loguru import logger


def setup_logging() -> None:
    logger.add("logs/app.log", rotation="10 MB", retention="7 days", enqueue=True)
