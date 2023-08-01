import logging
import sys

from loguru import logger


# Using InterceptionHandler from loguru docs to redirect logs
# from standard logging module into loguru's logger.
# Source: https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(
            depth=depth,
            exception=record.exc_info,
        ).log(level, record.getMessage())


def redirect_standard_logging_to_loguru() -> None:
    """Configure logging to redirect its logs to loguru"""
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


def disable_low_level_logs() -> None:
    """Disable logs from low-level libraries"""
    logger.disable('asyncio')
    logger.disable('httpx')
    logger.disable('httpcore')
    logger.disable('hpack')
    logger.disable('psycopg')
    logger.disable('apscheduler')


def set_logging_level(level: int | str) -> None:
    """Set logging level for loguru"""
    logger.remove()
    logger.add(sys.stderr, level=level)
