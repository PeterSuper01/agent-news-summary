import chainlit as cl
from langchain.agents.structured_output import ToolStrategy

from agents.schemes import NewsSummaryResponse
from app.config import settings
from agents.tools import retrieve_news_from_vectorstore
from background_service.scheduler import (
    create_news_update_scheduler,
    create_expired_news_cleanup_scheduler,
)
from background_service.tasks import update_all_sections, clear_expired_news
from create_models.llms import create_openai_llm
from langchain.agents.factory import create_agent
from langchain.messages import HumanMessage
from news.allowed_sections import allowed_sections
from prompts.summarization_prompts import summarization_system_prompt


@cl.on_chat_start
async def start():
    agent = create_agent(
        model=create_openai_llm(settings.OPENROUTER_MODEL_NAME),
        tools=[retrieve_news_from_vectorstore],
        system_prompt=summarization_system_prompt,
        response_format=ToolStrategy(
            NewsSummaryResponse, tool_message_content="Returning structured response:"
        ),
    )

    update_all_sections(allowed_sections)
    news_update_scheduler = create_news_update_scheduler(allowed_sections)
    news_update_scheduler.start()

    clear_expired_news()
    expired_news_cleanup_scheduler = create_expired_news_cleanup_scheduler()

    expired_news_cleanup_scheduler.start()
    cl.user_session.set("agent", agent)
    cl.user_session.set("messages", [])

    await cl.Message(
        content="Hello! Let's see what's new in the world. What topic would you like to know about today?"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")
    messages = cl.user_session.get("messages")
    messages.append(HumanMessage(content=message.content))
    response = await cl.make_async(agent.invoke)({"messages": messages})
    structured_response = response["structured_response"]
    data_dict = structured_response.model_dump()
    # Generate and send the formatted English UI
    formatted_content = format_for_display(data_dict)

    await cl.Message(content=formatted_content).send()


def format_for_display(data: dict) -> str:
    """Renders structured news data into an English Markdown UI"""
    output = f"## Search Analysis\n"
    output += f"- **Original Query**: {data.get('user_query', 'N/A')}\n"
    output += f"- **Search Keywords**: {data.get('agent_query', 'N/A')}\n\n"
    output += "---\n"

    articles = data.get("articles", [])
    if not articles:
        output += "_No relevant articles found for this topic._"
        return output

    for idx, article in enumerate(articles, 1):
        title = article.get("title", "Untitled")
        url = article.get("article_url", "#")
        sentiment = article.get("sentiment") or "Neutral"

        output += f"### {idx}. {title}\n"
        output += f"[Read Article]({url}) | Sentiment: **{sentiment}**\n\n"

        output += "**Key Summary:**\n"
        for point in article.get("key_summary", []):
            output += f"- {point}\n"

        if article.get("background"):
            output += f"\n> **Context**: {article['background']}\n"

        output += "\n---\n"

    return output
