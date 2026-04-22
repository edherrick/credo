"""Quick test: scrape both campaign site and Wikipedia for Brandon Johnson.
No DB writes, no Claude — just prints what would be extracted.

Usage (from backend/ directory):
    python scripts/test_scrape.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from bs4 import BeautifulSoup

WIKIPEDIA_API = (
    "https://en.wikipedia.org/w/api.php"
    "?action=query&titles=Brandon_Johnson&prop=extracts&explaintext=1&format=json"
)
CAMPAIGN_URL = "https://www.brandonforchicago.com/on-the-issues"

POLICY_SECTIONS = {
    "One Fair Wage",
    "Housing and Bring Chicago Home",
    'Housing and "Bring Chicago Home"',
    "Chicago Public Schools",
    "Blocked economic efforts",
    "Other matters",
}


def extract_wikipedia_sections(data: dict) -> list[dict[str, str]]:
    """Parse policy subsections from Wikipedia plain-text extract.

    The extract uses === heading === markers to delimit sections.
    """
    pages = data.get("query", {}).get("pages", {})
    text = next(iter(pages.values()), {}).get("extract", "")
    if not text:
        return []

    sections = []
    current_title = None
    current_body: list[str] = []

    for line in text.splitlines():
        # === subsection === (h3)
        if line.startswith("=== ") and line.endswith(" ==="):
            if current_title and current_body:
                sections.append({"topic": current_title, "raw_text": " ".join(current_body)})
            title = line.strip("= ").strip()
            if title in POLICY_SECTIONS:
                current_title = title
                current_body = []
            else:
                current_title = None
                current_body = []
        # == section == (h2) — reset subsection tracking
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


def extract_campaign_sections(html: str) -> list[dict[str, str]]:
    """Extract sections from campaign issues page.

    The site uses a Webflow FAQ accordion pattern:
      div.faq2_accordion
        div.faq2_question > h1.text-color-blue  ← topic title
        div (answer body)                        ← stance text
    """
    soup = BeautifulSoup(html, "html.parser")
    sections = []

    for accordion in soup.find_all("div", class_="faq2_accordion"):
        h1 = accordion.find("h1")
        if not h1:
            continue
        title = h1.get_text(strip=True)
        if not title or len(title) < 3:
            continue

        # Body is all text in the accordion outside the question div
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


async def main() -> None:
    headers = {
        "User-Agent": "CredoApp/0.1 (https://github.com/ed/credo; research project)",
    }
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        wiki_resp, campaign_resp = await asyncio.gather(
            client.get(WIKIPEDIA_API, headers=headers, params=None),
            client.get(CAMPAIGN_URL),
        )

    # Wikipedia
    print(f"\n{'='*60}")
    print(f"  Wikipedia (via REST API)")
    print(f"{'='*60}")
    if wiki_resp.status_code == 200:
        sections = extract_wikipedia_sections(wiki_resp.json())
        for s in sections:
            print(f"\n  [{s['topic']}]")
            print(f"  {s['raw_text'][:200]}{'...' if len(s['raw_text']) > 200 else ''}")
        print(f"\n  → {len(sections)} section(s) extracted")
    else:
        print(f"  ERROR: HTTP {wiki_resp.status_code}")

    # Campaign site
    print(f"\n{'='*60}")
    print(f"  Campaign site: {CAMPAIGN_URL}")
    print(f"{'='*60}")
    sections = extract_campaign_sections(campaign_resp.text)
    for s in sections:
        print(f"\n  [{s['topic']}]")
        print(f"  {s['raw_text'][:200]}{'...' if len(s['raw_text']) > 200 else ''}")
    print(f"\n  → {len(sections)} section(s) extracted")


if __name__ == "__main__":
    asyncio.run(main())
