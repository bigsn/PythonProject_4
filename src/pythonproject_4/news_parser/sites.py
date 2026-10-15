"""Site-specific news parsers with registry."""

from typing import Dict, Optional, List
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

from pythonproject_4.news_parser.base import BaseParser, ParsedNews


def get_parser_for_url(url: str) -> Optional[BaseParser]:
    """Select parser by URL domain."""
    parsed = urlparse(url)
    domain = parsed.hostname or ""
    # Try full domain, then TLD+1
    for key in [domain, ".".join(domain.split(".")[-2:])]:
        if key in PARSER_REGISTRY:
            return PARSER_REGISTRY[key]()
    return None

class HabrParser(BaseParser):
    """Parser for Habr.com news feed."""

    def parse(self, source_url: str) -> List[ParsedNews]:
        url = 'https://habr.com/ru/rss/news/'
        results = []
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        items = BeautifulSoup(response.content, 'xml').find_all('item')[:10]
        for item in items:
            title = item.title.text
            url = item.guid.text
            author = item.creator.text
            
            # Extract image safely
            img = ""
            try:
                soup = BeautifulSoup(item.description.text, "html.parser")
                img_tag = soup.find('img')
                if img_tag:
                    img = img_tag.get('src', '')
            except Exception:
                pass

            response = requests.get(item.guid.text)
            if response.status_code == 200:
                if response:
                    post = BeautifulSoup(response.content, 'lxml')
                    post_txt = post.find('div', class_='article-body').text

            published_at = item.pubDate.text
            results.append(ParsedNews(title=title,
                                      raw_text=post_txt,
                                      url=url,
                                      img_url=img,
                                      author=author,
                                      published_at=published_at))
        return results


# Registry: domain -> parser class
PARSER_REGISTRY: Dict[str, type] = {"habr.com": HabrParser}