from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from sidecar import main


async def _empty_async_iter():
    return
    yield  # makes this an async generator


@asynccontextmanager
async def _noop_lifespan(_app: object) -> AsyncIterator[None]:
    yield


@pytest.fixture
def client():
    """Client de test avec le lifespan désactivé."""
    # On désactive le lifespan pour contrôler _models_ready manuellement
    main.app.router.lifespan_context = _noop_lifespan
    return TestClient(main.app, raise_server_exceptions=False)


class TestHealthEndpoint:
    def test_health_loading(self, client: TestClient):
        main._models_ready = False
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "loading"}

    def test_health_ready(self, client: TestClient):
        main._models_ready = True
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"
        assert "chat_model" in data
        assert "embedding_model" in data


class TestLifespan:
    @pytest.mark.asyncio
    async def test_lifespan_pulls_models(self):
        """Vérifie que le lifespan attend Ollama puis pull les modèles."""
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.raise_for_status = lambda: None
        mock_response.aiter_lines = AsyncMock(return_value=iter([]))
        mock_client.get = AsyncMock(return_value=mock_response)

        # Simule le context manager de client.stream()
        mock_stream_response = MagicMock()
        mock_stream_response.raise_for_status = lambda: None
        mock_stream_response.aiter_lines = _empty_async_iter

        stream_call_count = 0

        @asynccontextmanager
        async def mock_stream(*args, **kwargs):
            nonlocal stream_call_count
            stream_call_count += 1
            yield mock_stream_response

        mock_client.stream = mock_stream

        main._models_ready = False

        with patch("sidecar.main.httpx.AsyncClient") as mock_cls:
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            async with main.lifespan(main.app):
                assert main._models_ready is True

        # Vérifie qu'on a appelé get (attente Ollama) et stream (pull modèles)
        mock_client.get.assert_called_once()
        assert stream_call_count == 2
