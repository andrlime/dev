import copy
import logging
from enum import StrEnum
from pathlib import Path


class SentinelColor(StrEnum):
    GRAY = "\033[37m"
    BOLD_WHITE = "\033[1;97m"
    RESET = "\033[0m"


class ColoredFormatter(logging.Formatter):
    def __init__(self, no_color: bool = False) -> None:
        super().__init__()
        self.no_color = no_color

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
        record = copy.copy(record)

        timestamp = self.formatTime(record, self.datefmt)
        message = record.getMessage()

        gray = "" if self.no_color else str(SentinelColor.GRAY)
        reset = "" if self.no_color else str(SentinelColor.RESET)
        level_color = "" if self.no_color else self.color_of_loglevel(record.levelno)
        name_color = "" if self.no_color else str(SentinelColor.BOLD_WHITE)

        level = f"{level_color}{record.levelname:<8}{reset}"
        name = f"{name_color}{record.name}{reset}"

        return f"{gray}{timestamp}{reset}  {level}  {name}{gray}: {message}{reset}"


class Logger:
    file_handler: logging.Handler | None = None
    no_color: bool = False

    @classmethod
    def get(cls, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(ColoredFormatter(no_color=cls.no_color))
            logger.addHandler(handler)
            logger.propagate = False
            if cls.file_handler is not None:
                logger.addHandler(cls.file_handler)
        return logger

    @staticmethod
    def set_log_level(level: int | str) -> None:
        logging.getLogger().setLevel(level)

    @classmethod
    def set_log_file(cls, path: str | Path) -> None:
        handler = logging.FileHandler(path)
        handler.setFormatter(ColoredFormatter(no_color=True))
        cls.file_handler = handler

    @classmethod
    def set_no_color(cls, no_color: bool) -> None:
        cls.no_color = no_color
