import sqlite3
import os
from abc import ABC, abstractmethod
from typing import Any, Optional

class Connector(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

class HttpConnector(Connector):
    """Stub HTTP connector that returns mock responses.

    This is a placeholder implementation intended for testing and local
    development. Replace ``get`` and ``post`` with real HTTP calls (e.g.
    via ``urllib.request``) when connecting to live services.
    """

    def __init__(self, base_url: str = ""):
        self.base_url = base_url

    def connect(self):
        pass

    def disconnect(self):
        pass

    def get(self, url: str, headers: dict = None) -> dict:
        return {"status": 200, "body": f"GET {url}", "headers": {}}

    def post(self, url: str, data: Any, headers: dict = None) -> dict:
        return {"status": 200, "body": f"POST {url}", "data": data}

class DatabaseConnector(Connector):
    def __init__(self):
        self._conn = None

    def connect(self):
        self._conn = sqlite3.connect(":memory:")
        self._conn.row_factory = sqlite3.Row

    def disconnect(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def query(self, sql: str, params: tuple = None) -> list[dict]:
        if not self._conn:
            self.connect()
        cursor = self._conn.cursor()
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def execute(self, sql: str, params: tuple = None) -> int:
        if not self._conn:
            self.connect()
        cursor = self._conn.cursor()
        cursor.execute(sql, params or ())
        self._conn.commit()
        return cursor.rowcount

class FileConnector(Connector):
    def __init__(self, base_path: str = "."):
        self.base_path = base_path

    def connect(self):
        pass

    def disconnect(self):
        pass

    def read(self, path: str) -> str:
        with open(os.path.join(self.base_path, path), "r") as f:
            return f.read()

    def write(self, path: str, data: str) -> bool:
        with open(os.path.join(self.base_path, path), "w") as f:
            f.write(data)
        return True

    def list(self, directory: str) -> list[str]:
        full_path = os.path.join(self.base_path, directory)
        return os.listdir(full_path)

class ConnectorRegistry:
    def __init__(self):
        self._connectors: dict[str, Connector] = {}

    def register(self, name: str, connector: Connector) -> None:
        self._connectors[name] = connector

    def get(self, name: str) -> Optional[Connector]:
        return self._connectors.get(name)

    def list_connectors(self) -> list[str]:
        return list(self._connectors.keys())
