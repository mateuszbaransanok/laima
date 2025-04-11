import secrets

from chatbot.core.llm_provider import LlmProvider


class AzureLlmProvider(LlmProvider):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.id = secrets.token_hex(2)

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}[{self.id}]"

    def complete(self, text: str) -> str:
        return text.upper()
