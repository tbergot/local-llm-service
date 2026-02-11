import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from sidecar.config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = Settings()

# État global : passe à True une fois les modèles téléchargés
_models_ready = False

N_TENTATIVES = 60


async def _wait_for_ollama(client: httpx.AsyncClient) -> None:
    """Attend qu'Ollama soit prêt à répondre."""
    import asyncio

    url = f"{settings.ollama_base_url}/api/tags"
    for attempt in range(1, N_TENTATIVES + 1):
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            logger.info("Ollama est prêt (tentative %d)", attempt)
            return
        except (httpx.ConnectError, httpx.HTTPStatusError):
            logger.debug("Ollama pas encore prêt (tentative %s/%s)", attempt, N_TENTATIVES)
            await asyncio.sleep(2)
    msg = f"Ollama n'a pas répondu après {N_TENTATIVES} tentatives"
    raise TimeoutError(msg)


async def _pull_model(client: httpx.AsyncClient, model: str) -> None:
    """Déclenche le téléchargement d'un modèle via l'API Ollama."""
    logger.info("Téléchargement du modèle '%s'…", model)
    url = f"{settings.ollama_base_url}/api/pull"

    # Le pull peut être long ; on stream la réponse pour ne pas timeout
    async with client.stream("POST", url, json={"name": model}, timeout=None) as resp:
        resp.raise_for_status()
        async for line in resp.aiter_lines():
            logger.debug("pull %s: %s", model, line)
    logger.info("Modèle '%s' prêt", model)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Attend Ollama puis télécharge les modèles configurés au démarrage."""
    global _models_ready

    async with httpx.AsyncClient() as client:
        await _wait_for_ollama(client)
        await _pull_model(client, settings.llm_chat_model)
        await _pull_model(client, settings.llm_embedding_model)

    _models_ready = True
    logger.info("Tous les modèles sont prêts")

    yield

    logger.info("Rien a rouler à la fermeture")


app = FastAPI(title="local-llm-service sidecar", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    """Renvoie l'état du service et les modèles configurés."""
    if not _models_ready:
        return {"status": "loading"}
    return {
        "status": "ready",
        "chat_model": settings.llm_chat_model,
        "embedding_model": settings.llm_embedding_model,
    }
