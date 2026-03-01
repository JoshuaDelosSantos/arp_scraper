import requests
from bs4 import BeautifulSoup
import config
import os

def save_paper(paper:dict, output_dir: str) -> None:
    """
    Args:
        paper (dict): Dictionary containing paper ID and BeautifulSoup object
        output_dir (str): Output directory path where the paper text will be saved
        
    Saves the paper text to a file named {paper_id}.txt in the specified output directory.
    """
    paper_id = paper["id"]
    soup = paper["soup"]
    
    for tag in soup(["script", "style", "header", "footer", "nav"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)

    with open(f"{output_dir}/{paper_id}.txt", "w", encoding="utf-8") as f:
        f.write(text)
        print(f"Saved paper {paper_id} to {output_dir}/{paper_id}.txt")


def fetch_paper(paper_id: str) -> dict:
    """
    Fetches the paper details given a paper ID and returns a dictionary with the paper ID and its BeautifulSoup object.
    """
    try:
        url = f"{config.BASE_URL}/html/{paper_id}"
        print(f"Fetching paper: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    
    except requests.HTTPError:
        # Modify this logic for a fallback
        print(f"Failed to fetch paper {paper_id}: HTTP error")
        return None
    
    return {
        "id": paper_id,
        "soup": BeautifulSoup(response.text, 'html.parser')
    }
        
    
def get_paper_ids(listing_url: str, num_papers: int) -> list[str]:
    """
    Args:
        listing_url (str): URL of the arXiv listing page to scrape for paper IDs
        num_papers (int): Number of paper IDs to retrieve

    Returns:
        list[str]: List of paper IDs
    """
    response = requests.get(listing_url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    ids = []
    for a_tag in soup.select("a[href^='/abs/']"):
        paper_id = a_tag["href"].split("/abs/")[-1]
        
        if paper_id and paper_id not in ids:
            ids.append(paper_id)
            print(f"Found paper ID: {paper_id}")
        
        if os.path.exists(f"{config.OUTPUT_DIR}/{paper_id}.txt"):
            print(f"Paper {paper_id} already exists. Skipping.")
            ids.remove(paper_id)  # Remove the paper ID from the list if it already exists
            
        if len(ids) >= num_papers:
            print(f"Reached desired number of papers: {num_papers}")
            break
    return ids



if __name__ == "__main__":
    # paper_ids = get_paper_ids(config.LISTING_URL, config.NUM_PAPERS)
    # print(paper_ids)
    
    # paper = fetch_paper(paper_id=get_paper_ids(config.LISTING_URL, 1)[0])
    # print(paper["soup"].title.text if paper else "No paper found")
    
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    save_paper(fetch_paper(get_paper_ids(config.LISTING_URL, 1)[0]), config.OUTPUT_DIR)