from enum import Enum

import requests
from pydantic import BaseModel, Field

from app.config import settings


def get_allowed_sections_from_the_guardian() -> list[str]:
    url = settings.THEGUARDIAN_SECTION_URL
    api_key = settings.THEGUARDIAN_API_KEY
    response = requests.get(url, params={"api-key": api_key})
    response.raise_for_status()
    results = response.json()["response"]["results"]
    allowd_section_list = [result["id"] for result in results]
    sections_to_remove = [
        "about",
        "better-business",
        "community",
        "crosswords",
        "culture-network",
        "enterprise-network",
        "info",
        "jobadvice",
        "leeds",
        "membership",
        "society-professionals",
        "theguardian",
        "travel/offers",
        "us-wellness",
    ]
    allowd_section_list = [
        section for section in allowd_section_list if section not in sections_to_remove
    ]
    return allowd_section_list


allowed_sections = get_allowed_sections_from_the_guardian()

DynamicSection = Enum(
    "DynamicSection", {k.upper(): k for k in allowed_sections}, type=str
)


class AllowedSectionInput(BaseModel):
    section_input: DynamicSection = Field(
        description="Allowed section on The Guardian news website",
        default=DynamicSection.WORLD,
    )


class AllowedQueryInput(BaseModel):
    query: str = Field(
        description="The query to search the news",
        default="",
    )
    section_input: DynamicSection = Field(
        description="Allowed section on The Guardian news website",
        default=DynamicSection.WORLD,
    )


if __name__ == "__main__":
    print(get_allowed_sections_from_the_guardian())
