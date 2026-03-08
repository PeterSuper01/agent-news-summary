from huggingface_hub.utils import are_progress_bars_disabled
from langchain.agents.structured_output import ToolStrategy

from agents.schemes import NewsSummaryResponse
from app.config import settings
from agents.tools import retrieve_news_from_vectorstore
from create_models.llms import create_openai_llm
from langchain.agents.factory import create_agent
from langchain.messages import HumanMessage
from prompts.summarization_prompts import summarization_system_prompt


# agent = create_agent(
#     model=create_openai_llm(settings.OPENROUTER_MODEL_NAME),
#     tools=[retrieve_news_from_vectorstore],
#     system_prompt=summarization_system_prompt,
#     response_format=NewsSummaryResponse,
# )

if __name__ == "__main__":
    agent = create_agent(
        model=create_openai_llm(settings.OPENROUTER_MODEL_NAME),
        tools=[retrieve_news_from_vectorstore],
        system_prompt=summarization_system_prompt,
        response_format=ToolStrategy(NewsSummaryResponse),
    )
    print("Type 'quit', 'exit', or 'q' to end the conversation.\n")

    messages = []

    while True:
        input_message_from_user = input("Let's see what's new in the world: ")

        if input_message_from_user.lower() in ["quit", "exit", "q"]:
            print("Have a nice day!")
            break

        if not input_message_from_user:
            continue

        messages.append(HumanMessage(input_message_from_user))
        response = agent.invoke({"messages": messages})
        messages = response["messages"]
        last_message_from_agent = messages[-1].content
        print(f"\n{last_message_from_agent}\n")
