import secrets

import laima
from chatbot.core.repositories import ChatHistoryRepository, ChunkRepository
from chatbot.gateways.databases.postgres.postgres_database import PostgresDatabase


@laima.transient
class PostgresChunkRepository(ChunkRepository):
    def __init__(self, database: PostgresDatabase) -> None:
        self.database = database
        self.id = secrets.token_hex(2)

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}[{self.id}]"

    def find_chunks(self, query: str, n_results: int) -> list[str]:
        session = self.database.get_session()
        print(f"{self}.find_chunks+{session}")
        return list(query)[:n_results]


@laima.transient
class PostgresChatHistoryRepository(ChatHistoryRepository):
    def __init__(self, database: PostgresDatabase) -> None:
        self.database = database
        self.id = secrets.token_hex(2)

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}[{self.id}]"

    def get_history(self, chat_id: str) -> list[str]:
        session = self.database.get_session()
        print(f"{self}.get_history+{session}")
        return list(chat_id)
