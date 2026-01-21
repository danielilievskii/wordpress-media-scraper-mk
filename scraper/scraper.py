import logging
import os
import aiohttp
from .fetcher import fetch_category_map, fetch_total_pages, fetch_all_posts
from .parsers import parse_posts
from .data_utils import get_scraped_article_ids, append_new_articles, filter_new_articles
from .config import (
    BASE_URL_TEMPLATE,
    CATEGORIES_URL_TEMPLATE,
    DATA_DIR,
    DATASET_FILENAME_TEMPLATE
)

logger = logging.getLogger(__name__)


async def scrape_site(site: str):
    """
    Scrape a single WordPress site.

    :param site: Domain name of the site to scrape
    """
    logger.info("=" * 80)
    logger.info("Starting scraper for %s", site)
    logger.info("=" * 80)

    base_url = BASE_URL_TEMPLATE.format(site)
    categories_url = CATEGORIES_URL_TEMPLATE.format(site)

    site_name = site.replace(".", "_")
    dataset_path = os.path.join(DATA_DIR, DATASET_FILENAME_TEMPLATE.format(site_name))

    existing_ids = get_scraped_article_ids(dataset_path)
    logger.info("Loaded %d existing article IDs for %s", len(existing_ids), site)

    async with aiohttp.ClientSession() as session:
        logger.info("Fetching categories for %s...", site)
        category_map = await fetch_category_map(session, categories_url)

        logger.info("Determining total pages for %s...", site)
        total_pages = await fetch_total_pages(session, base_url)

        logger.info("Fetching all posts from %s...", site)
        all_posts = await fetch_all_posts(session, base_url, total_pages, existing_ids)
        logger.info("Fetched %d total posts from %s", len(all_posts), site)

        logger.info("Parsing posts from %s...", site)
        articles = parse_posts(all_posts, category_map)

        new_articles = filter_new_articles(articles, existing_ids)

        if new_articles:
            logger.info("Saving %d new articles from %s...", len(new_articles), site)
            append_new_articles(new_articles, dataset_path)
            logger.info("Successfully saved new articles from %s!", site)
        else:
            logger.info("No new articles to save from %s.", site)

    final_count = len(get_scraped_article_ids(dataset_path))
    logger.info("=" * 80)
    logger.info("COMPLETED %s - Total articles in dataset: %d", site, final_count)
    logger.info("=" * 80)
    logger.info("")