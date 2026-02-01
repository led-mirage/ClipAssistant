import os
import yaml
from dataclasses import dataclass, field
from typing import List

CONFIG_FILE = "config.yaml"
FILE_VERSION = 1


@dataclass
class AIConfig:
    api: str
    model: str
    openai_api_key_envvar: str
    azure_api_key_envvar: str
    azure_endpoint_envvar: str
    claude_api_key_envvar: str
    gemini_api_key_envvar: str

    @property
    def api_key(self) -> str | None:
        return os.getenv(self.openai_api_key_envvar)

    @property
    def azure_api_key(self) -> str | None:
        return os.getenv(self.azure_api_key_envvar)

    @property
    def azure_endpoint(self) -> str | None:
        return os.getenv(self.azure_endpoint_envvar)
    
    @property
    def claude_api_key(self) -> str | None:
        return os.getenv(self.claude_api_key_envvar)
    
    @property
    def gemini_api_key(self) -> str | None:
        return os.getenv(self.gemini_api_key_envvar)


@dataclass
class ModeConfig:
    label: str
    system_prompt: str
    user_prompt: str
    usage_message: str
    display_original_text: bool


@dataclass
class WindowConfig:
    width: int
    height: int
    font_size: int
    start_hidden: bool = False


@dataclass
class Config:
    ai: AIConfig
    window: WindowConfig
    modes: List[ModeConfig] = field(default_factory=list)

    @staticmethod
    def load(path: str = CONFIG_FILE) -> "Config":
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        Config._migration(raw)
        
        # データクラスへのマッピング
        # modesは辞書のリストなので、ModeConfigオブジェクトのリストに変換
        modes_data = [ModeConfig(**m) for m in raw.get("modes", [])]

        return Config(
            ai=AIConfig(**raw["ai"]),
            window=WindowConfig(**raw["window"]),
            modes=modes_data
        )
    
    @staticmethod
    def _migration(raw: any):
        file_version = raw.get("filever", 1)

    def find_mode(self, label: str) -> ModeConfig | None:
        found = next((m for m in self.modes if m.label == label), None)
        return found or (self.modes[0] if self.modes else None)


if __name__ == "__main__":
    # For Test
    cfg = Config.load()
    mode = cfg.find_mode("要約")
    print(mode)
