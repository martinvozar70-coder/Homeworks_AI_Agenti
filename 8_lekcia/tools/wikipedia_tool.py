"""
Wikipedia Tool
==============
Allows the agent to search Wikipedia and retrieve article summaries.
This tool requires no API key — it uses the free Wikipedia API.

Requirements:
    pip install wikipedia-api
"""

import wikipediaapi
from tools.base_tool import BaseTool


class WikipediaTool(BaseTool):

    def __init__(self, language: str = "en"):
        self.wiki = wikipediaapi.Wikipedia(
            language=language,
            user_agent="AI-Agent-Homework/1.0 (educational project)"
        )

    @property
    def name(self) -> str:
        return "wikipedia_search"

    @property
    def description(self) -> str:
        return (
            "Search Wikipedia for information about a topic. "
            "Returns a summary of the Wikipedia article. "
            "Use this for general knowledge questions, definitions, historical facts, etc."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "topic": "string — the topic or entity to search for on Wikipedia"
        }

    def run(self, inputs: dict) -> str:
        topic = inputs.get("topic", "").strip()

        if not topic:
            return "Error: No topic provided."

        page = self.wiki.page(topic)

        if not page.exists():
            # Try a simple variation
            return f"No Wikipedia article found for '{topic}'. Try a different search term."

        # Return first ~1000 characters of summary (enough for context)
        summary = page.summary
        if len(summary) > 1500:
            summary = summary[:1500] + "..."

        return f"Wikipedia: {page.title}\n\n{summary}\n\nURL: {page.fullurl}"
