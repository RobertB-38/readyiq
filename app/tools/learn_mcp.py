"""Microsoft Learn MCP tool — live, official documentation grounding.

ReadyIQ's Curator step calls the public Microsoft Learn MCP server
(https://learn.microsoft.com/api/mcp, Streamable HTTP) to fetch live, official
study content for a candidate's weak area. This grounds the recommended next
step in real Microsoft Learn material instead of static text.

Public documentation only — no personal/learner data, no PII.
Returns [] on any failure so the demo never breaks.
"""
from __future__ import annotations

import asyncio
import json
from typing import Dict, List

ENDPOINT = "https://learn.microsoft.com/api/mcp"


async def _search(query: str, k: int) -> List[Dict]:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    async with streamablehttp_client(ENDPOINT) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "microsoft_docs_search", {"query": query}
            )

    text = "".join(getattr(c, "text", "") or "" for c in result.content)
    items: List[Dict] = []
    try:
        data = json.loads(text)
        rows = data if isinstance(data, list) else data.get("results", [])
        for d in rows[:k]:
            items.append({
                "title": d.get("title") or d.get("name") or "Microsoft Learn",
                "url": d.get("contentUrl") or d.get("url") or "",
                "excerpt": (d.get("content") or d.get("excerpt") or "")[:300],
            })
    except (ValueError, AttributeError):
        if text.strip():
            items.append({"title": "Microsoft Learn", "url": "", "excerpt": text[:300]})
    return items[:k]


def search_learn(query: str, k: int = 3) -> List[Dict]:
    """Live Microsoft Learn docs search via the official MCP server.

    Returns a list of {title, url, excerpt}. Degrades to [] on any error
    (no network, MCP unavailable) so it never breaks the readiness demo.
    """
    try:
        return asyncio.run(_search(query, k))
    except Exception:
        return []
