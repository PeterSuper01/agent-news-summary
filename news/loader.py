from abc import ABC, abstractmethod
from datetime import datetime

import requests
from langchain_core.documents import Document

from app.config import settings


class BaseNewsLoader(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    def _fetch(self, params: dict, **kwargs) -> dict:
        """Fetch raw news data from specific news API."""
        pass

    @abstractmethod
    def _transform(self, data: dict) -> list[Document]:
        """Transform raw news data to langchain documents."""
        pass

    def load(self, params: dict, **kwargs) -> list[Document]:
        """Load documents from specific news API."""
        data = self._fetch(params, **kwargs)
        return self._transform(data)


class TheGuardianLoader(BaseNewsLoader):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def _fetch(self, params: dict, section: str) -> dict:
        url = f"https://content.guardianapis.com/{section}"

        request_params = {"api-key": self.api_key, "show-fields": "bodyText, headline"}

        if params:
            request_params.update(params)
        response = requests.get(url, params=request_params)
        response.raise_for_status()
        data = response.json()
        return data

    def _transform(self, data: dict) -> list[str]:
        docs = []
        try:
            results = data.get("response", {}).get("results", [])
            for article in results:
                public_date = datetime.strptime(
                    article.get("webPublicationDate", ""), "%Y-%m-%dT%H:%M:%SZ"
                )
                content = Document(
                    page_content=article.get("fields", {}).get("bodyText", ""),
                    metadata={
                        "section": article.get("sectionId", ""),
                        "title": article.get("webTitle", ""),
                        "public_date": public_date.timestamp(),
                        "public_date_plain": public_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "article_url": article.get("webUrl", ""),
                    },
                )
                docs.append(content)
            return docs
        except Exception as e:
            print(f"Error transforming to langchain documents: {e}")
            return []

    def load(self, params: dict, section: str) -> list[Document]:
        data = self._fetch(params, section)
        return self._transform(data)


if __name__ == "__main__":
    loader = TheGuardianLoader(api_key=settings.THEGUARDIAN_API_KEY)
    docs = loader.load(params={"page-size": 2, "order-by": "newest"}, section="science")
    print(docs)
