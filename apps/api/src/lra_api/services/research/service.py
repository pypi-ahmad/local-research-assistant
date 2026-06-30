"""Research analysis generation service."""

from __future__ import annotations

from lra_api.services.ollama.client import OllamaClient


class ResearchService:
    """Service for summaries, comparisons, and insight extraction."""

    async def summarize(self, text: str, mode: str) -> str:
        """Generate summary from input text."""
        prompt = (
            f"Create {mode} summary with headings, key points, limitations, and citations placeholder markers."
            f"\n\nText:\n{text[:16000]}"
        )
        client = OllamaClient()
        response = await client.generate(prompt, task="summary")
        await client.close()
        return response.get("response", "")

    async def compare(self, text_a: str, text_b: str) -> str:
        """Generate structured comparison and contradiction analysis."""
        prompt = (
            "Compare two sources. Return: agreements, contradictions, evidence confidence, action items."
            f"\n\nSource A:\n{text_a[:12000]}\n\nSource B:\n{text_b[:12000]}"
        )
        client = OllamaClient()
        response = await client.generate(prompt, task="chat")
        await client.close()
        return response.get("response", "")

    async def timeline(self, text: str) -> str:
        """Generate timeline from source text."""
        prompt = f"Extract chronological timeline with date, event, source quote.\n\n{text[:16000]}"
        client = OllamaClient()
        response = await client.generate(prompt, task="summary")
        await client.close()
        return response.get("response", "")

    async def glossary(self, text: str) -> str:
        """Generate glossary from source text."""
        prompt = f"Extract glossary: term, definition, why it matters.\n\n{text[:16000]}"
        client = OllamaClient()
        response = await client.generate(prompt, task="summary")
        await client.close()
        return response.get("response", "")

    async def entities(self, text: str) -> str:
        """Generate entity and relationship extraction report."""
        prompt = (
            "Extract people, organizations, locations, concepts, events, and relationships in JSON."
            f"\n\n{text[:16000]}"
        )
        client = OllamaClient()
        response = await client.generate(prompt, task="chat")
        await client.close()
        return response.get("response", "")
