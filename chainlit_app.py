import asyncio
import logging

import chainlit as cl

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
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
from langchain_core.messages import AIMessage, ToolMessage
from news.allowed_sections import allowed_sections
from prompts.summarization_prompts import summarization_system_prompt

news_scheduler = None
cleanup_scheduler = None
_scheduler_initialized = settings.SCHEDULER_INITIALIZED


@cl.on_chat_start
async def start():
    asyncio.create_task(asyncio.to_thread(init_background_services))

    agent = create_agent(
        model=create_openai_llm(settings.OPENROUTER_MODEL_NAME),
        tools=[retrieve_news_from_vectorstore],
        system_prompt=summarization_system_prompt,
        response_format=ToolStrategy(
            NewsSummaryResponse, tool_message_content="Returning structured response:"
        ),
    )

    cl.user_session.set("agent", agent)
    cl.user_session.set("messages", [])

    await cl.Message(
        content="Hello! Let's see what's new in the world. What topic would you like to know about today?"
    ).send()


def _strip_tool_messages(messages: list) -> list:
    """Remove all tool call pairs (both retrieve_news and NewsSummaryResponse) from
    message history.

    Rationale: After each turn we only preserve HumanMessages and bare AIMessages
    (text-only, no tool_calls). This prevents the LLM from being confused by stale
    tool results when the user switches topics, while still giving the LLM enough
    context to handle detail-mode follow-ups (the prior text response is preserved
    in the AIMessage content if the LLM produced one, though with ToolStrategy the
    LLM typically only calls tools and does not emit a text turn).

    If the LLM emitted an AIMessage that has BOTH tool_calls and text content, we
    strip the tool_calls and keep only the text content so conversation context is
    maintained without confusing the routing logic.
    """
    # Collect all tool_call_ids so we can drop their paired ToolMessages.
    all_tool_call_ids: set[str] = set()
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                all_tool_call_ids.add(tc["id"])

    filtered = []
    for msg in messages:
        # Drop ToolMessages (responses to any tool call)
        if isinstance(msg, ToolMessage):
            continue
        # For AIMessages that contain tool_calls, keep only text content if present;
        # drop entirely if there is no text content (pure tool-call turn).
        if isinstance(msg, AIMessage) and msg.tool_calls:
            text_content = msg.content if isinstance(msg.content, str) else "".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in msg.content
            )
            if text_content.strip():
                # Preserve as a plain text AIMessage without tool_calls
                filtered.append(AIMessage(content=text_content))
            # else: pure tool-call turn with no text → drop entirely
            continue
        filtered.append(msg)
    return filtered


@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")
    messages = cl.user_session.get("messages")
    messages.append(HumanMessage(content=message.content))
    response = await cl.make_async(agent.invoke)({"messages": messages})
    cl.user_session.set("messages", _strip_tool_messages(response["messages"]))
    structured_response = response.get("structured_response")
    if structured_response is None:
        await cl.Message(content="I can only help with news queries. What topic would you like to know about?").send()
        return
    data_dict = structured_response.model_dump()
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


def init_background_services():
    global news_scheduler, cleanup_scheduler, _scheduler_initialized
    if not _scheduler_initialized:
        update_all_sections(allowed_sections)
        news_update_scheduler = create_news_update_scheduler(allowed_sections)
        news_update_scheduler.start()

        clear_expired_news()
        expired_news_cleanup_scheduler = create_expired_news_cleanup_scheduler()
        expired_news_cleanup_scheduler.start()

        _scheduler_initialized = True
