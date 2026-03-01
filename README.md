# Overview
- Python script that scrapes https://arxiv.org for AI research papers
- Scraped papers are stored as .txt files in specified directory within the [config](/config.py)

## Docker
1. Pull image
```
docker pull joshuaffds/arc_scraper:latest
```

2. Build with env
```
docker run \
-e NUM_PAPERS=3 \  # Number of papers to scrape
-e DELAY=3 \  # Delay per fetch req
-v $PWD/papers:/app/papers \  # Add this to output papers in project dir
joshuaffds/arp_scraper:latest
```