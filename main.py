import time
import config
import paper as p

def main():
    paper_ids = p.get_paper_ids(config.LISTING_URL, config.NUM_PAPERS)
    
    if not paper_ids:
        print("No paper IDs found. Exiting.")
        return
    
    if not config.OUTPUT_DIR.exists():
        config.OUTPUT_DIR.mkdir(parents=True)
    
    papers = []
    for paper_id in paper_ids:
        if paper_id is None:
            print("Skipping invalid paper ID: None")
            continue
        try:
            paper = p.fetch_paper(paper_id)
            if paper:
                papers.append(paper)
        except Exception as e:
            print(f"Error fetching paper {paper_id}: {e}")

        time.sleep(config.DELAY)  # Be polite and avoid hitting the server too hard

    if papers:
        p.save_papers(papers, config.OUTPUT_DIR)

    print(f"Finished fetching {len(papers)} paper(s). Saved to {config.OUTPUT_DIR}.")
    
if __name__ == "__main__":
    main()