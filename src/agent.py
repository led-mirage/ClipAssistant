import os

from openai import OpenAI, AzureOpenAI
from anthropic import Anthropic
from google import genai

from config import Config, ModeConfig


class Agent:
    def __init__(self, config: Config):
        self.client = self.create_client(config)
        self.api = config.ai.api
        self.model = config.ai.model


    def create_client(self, config: Config) -> OpenAI | AzureOpenAI:
        if config.ai.api == "OpenAI":
            api_key = os.getenv(config.ai.openai_api_key_envvar)
            return OpenAI(api_key=api_key)
        
        if config.ai.api == "AzureOpenAI":
            api_key = os.getenv(config.ai.azure_api_key_envvar)
            endpoint = os.getenv(config.ai.azure_endpoint_envvar)
            return AzureOpenAI(
                api_key=api_key,
                azure_endpoint=endpoint,
                api_version="2025-04-01-preview",
            )

        if config.ai.api == "Claude":
            api_key = os.getenv(config.ai.claude_api_key_envvar)
            return Anthropic(api_key=api_key)

        if config.ai.api == "Gemini":
            api_key = os.getenv(config.ai.gemini_api_key_envvar)
            return genai.Client(api_key=api_key)

        raise ValueError(f"Unsupported AI API: {config.ai.api}")


    def generate_text(self, text: str, mode: ModeConfig) -> str:
        if self.api in ["OpenAI", "AzureOpenAI"]:
            return self._generate_openai_style(text, mode)
        
        if self.api == "Claude":
            return self._generate_claude(text, mode)
        
        if self.api == "Gemini":
            return self._generate_gemini(text, mode)
        
        raise ValueError(f"Unsupported AI api: {self.api}")


    def _generate_openai_style(self, text: str, mode: ModeConfig) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": f"{mode.system_prompt}",
                },
                {
                    "role": "user",
                    "content": f"{mode.user_prompt}\n\n{text}",
                },
            ],
        )
        return response.choices[0].message.content


    def _generate_claude(self, text: str, mode: ModeConfig) -> str:
        message = self.client.messages.create(
            model=self.model,
            system=mode.system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"{mode.user_prompt}\n\n{text}",
                }
            ],
            max_tokens=4096,
        )
        return message.content[0].text
    

    def _generate_gemini(self, text: str, mode: ModeConfig) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            config={
                "system_instruction": mode.system_prompt
            },
            contents=f"{mode.user_prompt}\n\n{text}"
        )
        return response.text
