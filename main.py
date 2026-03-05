import logging
import time

import config
import paper as p

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info("Starting paper scraper")
    logger.info("Listing URL: %s | Num papers: %s | Delay: %ss", config.LISTING_URL, config.NUM_PAPERS, config.DELAY)

    paper_ids = p.get_paper_ids(config.LISTING_URL, config.NUM_PAPERS)
    
    if not paper_ids:
        logger.warning("No paper IDs found. Exiting.")
        return
    
    if not config.OUTPUT_DIR.exists():
        config.OUTPUT_DIR.mkdir(parents=True)
        logger.info("Created output directory: %s", config.OUTPUT_DIR)
    
    papers = []
    for paper_id in paper_ids:
        if paper_id is None:
            logger.warning("Skipping invalid paper ID: None")
            continue
        try:
            paper = p.fetch_paper(paper_id)
            if paper:
                papers.append(paper)
        except Exception as e:
            logger.error("Error fetching paper %s: %s", paper_id, e, exc_info=True)

        time.sleep(config.DELAY)

    if papers:
        p.save_papers(papers, config.OUTPUT_DIR)

    logger.info("Finished fetching %d paper(s). Saved to %s.", len(papers), config.OUTPUT_DIR)
    
if __name__ == "__main__":
    main()