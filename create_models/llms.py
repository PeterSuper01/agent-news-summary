from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI

from app.config import settings


def create_openai_llm(model: str) -> ChatOpenAI:
    return init_chat_model(
        model=model,
        model_provider="openai",
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
    )


if __name__ == "__main__":
    llm = create_openai_llm(settings.OPENROUTER_MODEL_NAME)
    resp = llm.invoke("How long a paragraph can you handle?")
    print(resp)
