"""Site-specific news parsers with registry."""

from typing import Dict, Optional, List
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

from pythonproject_4.news_parser.base import BaseParser, ParsedNews


# Registry: domain -> parser class
PARSER_REGISTRY: Dict[str, type] = {}


def register_parser(domain: str):
    """Decorator to register a site parser by domain."""
    def decorator(cls):
        PARSER_REGISTRY[domain] = cls
        return cls
    return decorator


def get_parser_for_url(url: str) -> Optional[BaseParser]:
    """Select parser by URL domain."""
    parsed = urlparse(url)
    domain = parsed.hostname or ""
    # Try full domain, then TLD+1
    for key in [domain, ".".join(domain.split(".")[-2:])]:
        if key in PARSER_REGISTRY:
            return PARSER_REGISTRY[key]()
    return None


class GenericSiteParser(BaseParser):
    """Generic HTML news parser as fallback for supported sites."""

    def parse(self, source_url: str) -> List[ParsedNews]:
        response = requests.get(source_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        # Generic extraction: look for article containers
        articles = soup.select("article, .post, .news-item, .article")
        if not articles:
            # Fallback: try body text
            body = soup.find("body")
            if body:
                text = body.get_text(strip=True)
                if text:
                    title = soup.title.string if soup.title else "Untitled"
                    return [ParsedNews(
                        title=title[:200],
                        raw_text=text[:5000],
                        url=source_url,
                    )]
            return []

        results = []
        for article in articles:
            title_el = article.select_one("h1, h2, h3, .title, .headline")
            title = title_el.get_text(strip=True) if title_el else ""

            content_el = article.select_one(".content, .body, .text, p")
            raw_text = content_el.get_text(strip=True) if content_el else ""

            if not raw_text:
                continue

            # Try to get absolute URL
            link_el = article.select_one("a[href]")
            url = None
            if link_el:
                href = link_el["href"]
                if href.startswith("http"):
                    url = href
                else:
                    url = urljoin(source_url, href)

            if url is None:
                continue  # Skip articles without URL

            results.append(ParsedNews(
                title=title or raw_text[:200].strip(),
                raw_text=raw_text,
                url=url,
            ))

        return results


@register_parser("habr.com")
class HabrParser(BaseParser):
    """Parser for Habr.com news feed."""

    def parse(self, source_url: str) -> List[ParsedNews]:
        response = requests.get(source_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        results = []
        # Habr feed structure
        items = soup.select("div.post__title a, .feed-item__title a")
        for item in items:
            title = item.get_text(strip=True)
            href = item.get("href", "")
            if href.startswith("//"):
                href = "https:" + href

            # Get parent article for text
            article = item.find_parent(["div", "article"])
            if article:
                text_el = article.select_one(".post__text, .p_text, .article__content")
                raw_text = text_el.get_text(strip=True) if text_el else ""
            else:
                raw_text = ""

            if not raw_text:
                continue

            results.append(ParsedNews(
                title=title,
                raw_text=raw_text,
                url=href if href.startswith("http") else None,
            ))

        return results
