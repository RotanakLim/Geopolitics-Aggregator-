"""
Geopolitics News Aggregator — Starter Skeleton
------------------------------------------------
This is scaffolding, not a finished app. Fill in the TODOs.

Design:
  - Source: a news outlet (RSS or API), with a bias rating you supply
    from a transparent third-party source (AllSides, Ad Fontes Media).
  - Article: a normalized news item pulled from a Source.
  - fetch_source(): pulls + normalizes raw feed data into Article objects.
  - is_geopolitics(): filters for world/politics content.
  - build_digest(): groups today's articles, e.g. by bias label, for delivery.

Suggested libraries:
  pip install feedparser requests apscheduler
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import sqlite3

# ---------------------------------------------------------------------------
# 1. Data model
# ---------------------------------------------------------------------------

@dataclass
class Source:
    name: str                  # e.g. "The Guardian"
    country: str                # e.g. "UK"
    feed_url: str                # RSS URL or API endpoint
    bias_label: str              # e.g. "Center", "Lean Left" — from AllSides/Ad Fontes
    bias_rating_source: str      # citation for where the label came from
    fetch_type: str = "rss"      # "rss" or "api" rss = Really Simple Syndication


@dataclass
class Article:
    title: str
    url: str
    summary: str
    source_name: str
    source_country: str
    bias_label: str
    published_at: datetime
    topic_tags: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 2. Source registry
# ---------------------------------------------------------------------------
# TODO: Fill in real feed URLs and confirm bias labels against AllSides
# (https://www.allsides.com/media-bias/ratings) or Ad Fontes Media
# (https://adfontesmedia.com/) before shipping. Don't hardcode a label
# without a citation — that's exactly the kind of unsourced bias claim
# this project is trying to avoid.

SOURCES: list[Source] = [
    Source(
        name = "The Guardian",
        country = "UK",
        feed_url = "https://www.theguardian.com/world/rss",
        bias_label = "Far Left",
        bias_rating_source = "https://www.allsides.com/news-source/guardian-media-bias",
    ),
    Source(
        name = "Al Jazeera",
        country = "Qatar",
        feed_url = "https://www.aljazeera.com/xml/rss/all.xml",
        bias_label = "Lean Left",
        bias_rating_source = "https://www.allsides.com/news-source/al-jazeera-media-bias",
    ),
    Source(
        name = "Deutsche Welle (DW)",
        country = "Germany",
        feed_url = "https://rss.dw.com/rdf/rss-en-world",
        bias_label = "Center",
        bias_rating_source = "https://www.allsides.com/news-source/deutsche-welle-media-bias",
    ),
    Source(
        name = "Cable News Network (CNN)",
        country = "USA",
        feed_url = "https://rss.app/r/feed/5KS3LEsH41ez1jdV",
        bias_label = "Far Left",
        bias_rating_source = "https://www.allsides.com/news-source/cnn-opinion-media-bias",
    ),
    Source(
        name = "Fox News",
        country = "USA",
        feed_url = "", #comeback to this
        bias_label = "Far Right",
        bias_rating_source = "https://www.allsides.com/news-source/fox-news-media-bias",
    ),
    Source(
        name = "British Broadcasting Corporation (BBC)",
        country  = "England",
        feed_url = "", # comeback to this
        bias_label = "Center"
        bias_rating_source = "https://www.allsides.com/news-source/bbc-news-media-bias"
    )

    # TODO: add AFP (via a licensed aggregator/API — AFP does not run a
    # simple public RSS feed the way Guardian/DW do), Reuters, NHK World, etc.
]


# ---------------------------------------------------------------------------
# 3. Fetch / ingest layer
# ---------------------------------------------------------------------------

def fetch_source(source: Source) -> list[Article]:
    """
    Pull raw items from `source` and normalize into Article objects.
    TODO:
      - if source.fetch_type == "rss": use feedparser.parse(source.feed_url)
      - if source.fetch_type == "api": requests.get(...) with your API key
      - map each raw entry into an Article, filling bias_label from `source`
    """
    raise NotImplementedError


def fetch_all_sources(sources: list[Source]) -> list[Article]:
    """Loop over SOURCES, call fetch_source, collect + dedupe by url."""
    articles: list[Article] = []
    for source in sources:
        try:
            articles.extend(fetch_source(source))
        except NotImplementedError:
            continue
        # TODO: real error handling (network failures, malformed feeds, etc.)
    return _dedupe_by_url(articles)


def _dedupe_by_url(articles: list[Article]) -> list[Article]:
    seen = set()
    unique = []
    for a in articles:
        if a.url not in seen:
            seen.add(a.url)
            unique.append(a)
    return unique


# ---------------------------------------------------------------------------
# 4. Geopolitics filter
# ---------------------------------------------------------------------------

GEOPOLITICS_KEYWORDS = [
    "summit", "sanctions", "treaty", "election", "coup", "ceasefire",
    "diplomacy", "border dispute", "united nations", "nato", "eu",
    # TODO: expand / tune this list, or prefer section-tag filtering
    # if the feed already provides categories like "world" or "politics"
]


def is_geopolitics(article: Article) -> bool:
    """
    TODO: prefer the source's own section/category tag when available.
    Fall back to keyword matching in title/summary only if needed.
    """
    text = f"{article.title} {article.summary}".lower()
    return any(keyword in text for keyword in GEOPOLITICS_KEYWORDS)


# ---------------------------------------------------------------------------
# 5. Storage
# ---------------------------------------------------------------------------

def init_db(path: str = "news.db") -> sqlite3.Connection:
    """
    TODO: create an `articles` table (url as PRIMARY KEY to prevent
    re-notifying on stories you've already seen) and a `sources` table.
    """
    conn = sqlite3.connect(path)
    # conn.execute("CREATE TABLE IF NOT EXISTS articles (...)")
    return conn


def save_articles(conn: sqlite3.Connection, articles: list[Article]) -> None:
    """TODO: INSERT OR IGNORE each article into the db."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 6. Digest builder
# ---------------------------------------------------------------------------

def build_digest(articles: list[Article]) -> dict[str, list[Article]]:
    """
    Group today's articles by bias_label so a digest can show multiple
    perspectives on the same story rather than a single flat feed.
    TODO: also consider grouping by topic/region.
    """
    digest: dict[str, list[Article]] = {}
    for article in articles:
        digest.setdefault(article.bias_label, []).append(article)
    return digest


# ---------------------------------------------------------------------------
# 7. Delivery (pick one to start)
# ---------------------------------------------------------------------------

def send_email_digest(digest: dict[str, list[Article]], to_address: str) -> None:
    """TODO: render digest to HTML/markdown and send via smtplib."""
    raise NotImplementedError


def render_digest_markdown(digest: dict[str, list[Article]]) -> str:
    """TODO: turn the digest dict into a readable markdown string."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 8. Scheduling entry point
# ---------------------------------------------------------------------------

def run_daily_job() -> None:
    """
    TODO: wire this into APScheduler (or a cron job calling this script)
    to run once a day.
    """
    conn = init_db()
    articles = fetch_all_sources(SOURCES)
    geo_articles = [a for a in articles if is_geopolitics(a)]
    save_articles(conn, geo_articles)
    digest = build_digest(geo_articles)
    # send_email_digest(digest, "you@example.com")


if __name__ == "__main__":
    run_daily_job()