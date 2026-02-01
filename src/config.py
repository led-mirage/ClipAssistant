import sys
import ctypes
import os
import yaml
from dataclasses import dataclass, field
from typing import List

from app_const import APP_NAME

CONFIG_FILE = "config.yaml"


@dataclass
class AIConfig:
    api: str = "OpenAI"
    model: str = "gpt-5.1"
    openai_api_key_envvar: str = "OPENAI_API_KEY"
    azure_api_key_envvar: str = "AZURE_OPENAI_API_KEY"
    azure_endpoint_envvar: str = "AZURE_OPENAI_ENDPOINT"
    claude_api_key_envvar: str = "ANTHROPIC_API_KEY"
    gemini_api_key_envvar: str = "GEMINI_API_KEY"

    @classmethod
    def from_dict(cls, data: dict):
        return _safe_load_dataclass(cls, data)

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
    label: str = ""
    system_prompt: str = ""
    user_prompt: str = ""
    usage_message: str = ""
    display_original_text: bool = False

    @classmethod
    def from_dict(cls, data: dict):
        return _safe_load_dataclass(cls, data)


@dataclass
class WindowConfig:
    width: int = 800
    height: int = 400
    font_size: int = 16
    start_hidden: bool = False

    @classmethod
    def from_dict(cls, data: dict):
        return _safe_load_dataclass(cls, data)


@dataclass
class Config:
    ai: AIConfig
    window: WindowConfig
    modes: List[ModeConfig] = field(default_factory=list)

    @staticmethod
    def load(path: str = CONFIG_FILE, exit_on_error: bool = True) -> "Config":
        if not os.path.exists(path):
            if exit_on_error:
                ctypes.windll.user32.MessageBoxW(0, f"設定ファイル config.yaml が見つかりません。", APP_NAME, 0x10)
                sys.exit(1)
            else:
                raise FileNotFoundError(f"Config file not found: {path}")

        try:
            with open(path, encoding="utf-8") as f:
                raw = yaml.safe_load(f)
            
            if raw is None:
                raise ValueError("Config file is empty")

            # 安全にロード
            ai_data = raw.get("ai", {})
            window_data = raw.get("window", {})
            modes_list = raw.get("modes", [])
    
            modes_data = [ModeConfig.from_dict(m) for m in modes_list]
    
            return Config(
                ai=AIConfig.from_dict(ai_data),
                window=WindowConfig.from_dict(window_data),
                modes=modes_data
            )
        except Exception as e:
            if exit_on_error:
                print(f"Error loading config: {e}")
                ctypes.windll.user32.MessageBoxW(0, f"設定ファイル config.yaml の読み込みに失敗しました。\n\n{e}\n\n設定ファイルの内容を確認してください。", APP_NAME, 0x10)
                sys.exit(1)
            else:
                raise e

    def find_mode(self, label: str) -> ModeConfig | None:
        found = next((m for m in self.modes if m.label == label), None)
        return found or (self.modes[0] if self.modes else None)


def _safe_load_dataclass(cls, data: dict):
    from dataclasses import fields, MISSING
    
    # 既知のフィールドのみ抽出
    known_fields = {f.name: f for f in fields(cls)}
    filtered_data = {k: v for k, v in data.items() if k in known_fields}
    
    # 必須フィールドのチェック
    missing_fields = []
    for name, field_def in known_fields.items():
        if name not in filtered_data:
            # デフォルト値がない場合は必須
            if field_def.default is MISSING and field_def.default_factory is MISSING:
                missing_fields.append(name)
    
    if missing_fields:
        raise ValueError(f"Missing required fields in {cls.__name__}: {', '.join(missing_fields)}")
        
    return cls(**filtered_data)
