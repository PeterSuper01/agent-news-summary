from pprint import pprint

from app.config import settings
from create_models.llms import create_openai_llm
from langchain.agents.factory import create_agent
from langchain.messages import HumanMessage
from prompts.summarization_prompts import summarization_system_prompt

from agents.tools import (
    load_latest_news_from_the_guardian,
    retrieve_news_from_vectorstore,
)

agent = create_agent(
    model=create_openai_llm(settings.OPENROUTER_MODEL_NAME),
    tools=[retrieve_news_from_vectorstore],
    system_prompt=summarization_system_prompt,
)

if __name__ == "__main__":
    messages = [HumanMessage("Summarize the latest news in sports")]
    response = agent.invoke({"messages": messages})
    pprint(response, sort_dicts=False)
