from typing import List, Optional
from pydantic import BaseModel, Field


class NewsSummary(BaseModel):
    title: str = Field(
        description="The headline and publication date of the news article, e.g. 'Trump to visit Japan next week'(yyyy-mm-dd)"
    )
    article_url: str = Field(description="The URL of the news article")
    summary_type: str = Field(
        description="The type of summary: 'brief' or 'detailed', default is 'brief'"
    )

    # Brief summary
    key_summary: List[str] = Field(
        description="A list of important facts from the article"
    )

    # Detailed summary
    background: Optional[str] = Field(
        None, description="Detailed background or historical context"
    )
    key_figures: Optional[List[str]] = Field(
        None, description="List of important figures or organizations involved"
    )
    future_impact: Optional[str] = Field(
        None, description="Potential future consequences or developments"
    )

    entities: Optional[str] = Field(
        None, description="Key people, organizations, or locations mentioned"
    )
    sentiment: Optional[str] = Field(
        None,
        description="The overall tone of the article (e.g., Neutral, Positive, Negative)",
    )


class NewsSummaryResponse(BaseModel):
    user_query: str = Field(description="The user's original search query")
    agent_query: str = Field(
        description="The query used by the agent to retrieve the news articles"
    )
    articles: List[NewsSummary] = Field(description="List of processed news articles")
