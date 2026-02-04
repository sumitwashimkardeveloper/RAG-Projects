import yaml
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

class Config:
    def __init__(self, config_path: str = None):
        load_dotenv()

        if config_path is None:
            config_path = os.getenv("CONFIG_PATH", "configs/config.yaml")

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        return config or {}

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_section(self, section: str) -> Dict[str, Any]:
        return self.config.get(section, {})

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

_config_instance = None

def get_config(config_path: str = None) -> Config:
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance
