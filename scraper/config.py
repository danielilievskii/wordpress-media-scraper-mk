# List of WordPress sites to scrape
SITES = [
    "kurir.mk",
    "republika.mk",
    "centar.mk",
    "sportmedia.mk",
    "magazin.mk",
    "smartportal.mk",
    "makpress.mk",
    "irl.mk",
    "a1on.mk",
    "plusinfo.mk",
    "mkd-news.com",
    "mkinfo.mk",
    "slobodenpecat.mk",
    "press24.mk",
    "nezavisen.mk",
    "trn.mk",
    "4news.mk",
    "racin.mk",
    "netpress.com.mk",
    "makedonija24.mk",
    "infomax.mk",
    "puls24.mk"
]

# WordPress API endpoint templates
BASE_URL_TEMPLATE = "https://{}/wp-json/wp/v2/posts"
CATEGORIES_URL_TEMPLATE = "https://{}/wp-json/wp/v2/categories"

# Data storage
DATA_DIR = "data"
DATASET_FILENAME_TEMPLATE = "{}_articles_dataset.json"

# Scraping settings
POSTS_PER_PAGE = 100
MAX_CONCURRENT_REQUESTS = 5
REQUEST_TIMEOUT = 20
REQUEST_DELAY = 1.0

# HTTP Headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"