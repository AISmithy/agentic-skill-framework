"""HTTP and generic connector pool for skill external calls."""

from __future__ import annotations

from typing import Any

import httpx

from agentic.core.exceptions import ConnectorError
from agentic.layer7_observability.logger import get_logger

logger = get_logger(__name__)


class HTTPConnector:
    """Async HTTP connector backed by httpx."""

    def __init__(self, base_url: str = "", timeout_s: float = 30.0) -> None:
        self._base_url = base_url
        self._timeout = httpx.Timeout(timeout_s)

    async def get(self, url: str, **kwargs: Any) -> dict[str, Any]:
        full_url = f"{self._base_url}{url}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(full_url, **kwargs)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            raise ConnectorError("http", str(exc)) from exc

    async def post(self, url: str, json: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        full_url = f"{self._base_url}{url}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(full_url, json=json, **kwargs)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            raise ConnectorError("http", str(exc)) from exc


class ConnectorManager:
    """Registry of named connectors available to skill executors."""

    def __init__(self) -> None:
        self._http_connectors: dict[str, HTTPConnector] = {}

    def register_http(self, name: str, base_url: str = "", timeout_s: float = 30.0) -> None:
        self._http_connectors[name] = HTTPConnector(base_url=base_url, timeout_s=timeout_s)

    def http(self, name: str = "default") -> HTTPConnector:
        if name not in self._http_connectors:
            # Auto-create a default connector
            self._http_connectors[name] = HTTPConnector()
        return self._http_connectors[name]
