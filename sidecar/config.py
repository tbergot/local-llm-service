from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Config du sidecar."""

    llm_chat_model: str = "mistral:7b"
    llm_embedding_model: str = "nomic-embed-text"
    ollama_host: str = "ollama"
    ollama_port: int = 11434

    @property
    def ollama_base_url(self) -> str:
        return f"http://{self.ollama_host}:{self.ollama_port}"
