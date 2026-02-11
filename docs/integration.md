# Guide d'intégration
Doc générée par LLM, pas encore testé

## Usage standalone

### Démarrage

```bash
cp .env.example .env
docker compose up -d
```

### Attendre que les modèles soient prêts

Le sidecar expose un endpoint `/health` qui indique l'état du service :

```bash
# Pendant le téléchargement des modèles
curl http://localhost:8080/health
# {"status": "loading"}

# Une fois les modèles prêts
curl http://localhost:8080/health
# {"status": "ready", "chat_model": "mistral:7b", "embedding_model": "nomic-embed-text"}
```

### Exemples d'appels

**Chat complétion (format OpenAI) :**

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral:7b",
    "messages": [
      {"role": "system", "content": "Tu es un assistant utile."},
      {"role": "user", "content": "Explique Docker en une phrase."}
    ]
  }'
```

**Embeddings (format OpenAI) :**

```bash
curl http://localhost:11434/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nomic-embed-text",
    "input": "Texte à vectoriser pour la recherche sémantique"
  }'
```

**API native Ollama :**

```bash
curl http://localhost:11434/api/chat \
  -d '{"model": "mistral:7b", "messages": [{"role": "user", "content": "Bonjour"}]}'
```

## Intégration avec un autre projet

Deux patterns sont possibles pour intégrer `local-llm-service` dans un autre projet Docker Compose.

### Pattern 1 : Docker Compose `include` (recommandé)

Requiert Docker Compose v2.20+. Le fichier `docker-compose.yml` du projet consommateur :

```yaml
include:
  - path: ../local-llm-service/docker-compose.yml

services:
  my-rag-app:
    build: .
    environment:
      - OPENAI_API_BASE=http://ollama:11434/v1
      - OPENAI_API_KEY=not-needed
    networks:
      - llm-network
```

Les services `ollama` et `sidecar` sont automatiquement inclus. Le réseau `llm-network` est partagé, donc `my-rag-app` peut accéder à Ollama via `http://ollama:11434`.

### Pattern 2 : Réseau externe

Si `local-llm-service` tourne déjà séparément, le projet consommateur peut se connecter via le réseau Docker existant :

```yaml
services:
  my-rag-app:
    build: .
    environment:
      - OPENAI_API_BASE=http://ollama:11434/v1
      - OPENAI_API_KEY=not-needed
    networks:
      - llm-net

networks:
  llm-net:
    external: true
    name: llm-network
```

### Configuration côté application

Dans les deux cas, l'application consommatrice utilise :

| Variable | Valeur |
|---|---|
| `OPENAI_API_BASE` | `http://ollama:11434/v1` |
