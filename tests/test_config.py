import os

from sidecar.config import Settings


class TestSettingsDefaults:
    def test_default_chat_model(self):
        settings = Settings()
        assert settings.llm_chat_model == "mistral:7b"

    def test_default_embedding_model(self):
        settings = Settings()
        assert settings.llm_embedding_model == "nomic-embed-text"

    def test_default_ollama_host(self):
        settings = Settings()
        assert settings.ollama_host == "ollama"

    def test_default_ollama_port(self):
        settings = Settings()
        assert settings.ollama_port == 11434

    def test_ollama_base_url(self):
        settings = Settings()
        assert settings.ollama_base_url == "http://ollama:11434"


class TestSettingsOverrides:
    def test_override_from_env(self, monkeypatch: object):
        monkeypatch.setattr(
            os,
            "environ",
            {
                "LLM_CHAT_MODEL": "llama3:8b",
                "LLM_EMBEDDING_MODEL": "mxbai-embed-large",
                "OLLAMA_HOST": "localhost",
                "OLLAMA_PORT": "9999",
            },
        )
        settings = Settings()
        assert settings.llm_chat_model == "llama3:8b"
        assert settings.llm_embedding_model == "mxbai-embed-large"
        assert settings.ollama_host == "localhost"
        assert settings.ollama_port == 9999
        assert settings.ollama_base_url == "http://localhost:9999"
