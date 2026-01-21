import json
import os
import logging
from typing import Dict, List, Set
from datetime import datetime

logger = logging.getLogger(__name__)


def get_scraped_articles(path: str) -> List[Dict]:
    """
    Load and return a list of scraped articles from a JSON dataset file.

    :param path: Path to the dataset file
    :return: List of articles, each represented as a dictionary
    """
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            logger.info("Loaded existing dataset from %s", path)
            return json.load(f)

    logger.info("No existing dataset found at %s", path)
    return []


def get_scraped_article_ids(path: str) -> Set[int]:
    """
    Build a set of previously scraped article IDs to avoid duplicates.

    :param path: Path to the dataset file
    :return: Set of article IDs
    """
    scraped_articles = get_scraped_articles(path)
    article_ids = {article["id"] for article in scraped_articles if "id" in article}

    logger.info("Loaded %d previously scraped article IDs", len(article_ids))
    return article_ids


def save_articles(articles: List[Dict], path: str) -> None:
    """
    Save articles to the dataset file, replacing existing content.
    Articles are sorted by date before saving. If any date cannot be parsed,
    the articles are saved in their original order without sorting.

    :param articles: List of articles to save
    :param path: Path to the dataset file
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    try:
        articles_sorted = sorted(
            articles,
            key=lambda x: datetime.fromisoformat(x["date"]) if "date" in x else datetime.min
        )
    except Exception as e:
        logger.warning("Date parsing failed (%s). Saving without sorting.", e)
        articles_sorted = articles

    with open(path, "w", encoding="utf-8") as f:
        json.dump(articles_sorted, f, ensure_ascii=False, indent=4)

    logger.info("Saved %d articles to %s", len(articles_sorted), path)



def append_new_articles(new_articles: List[Dict], path: str) -> None:
    """
    Save new articles to the dataset file, appending to existing entries if present.

    :param new_articles: List of new articles to save
    :param path: Path to the dataset file
    """
    scraped_articles = get_scraped_articles(path)
    scraped_articles.extend(new_articles)

    save_articles(scraped_articles, path)
    logger.info("Appended %d new articles", len(new_articles))


def filter_new_articles(articles: List[Dict], existing_ids: set) -> List[Dict]:
    """
    Filter out articles that have already been scraped.

    :param articles: List of all articles
    :param existing_ids: Set of existing article IDs
    :return: List of new articles only
    """
    new_articles = [article for article in articles if article["id"] not in existing_ids]
    logger.info("Found %d new articles out of %d total", len(new_articles), len(articles))
    return new_articles