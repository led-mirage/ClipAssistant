from dataclasses import dataclass, fields, asdict
import yaml
from pathlib import Path

STATE_FILE = "state.yaml"
FILE_VERSION = 1


@dataclass
class State:
    _file_version: int = FILE_VERSION
    current_mode_label: str = "翻訳"

    def save(self, path: str = STATE_FILE) -> None:
        p = Path(path)
        with p.open("w", encoding="utf-8") as f:
            yaml.safe_dump(asdict(self), f, allow_unicode=True)

    @classmethod
    def load(cls, path: str = STATE_FILE) -> "State":
        p = Path(STATE_FILE)
        if not p.exists():
            return cls()

        try:
            with p.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            cls._migration(data)
            return cls(**data)
        except (OSError, yaml.YAMLError, TypeError, ValueError):
            return cls()

    @classmethod
    def _migration(cls, data: dict):
        file_version = data.get("_file_version", 1)
        # migration logic here!
