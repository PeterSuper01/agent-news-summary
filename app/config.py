from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # The Guardian
    THEGUARDIAN_API_KEY: str
    THEGUARDIAN_SECTION_URL: str = "https://content.guardianapis.com/sections"
    THEGUARDIAN_NEWS_UPDATE_INTERVAL_HOURS: int = 6
    THEGUARDIAN_NEWS_UPDATE_PAGE_SIZE: int = 10
    THEGUARDIAN_NEWS_SUMMARY_MAX_LENGTH: int = 1000

    # OpenRouter
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL_NAME: str = "stepfun/step-3.5-flash:free"

    # Hugging Face
    HF_TOKEN: str

    # Chroma DB
    CHROMA_DB_DIR: str = "./chroma_langchain_db"
    CHROMA_DB_COLLECTION_DISTANCE_METRIC: str = "cosine"  # "l2" or "cosine" or "ip"
    EMBEDDING_MODEL_CACHE_FOLDER: str = "./models/embedding_models"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-mpnet-base-v2"

    # Vectorstore
    VECTORSTORE_SEARCH_K: int = 3

    # Scheduler
    SCHEDULER_INITIALIZED: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
