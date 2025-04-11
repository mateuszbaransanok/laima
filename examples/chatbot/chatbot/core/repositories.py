from abc import ABC, abstractmethod


class ChunkRepository(ABC):
    @abstractmethod
    def find_chunks(self, query: str, n_results: int) -> list[str]:
        pass



class ChatHistoryRepository(ABC):
    @abstractmethod
    def get_history(self, chat_id: str) -> list[str]:
        pass
