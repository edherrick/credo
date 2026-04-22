"""Scrape politician stances from campaign websites and Wikipedia, insert as entity_events.

Events are inserted with reviewed=False — run the SQL below to approve them:

    UPDATE entity_events SET reviewed = true
    WHERE reviewed = false AND source_type IN ('government', 'wikipedia');

Usage (from backend/ directory):
    python scripts/scrape_politician_stances.py           # raw text, no summarisation
    ANTHROPIC_API_KEY=sk-... python scripts/scrape_politician_stances.py  # Claude summaries
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

import httpx
from bs4 import BeautifulSoup
import anthropic
from anthropic.types import TextBlock

POLITICIANS = [
    {
        "slug": "brandon-johnson",
        "sources": [
            {
                "url": "https://www.brandonforchicago.com/on-the-issues",
                "source_type": "government",
            },
            {
                "url": (
                    "https://en.wikipedia.org/w/api.php"
                    "?action=query&titles=Brandon_Johnson&prop=extracts&explaintext=1&format=json"
                ),
                "source_type": "wikipedia",
            },
        ],
    },
]

# Wikipedia subsections to extract for Brandon Johnson
WIKIPEDIA_POLICY_SECTIONS = {
    "One Fair Wage",
    "Housing and Bring Chicago Home",
    'Housing and "Bring Chicago Home"',
    "Chicago Public Schools",
    "Blocked economic efforts",
    "Other matters",
}

HEADERS = {
    "User-Agent": "CredoApp/0.1 (mailto:contact@credoapp.org; research project)",
}


# ── Extractors ────────────────────────────────────────────────────────────────

def extract_campaign_sections(html: str) -> list[dict[str, str]]:
    """Extract stances from a Webflow FAQ accordion campaign site."""
    soup = BeautifulSoup(html, "html.parser")
    sections = []
    for accordion in soup.find_all("div", class_="faq2_accordion"):
        h1 = accordion.find("h1")
        if not h1:
            continue
        title = h1.get_text(strip=True)
        if not title or len(title) < 3:
            continue
        question_div = accordion.find("div", class_="faq2_question")
        body_parts = []
        for child in accordion.children:
            if child == question_div:
                continue
            if hasattr(child, "get_text"):
                text = child.get_text(" ", strip=True)
                if text:
                    body_parts.append(text)
        body = " ".join(body_parts).strip()
        if body:
            sections.append({"topic": title, "raw_text": body})
    return sections


def extract_wikipedia_sections(data: dict) -> list[dict[str, str]]:
    """Parse policy subsections from Wikipedia plain-text extract."""
    pages = data.get("query", {}).get("pages", {})
    text = next(iter(pages.values()), {}).get("extract", "")
    if not text:
        return []

    sections = []
    current_title = None
    current_body: list[str] = []

    for line in text.splitlines():
        if line.startswith("=== ") and line.endswith(" ==="):
            if current_title and current_body:
                sections.append({"topic": current_title, "raw_text": " ".join(current_body)})
            title = line.strip("= ").strip()
            current_title = title if title in WIKIPEDIA_POLICY_SECTIONS else None
            current_body = []
        elif line.startswith("== ") and line.endswith(" =="):
            if current_title and current_body:
                sections.append({"topic": current_title, "raw_text": " ".join(current_body)})
            current_title = None
            current_body = []
        elif current_title and line.strip():
            current_body.append(line.strip())

    if current_title and current_body:
        sections.append({"topic": current_title, "raw_text": " ".join(current_body)})

    return sections


# ── Summarisation ─────────────────────────────────────────────────────────────

def summarise_stances(sections: list[dict[str, str]]) -> list[dict[str, str]]:
    """Use Claude to produce clean one-sentence summaries of each stance."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = (
        "You are extracting policy stances from a politician's sources. "
        "For each stance section below, produce a concise one-sentence summary (max 30 words) "
        "that captures the core position. Return a JSON array with objects: "
        '{"topic": "...", "summary": "..."}. '
        "Return ONLY valid JSON — no markdown, no explanation.\n\n"
        "Stances:\n"
        + json.dumps(sections, indent=2)
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = ""
    for block in message.content:
        if isinstance(block, TextBlock):
            raw = block.text.strip()
            break
    return json.loads(raw)


# ── Database ──────────────────────────────────────────────────────────────────

async def insert_stances(
    slug: str,
    source_url: str,
    source_type: str,
    stances: list[dict[str, str]],
) -> None:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with session_maker() as session:
        row = await session.execute(
            text("SELECT id FROM entities WHERE slug = :slug"),
            {"slug": slug},
        )
        entity_id = row.scalar_one_or_none()
        if not entity_id:
            print(f"  ERROR: entity '{slug}' not found — run seed_politicians.py first")
            await engine.dispose()
            return

        for stance in stances:
            await session.execute(
                text("""
                    INSERT INTO entity_events
                        (entity_id, title, description, source_url, source_type, confidence, reviewed)
                    VALUES
                        (:entity_id, :title, :description, :source_url, :source_type, 0.85, false)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "entity_id": entity_id,
                    "title": stance["topic"],
                    "description": stance["summary"],
                    "source_url": source_url,
                    "source_type": source_type,
                },
            )

        await session.commit()
        print(f"  Inserted {len(stances)} stance(s) (reviewed=false).")

    await engine.dispose()


# ── Scraping ──────────────────────────────────────────────────────────────────

async def scrape_source(
    slug: str,
    url: str,
    source_type: str,
    client: httpx.AsyncClient,
) -> None:
    print(f"  [{source_type}] {url}")
    response = await client.get(url, headers=HEADERS)
    response.raise_for_status()

    if source_type == "government":
        sections = extract_campaign_sections(response.text)
    elif source_type == "wikipedia":
        sections = extract_wikipedia_sections(response.json())
    else:
        print(f"  WARNING: unknown source_type '{source_type}', skipping")
        return

    if not sections:
        print(f"  WARNING: no sections extracted from {url}")
        return

    if os.environ.get("ANTHROPIC_API_KEY"):
        print(f"  Found {len(sections)} section(s) — summarising with Claude…")
        stances = summarise_stances(sections)
    else:
        print(f"  Found {len(sections)} section(s) — inserting raw text (no API key)…")
        stances = [
            {"topic": s["topic"], "summary": s["raw_text"][:500]}
            for s in sections
        ]
    await insert_stances(slug, url, source_type, stances)


async def main() -> None:
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for politician in POLITICIANS:
            print(f"\nScraping {politician['slug']}…")
            for source in politician["sources"]:
                await scrape_source(
                    politician["slug"],
                    source["url"],
                    source["source_type"],
                    client,
                )

    print("\nDone. To make stances visible, run:")
    print("  UPDATE entity_events SET reviewed = true")
    print("  WHERE reviewed = false AND source_type IN ('government', 'wikipedia');")


if __name__ == "__main__":
    asyncio.run(main())
