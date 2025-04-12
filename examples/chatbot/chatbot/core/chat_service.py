import secrets

import laima
from chatbot.core.llm_provider import LlmProvider
from chatbot.core.repositories import ChatHistoryRepository, ChunkRepository


class ChatService:
    @laima.inject
    def __init__(
        self,
        chunk_repository: ChunkRepository,
        history_repository: ChatHistoryRepository,
        model: LlmProvider,
        n_chunks: int,
    ) -> None:
        self.chunk_repository = chunk_repository
        self.history_repository = history_repository
        self.model = model
        self.n_chunks = n_chunks
        self.id = secrets.token_hex(2)

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}[{self.id}]"

    def chat(self, chat_id: str, message: str) -> str:
        history = self.history_repository.get_history(
            chat_id=chat_id,
        )
        chunks = self.chunk_repository.find_chunks(
            query=message,
            n_results=self.n_chunks,
        )
        text = "-".join(history) + "_" + "-".join(chunks) + "_" + message
        return self.model.complete(text)
