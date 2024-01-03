import os
import logging
import logging.config

import colorama
from colorama import Fore as F
from colorama import Style as S


if not os.path.exists('logs/'):
    os.mkdir('logs/')


colorama.init()

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
OUTPUT_FORMAT = (f"{F.GREEN}%(asctime)s{S.RESET_ALL} | %(name)s\t| "
                 f"%(levelcolor)s%(levelname)-8s{S.RESET_ALL} | "
                 f"{F.CYAN}%(module)s:%(funcName)s:%(lineno)s{S.RESET_ALL} - %(levelcolor)s%(message)s{S.RESET_ALL}")


DEFAULT_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug": {
            "()": "log.DebugTraceFilter",
        }
    },
    "formatters": {
        "stdout": {
            "()": "log.StdoutFormatter",
            "fmt": OUTPUT_FORMAT,
            "style": "%",
            "defaults": {
                "levelcolor": colorama.Fore.LIGHTBLACK_EX
            }
        },
        "file": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(module)s %(pathname)s %(filename)s %(funcName)s "
                      "%(lineno)s %(message)s %(exc_info)s %(exc_text)s",
            "datefmt": DATETIME_FORMAT,
        },
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "stdout",
            "level": "NOTSET",
            "stream": "ext://sys.stdout",
            "filters": ["require_debug"],
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "file",
            "level": "INFO",
            "filename": "logs/app.log",
            "mode": "a",
            "maxBytes": 102400,
            "backupCount": 10,
        },
    },
    "loggers": {
        "app": {
            "propagate": False,
            "handlers": ["stdout", "file"],
            "filters": ["require_debug"],
        },
        "app.auth": {
            "propagate": True,
        },
        "app.files": {
            "propagate": True,
        },
        "app.links": {
            "propagate": True,
        },
        "app.oth": {
            "propagate": True,
        },
    }
}


class DebugTraceFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        if __debug__:
            return True
        return record.levelno > logging.DEBUG


class StdoutFormatter(logging.Formatter):
    _CS = {
        "TRACE": colorama.Fore.CYAN,
        "DEBUG": colorama.Fore.BLUE,
        "INFO": colorama.Fore.LIGHTWHITE_EX,
        "WARNING": colorama.Fore.YELLOW,
        "ERROR": colorama.Fore.RED,
        "CRITICAL": colorama.Back.RED,
    }

    def format(self, record: logging.LogRecord):
        setattr(record, 'levelcolor', self._CS.get(record.levelname, colorama.Fore.LIGHTBLACK_EX))
        return super().format(record)


def setup_logging():
    logging.root.setLevel(logging.NOTSET)
    logging.addLevelName(5, "TRACE")
    logging.config.dictConfig(DEFAULT_LOGGING)
