# WordPress Media Scraper MK

Multi-site WordPress scraper for Macedonian news and media outlets - part of Vezilka project.

This project scrapes journalism articles from 20+ Macedonian WordPress media sites and stores them in structured JSON datasets. It supports incremental scraping, concurrent requests, and automatic retry logic.

---

## Supported Sites

The scraper currently supports 22 Macedonian media outlets:

- kurik.mk
- republika.mk
- centar.mk
- sportmedia.mk
- magazin.mk
- smartportal.mk
- makpress.mk
- irl.mk
- a1on.mk
- plusinfo.mk
- mkd-news.com
- mkinfo.mk
- slobodenpecat.mk
- press24.mk
- nezavisen.mk
- trn.mk
- 4news.mk
- racin.mk
- netpress.com.mk
- makedonija24.mk
- infomax.mk
- puls24.mk

---

## Features

- **Multi-site support**: Scrapes 24+ WordPress sites sequentially
- **Incremental updates**: Only fetches new articles on subsequent runs
- **Smart pagination**: Stops early when all posts on a page already exist
- **Concurrent requests**: Uses async HTTP for fast initial scraping
- **Rate limiting**: Respects server limits with automatic retry and backoff
- **Structured output**: Saves articles with metadata (title, content, categories, date, link)
- **Comprehensive logging**: Detailed progress tracking and error reporting
- **Site-specific datasets**: Each site gets its own JSON file

---

## Project Structure
```
wordpress-media-scraper-mk/
│
├── data/
│   ├── irl_mk_articles_dataset.json
│   ├── kurir_mk_articles_dataset.json
│   ├── republika_mk_articles_dataset.json
│   └── ... (one file per site)
│
├── scraper/
│   ├── config.py           # Configuration and site list
│   ├── fetcher.py          # Async HTTP fetching logic
│   ├── parsers.py          # HTML parsing and data extraction
│   ├── data_utils.py       # Dataset loading and saving
│   └── scraper.py          # Main scraping orchestration
│
├── main.py                 # Entry point
├── requirements.txt
└── README.md
```

---

## Setup

1. Clone the repository:
```bash
git clone https://github.com/danielilievskii/wordpress-media-scraper-mk
cd wordpress-media-scraper-mk
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```


## Usage

To run the scraper for all sites:
```bash
python main.py
```

The scraper will:

- Process each site sequentially
- Fetch only new articles (incremental updates)
- Save data to `data/{site_name}_articles_dataset.json`
- Display detailed progress and statistics
- Show a final summary with successful/failed sites

---

## Configuration

Configure scraping behavior in `scraper/config.py`:

### Sites List
```python
SITES = [
    "irl.mk",
    "kurir.mk",
    # ... add or remove sites here
]
```

### API Endpoints
- `BASE_URL_TEMPLATE`: WordPress REST API endpoint template for posts
- `CATEGORIES_URL_TEMPLATE`: WordPress REST API endpoint template for categories

### Data Storage
- `DATA_DIR`: Directory to store JSON datasets (default: `data/`)
- `DATASET_FILENAME_TEMPLATE`: Filename pattern for site datasets

### Scraping Settings
- `POSTS_PER_PAGE`: Posts per API request (default: 100)
- `MAX_CONCURRENT_REQUESTS`: Concurrent HTTP requests (default: 5)
- `REQUEST_TIMEOUT`: Timeout per request in seconds (default: 20)
- `REQUEST_DELAY`: Delay between requests (default: 1.0)

### HTTP Headers
- `HEADERS`: Browser-like headers to avoid blocking
  - User-Agent, Accept, Accept-Language, Accept-Encoding, Connection

### Logging
- `LOG_LEVEL`: Logging verbosity (default: "INFO")
- `LOG_FORMAT`: Log message format

---

## Output Format

Each article is saved with the following structure:
```json
{
    "id": 12345,
    "link": "https://example.mk/article-url",
    "date": "2026-01-21T10:30:00",
    "title": "Article Title",
    "content": "Plain text article content...",
    "categories": ["Politics", "Economy"]
}
```

Articles are automatically sorted by date within each dataset file.

---

## Logging

The scraper provides detailed logging at multiple levels:

- **INFO**: Progress updates, page completion, article counts
- **WARNING**: Rate limiting, missing categories, failed pages
- **ERROR**: HTTP errors, parsing failures, connection issues

---
