from functools import cached_property
from os import path
from pathlib import Path

import yaml  # type: ignore[import-untyped]
from dotenv import find_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(find_dotenv()).parent

class LoggerConfig(BaseSettings):
    LOG_CONFIG_PATH: str = path.join(BASE_DIR, 'config-log.yml')

    LOG_FILE_PATH: str = path.join(BASE_DIR, 'logs/app.log')

    @cached_property
    def CONFIG(self) -> dict:
        with open(self.LOG_CONFIG_PATH, 'rt') as f:
            config = yaml.safe_load(f)
            config["handlers"]["file"]["filename"] = self.LOG_FILE_PATH
        return config

logger_config = LoggerConfig() # type: ignore
