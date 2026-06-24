import copy
import logging
from enum import StrEnum


class SentinelColor(StrEnum):
    GRAY = "\033[37m"
    BOLD_WHITE = "\033[1;97m"
    RESET = "\033[0m"


class ColoredFormatter(logging.Formatter):
    @staticmethod
    def color_of_loglevel(level: int) -> str:
        match level:
            case logging.DEBUG:
                return "\033[2m"
            case logging.INFO:
                return "\033[92m"
            case logging.WARNING:
                return "\033[93m"
            case logging.ERROR:
                return "\033[91m"
            case logging.CRITICAL:
                return "\033[48;2;220;20;60m\033[97m"
            case _:
                return ""

    def format(self, record: logging.LogRecord) -> str:
        reset = SentinelColor.RESET

        record = copy.copy(record)

        timestamp = self.formatTime(record, self.datefmt)
        level = f"{self.color_of_loglevel(record.levelno)}{record.levelname:<8}{reset}"
        name = f"{SentinelColor.BOLD_WHITE}{record.name}{reset}"
        message = record.getMessage()

        return f"{SentinelColor.GRAY}{timestamp}{reset}  {level}  {name}{SentinelColor.GRAY}: {message}{reset}"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(ColoredFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger
