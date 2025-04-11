from collections.abc import Iterator

import laima
from chatbot.core.chat_service import ChatService
from chatbot.core.repositories import ChatHistoryRepository, ChunkRepository
from chatbot.gateways.databases.in_memory.in_memory_repositories import (
    InMemoryChatHistoryRepository,
    InMemoryChunkRepository,
)
from chatbot.gateways.databases.postgres.postgres_database import PostgresDatabase
from chatbot.gateways.databases.postgres.postgres_repositories import (
    PostgresChatHistoryRepository,
    PostgresChunkRepository,
)
from chatbot.gateways.llm_providers.azure_llm_provider import AzureLlmProvider


@laima.singleton
def get_postgres_database() -> Iterator[PostgresDatabase]:
    database = PostgresDatabase(
        url="<url>",
    )
    print(f"start {database}")
    yield database
    print(f"finish {database}")


@laima.singleton
def get_azure_llm_provider() -> Iterator[AzureLlmProvider]:
    ll_provider = AzureLlmProvider(
        api_key="<secret>",
    )
    print(f"start {ll_provider}")
    yield ll_provider
    print(f"finish {ll_provider}")


@laima.transient
def get_chat_service() -> Iterator[ChatService]:
    service = ChatService(
        model=get_azure_llm_provider(),
        n_chunks=5,
    )
    print(f"start {service}")
    yield service
    print(f"finish {service}")


def setup(
    repository: str,
) -> None:
    laima.bind(get_postgres_database, to=PostgresDatabase)
    laima.bind(get_chat_service, to=ChatService)

    match repository:
        case "in_memory":
            laima.bind(InMemoryChunkRepository, to=ChunkRepository)
            laima.bind(InMemoryChatHistoryRepository, to=ChatHistoryRepository)
        case "postgres":
            get_postgres_database()
            laima.bind(PostgresChunkRepository, to=ChunkRepository)
            laima.bind(PostgresChatHistoryRepository, to=ChatHistoryRepository)
        case _:
            raise ValueError(f"Unsupported database {repository}")
