# local-llm-service

Service local wrappant [Ollama](https://ollama.ai) dans un setup Docker Compose, exposant une API compatible OpenAI (chat/complétion + embeddings). Un sidecar FastAPI gère les health checks et le téléchargement automatique des modèles au démarrage.

## Prérequis

- Docker & Docker Compose (v2.20+)
- ~10 Go d'espace disque pour les modèles par défaut

## Quickstart

```bash
cp .env.example .env
make up
```

Vérifier que tout est prêt :
```bash
make health
# {"status": "ready", "chat_model": "mistral:7b", "embedding_model": "nomic-embed-text"}
```

## Configuration des modèles

Éditer `.env` pour changer les modèles :

| Variable | Défaut | Description |
|---|---|---|
| `LLM_CHAT_MODEL` | `mistral:7b` | Modèle de chat/complétion |
| `LLM_EMBEDDING_MODEL` | `nomic-embed-text` | Modèle d'embeddings |
| `LLM_SERVICE_PORT` | `11434` | Port exposé sur l'hôte |

## API

L'API Ollama est exposée sur `http://localhost:${LLM_SERVICE_PORT}` et supporte le format OpenAI :

**Chat complétion :**
```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral:7b",
    "messages": [{"role": "user", "content": "Bonjour !"}]
  }'
```

**Embeddings :**
```bash
curl http://localhost:11434/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nomic-embed-text",
    "input": "Texte à vectoriser"
  }'
```

**Health check (sidecar) :**
```bash
curl http://localhost:8080/health
```

## Intégration

Ce service est conçu pour être intégré dans d'autres projets. Voir le [guide d'intégration](docs/integration.md) pour les détails.

## Commandes Make

| Commande | Description |
|---|---|
| `make build` | Build les images Docker |
| `make up` | Démarrer les services |
| `make down` | Arrêter les services |
| `make pull-models` | Re-télécharger les modèles |
| `make health` | Vérifier l'état du service |
| `make test` | Lancer les tests |
