import secrets
from collections.abc import Iterator

import laima


class PostgresDatabase:
    def __init__(self, url: str) -> None:
        self.url = url
        self.id = secrets.token_hex(2)

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}[{self.id}]"

    @laima.scoped
    def get_session(self) -> Iterator["PostgresSession"]:
        session = PostgresSession(self)
        print(f"start {session}")
        yield session
        print(f"finish {session}")


class PostgresSession:
    @laima.inject
    def __init__(self, database: PostgresDatabase) -> None:
        self.database = database
        self.id = secrets.token_hex(2)

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}[{self.id}]"
