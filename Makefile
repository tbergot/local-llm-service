.PHONY: help build up down logs pull-models health test lint

.DEFAULT_GOAL := help

help: ## Afficher cette aide
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-14s %s\n", $$1, $$2}'

build: ## Build les images Docker
	docker compose build

up: ## services up
	docker compose up -d

down: ## services down
	docker compose down

pull-models: ## retélécharger les modèles
	docker compose exec ollama ollama pull $${LLM_CHAT_MODEL:-mistral:7b}
	docker compose exec ollama ollama pull $${LLM_EMBEDDING_MODEL:-nomic-embed-text}

health: ## Vérifier l'état du service
	@curl -sf http://localhost:8080/health | python3 -m json.tool

lint: ## Ruff
	ruff check
	ruff format --check

test: ## Lancer les tests
	python -m pytest tests/
