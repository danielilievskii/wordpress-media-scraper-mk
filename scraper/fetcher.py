import asyncio
import logging
from typing import Dict, List, Optional
import aiohttp
from .config import (
    POSTS_PER_PAGE,
    REQUEST_TIMEOUT,
    MAX_CONCURRENT_REQUESTS,
    HEADERS
)

logger = logging.getLogger(__name__)


async def fetch_json(
    session: aiohttp.ClientSession,
    url: str,
    params: Optional[Dict] = None,
    max_retries: int = 5
) -> Optional[Dict]:
    """
    Fetch JSON data from a URL asynchronously with retry logic and rate-limit handling.

    :param session: aiohttp client session
    :param url: URL to fetch
    :param params: Query parameters
    :param max_retries: Maximum number of retry attempts
    :return: JSON response or None on error
    """
    for attempt in range(1, max_retries + 1):
        try:
            async with session.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT
            ) as response:

                if response.status == 429:
                    wait_time = int(response.headers.get("Retry-After", 2 ** attempt))
                    logger.warning(
                        "Rate limited. Waiting %d seconds (attempt %d/%d)",
                        wait_time, attempt, max_retries
                    )
                    await asyncio.sleep(wait_time)
                    continue

                response.raise_for_status()
                return await response.json()

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            wait_time = 2 ** attempt

            if attempt >= max_retries:
                logger.error("Request failed after %d attempts: %s", max_retries, url)
                return None

            logger.warning(
                "Request error on %s: %s — retrying in %d seconds (%d/%d)",
                url, e, wait_time, attempt, max_retries
            )
            await asyncio.sleep(wait_time)

        except Exception as e:
            logger.error("Unexpected error fetching %s: %s", url, e)
            return None

    return None



async def fetch_category_map(session: aiohttp.ClientSession, categories_url: str) -> Dict[int, str]:
    """
    Fetch categories and build a mapping of IDs to names.

    :param session: aiohttp client session
    :param categories_url: URL to fetch categories from
    :return: Dictionary mapping category IDs to names
    """
    category_map = {}

    try:
        params = {"per_page": 100}
        data = await fetch_json(session, categories_url, params)

        if data:
            for cat in data:
                category_map[cat['id']] = cat['name']
            logger.info("Fetched %d categories", len(category_map))
        else:
            logger.warning("Failed to fetch categories")
    except Exception as e:
        logger.error("Error building category map: %s", e)

    return category_map


async def fetch_total_pages(session: aiohttp.ClientSession, base_url: str) -> int:
    """
    Fetch the total number of pages available from the WordPress API.

    :param session: aiohttp client session
    :param base_url: Base URL for the posts endpoint
    :return: Total number of pages
    """
    try:
        params = {"per_page": POSTS_PER_PAGE}
        async with session.get(base_url, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT) as response:
            response.raise_for_status()
            total_pages = int(response.headers.get("X-WP-TotalPages", 1))
            logger.info("Total pages available: %d", total_pages)
            return total_pages

    except Exception as e:
        logger.error("Error fetching total pages: %s", e)
        return 1


async def fetch_page(session: aiohttp.ClientSession, base_url: str, page: int) -> Optional[List[Dict]]:
    """
    Fetch posts from a specific page of the WordPress API.

    :param session: aiohttp client session
    :param base_url: Base URL for the posts endpoint
    :param page: Page number to fetch
    :return: List of posts or None on error
    """
    params = {
        "per_page": POSTS_PER_PAGE,
        "page": page,
    }

    data = await fetch_json(session, base_url, params)

    if data:
        logger.info("Fetched page %d with %d posts", page, len(data))
        return data
    else:
        logger.warning("Failed to fetch page %d", page)
        return None


async def fetch_all_posts(
    session: aiohttp.ClientSession,
    base_url: str,
    total_pages: int,
    existing_ids: set = None
) -> List[Dict]:
    """
    Fetch all posts from all pages.

    - If is_first_run is True (no existing_ids provided), fetch all pages concurrently.
    - If is_first_run is False, fetch pages sequentially starting from page 1 and stop
      early when a page contains only already-scraped posts.

    :param session: aiohttp client session
    :param base_url: Base URL for the posts endpoint
    :param total_pages: Total number of pages to fetch
    :param existing_ids: Set of existing article IDs (optional)
    :return: List of newly fetched posts
    """
    all_posts = []
    is_first_run = not existing_ids

    if is_first_run:
        logger.info("First run detected - fetching all pages concurrently")
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

        async def fetch_with_semaphore(page: int):
            async with semaphore:
                return await fetch_page(session, base_url, page)

        tasks = [fetch_with_semaphore(page) for page in range(1, total_pages + 1)]

        completed = 0
        for coro in asyncio.as_completed(tasks):
            posts = await coro
            completed += 1

            if posts:
                all_posts.extend(posts)

            logger.info("Progress: %d/%d pages completed, %d total posts",
                        completed, total_pages, len(all_posts))

        return all_posts

    logger.info("Incremental run detected - fetching sequentially from page 1")

    for page in range(1, total_pages + 1):
        posts = await fetch_page(session, base_url, page)

        if not posts:
            logger.warning("No posts returned for page %d, stopping", page)
            break

        new_posts = [post for post in posts if post.get('id') not in existing_ids]
        duplicate_posts = [post for post in posts if post.get('id') in existing_ids]

        logger.info("Page %d: %d new posts, %d already scraped",
                    page, len(new_posts), len(duplicate_posts))

        all_posts.extend(new_posts)

        if not new_posts and duplicate_posts:
            logger.info("All posts on page %d already exist - stopping scraping", page)
            logger.info("Total pages fetched: %d/%d, total new posts: %d",
                        page, total_pages, len(all_posts))
            break

    return all_posts
