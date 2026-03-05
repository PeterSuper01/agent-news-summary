from huggingface_hub.utils import are_progress_bars_disabled

from app.config import settings
from agents.tools import retrieve_news_from_vectorstore
from create_models.llms import create_openai_llm
from langchain.agents.factory import create_agent
from langchain.messages import HumanMessage
from prompts.summarization_prompts import summarization_system_prompt


agent = create_agent(
    model=create_openai_llm(settings.OPENROUTER_MODEL_NAME),
    tools=[retrieve_news_from_vectorstore],
    system_prompt=summarization_system_prompt,
)

if __name__ == "__main__":
    input_message_from_user = input("Let's see what's new in the world: ")
    response = agent.invoke({"messages": [HumanMessage(input_message_from_user)]})
    last_message_from_agent = response["messages"][-1].content
    print(last_message_from_agent)
