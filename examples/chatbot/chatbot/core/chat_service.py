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
        self._chunk_repository = chunk_repository
        self._history_repository = history_repository
        self._model = model
        self._n_chunks = n_chunks

    def chat(self, chat_id: str, message: str) -> str:
        history = self._history_repository.get_history(
            chat_id=chat_id,
        )
        chunks = self._chunk_repository.find_chunks(
            query=message,
            n_results=self._n_chunks,
        )
        text = "-".join(history) + "_" + "-".join(chunks) + "_" + message
        return self._model.complete(text)
