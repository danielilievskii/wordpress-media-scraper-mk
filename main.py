import asyncio
import logging
from scraper.config import LOG_LEVEL, LOG_FORMAT, SITES
from scraper.scraper import scrape_site

logger = logging.getLogger(__name__)


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
    )


async def main():
    """Entry point for the scraper - scrapes all sites sequentially."""
    setup_logging()

    logger.info("Starting multi-site scraper")
    logger.info("Total sites to scrape: %d", len(SITES))
    logger.info("")

    successful = 0
    failed = []

    for idx, site in enumerate(SITES, 1):
        logger.info("Processing site %d/%d: %s", idx, len(SITES), site)

        try:
            await scrape_site(site)
            successful += 1
        except KeyboardInterrupt:
            logger.warning("Scraping interrupted by user at site: %s", site)
            raise
        except Exception as e:
            logger.error("Failed to scrape %s: %s", site, e, exc_info=True)
            failed.append(site)
            continue

    # Final summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("SCRAPING COMPLETED")
    logger.info("=" * 80)
    logger.info("Successfully scraped: %d/%d sites", successful, len(SITES))

    if failed:
        logger.warning("Failed sites (%d): %s", len(failed), ", ".join(failed))

    logger.info("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error("Fatal error during scraping: %s", e, exc_info=True)
        raise