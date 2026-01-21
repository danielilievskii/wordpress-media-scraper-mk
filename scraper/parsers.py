import logging
from bs4 import BeautifulSoup
from typing import Dict, List

logger = logging.getLogger(__name__)


def strip_html(raw_html: str) -> str:
    """
    Convert HTML content into plain text by removing tags and normalizing whitespace.

    :param raw_html: Raw HTML content
    :return: Plain text string
    """
    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())


def parse_post(post: Dict, category_map: Dict[int, str]) -> Dict:
    """
    Parse a WordPress post object into a structured article dictionary.

    :param post: Raw WordPress post data
    :param category_map: Mapping of category IDs to names
    :return: Parsed article dictionary
    """
    post_id = post.get("id")
    link = post.get("link")
    date = post.get("date")
    title = post.get("title", {}).get("rendered", "")
    content = strip_html(post.get("content", {}).get("rendered", ""))

    category_ids = post.get("categories", [])
    categories = [category_map.get(c_id, f"category_{c_id}") for c_id in category_ids]

    article = {
        "id": post_id,
        "link": link,
        "date": date,
        "title": title,
        "content": content,
        "categories": categories
    }

    return article


def parse_posts(posts: List[Dict], category_map: Dict[int, str]) -> List[Dict]:
    """
    Parse multiple WordPress posts into structured article dictionaries.

    :param posts: List of raw WordPress post data
    :param category_map: Mapping of category IDs to names
    :return: List of parsed article dictionaries
    """
    articles = []

    for post in posts:
        try:
            article = parse_post(post, category_map)
            articles.append(article)
        except Exception as e:
            logger.error("Error parsing post %s: %s", post.get("id"), e)
            continue

    logger.info("Parsed %d articles", len(articles))
    return articles