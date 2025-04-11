import secrets

import laima
from chatbot.core.repositories import ChatHistoryRepository, ChunkRepository


@laima.singleton
class InMemoryChunkRepository(ChunkRepository):
    def __init__(self) -> None:
        self.id = secrets.token_hex(2)

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}[{self.id}]"

    def find_chunks(self, query: str, n_results: int) -> list[str]:
        print(f"{self}.find_chunks")
        return list(reversed(list(query)[:n_results]))


@laima.singleton
class InMemoryChatHistoryRepository(ChatHistoryRepository):
    def __init__(self) -> None:
        self.id = secrets.token_hex(2)

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}[{self.id}]"

    def get_history(self, chat_id: str) -> list[str]:
        print(f"{self}.get_history")
        return list(reversed(list(chat_id)))
