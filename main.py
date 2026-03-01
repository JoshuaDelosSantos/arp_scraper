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
    
    for i, paper_id in enumerate(paper_ids, 1):
        paper = p.fetch_paper(paper_id)
        p.save_paper(paper, config.OUTPUT_DIR)
        time.sleep(config.DELAY)  # Be polite and avoid hitting the server too hard
        
    print(f"Finished fetching {len(paper_ids)} papers. Saved to {config.OUTPUT_DIR}.")
    
if __name__ == "__main__":
    main()