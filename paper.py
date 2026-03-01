import requests
from bs4 import BeautifulSoup
import time
import config

def _get_paper_ids(listing_url: str, num_papers: int) -> list[str]:
    response = requests.get(listing_url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    ids = []
    for a_tag in soup.select("a[href^='/abs/']"):
        paper_id = a_tag["href"].split("/abs/")[-1]
        
        if paper_id and paper_id not in ids:
            ids.append(paper_id)
            print(f"Found paper ID: {paper_id}")
        if len(ids) >= num_papers:
            print(f"Reached desired number of papers: {num_papers}")
            break
    return ids

if __name__ == "__main__":
    paper_ids = _get_paper_ids(config.LISTING_URL, config.NUM_PAPERS)
    print(paper_ids)