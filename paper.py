import requests
from bs4 import BeautifulSoup
import time
import config

def fetch_paper(paper_id: str) -> BeautifulSoup:
    try:
        url = f"{config.BASE_URL}/html/{paper_id}"
        print(f"Fetching paper: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    
    except requests.HTTPError:
        # Modify this logic for a fallback
        print(f"Failed to fetch paper {paper_id}: HTTP error")
        return None
    
    return BeautifulSoup(response.text, 'html.parser')
        
    

def get_paper_ids(listing_url: str, num_papers: int) -> list[str]:
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
    # paper_ids = get_paper_ids(config.LISTING_URL, config.NUM_PAPERS)
    # print(paper_ids)
    
    soup = fetch_paper(paper_id=get_paper_ids(config.LISTING_URL, 1)[0])
    print(soup.title.text if soup else "No paper found")