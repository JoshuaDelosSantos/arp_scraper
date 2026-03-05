import json
import os

import requests
from bs4 import BeautifulSoup

import config

def load_papers(output_dir: str) -> list[dict]:
    """
    Loads existing papers from the papers.json file in the output directory.
    Returns an empty list if the file does not exist.
    """
    filepath = f"{output_dir}/papers.json"
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_papers(papers: list[dict], output_dir: str) -> None:
    """
    Args:
        papers (list[dict]): List of paper dictionaries to save
        output_dir (str): Output directory path

    Merges new papers with any existing papers in papers.json,
    avoiding duplicates by paper ID.
    """
    existing = load_papers(output_dir)
    existing_ids = {p["id"] for p in existing}

    new_papers = [p for p in papers if p["id"] not in existing_ids]
    merged = existing + new_papers

    filepath = f"{output_dir}/papers.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(new_papers)} new paper(s) to {filepath} ({len(merged)} total)")


def fetch_paper(paper_id: str) -> dict:
    """
    Fetches the paper details given a paper ID and returns a dictionary
    with structured metadata and content.
    """
    try:
        url = f"{config.BASE_URL}/html/{paper_id}"
        print(f"Fetching paper: {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()

    except requests.HTTPError:
        print(f"Failed to fetch paper {paper_id}: HTTP error {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract title
    title_tag = soup.find("h1", class_="ltx_title")
    title = title_tag.get_text(strip=True).removeprefix("Title:") if title_tag else ""

    # Extract authors
    authors_tag = soup.find("div", class_="ltx_authors")
    authors = authors_tag.get_text(separator=", ", strip=True) if authors_tag else ""

    # Extract abstract
    abstract_tag = soup.find("div", class_="ltx_abstract")
    abstract = abstract_tag.get_text(separator="\n", strip=True).removeprefix("Abstract\n") if abstract_tag else ""

    # Extract body text (strip non-content tags)
    for tag in soup(["script", "style", "header", "footer", "nav"]):
        tag.decompose()
    body = soup.get_text(separator="\n", strip=True)

    return {
        "id": paper_id,
        "title": title.strip(),
        "authors": authors.strip(),
        "abstract": abstract.strip(),
        "body": body,
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

    _existing_ids = {p["id"] for p in load_papers(config.OUTPUT_DIR)}

    ids = []
    for a_tag in soup.select("a[href^='/abs/']"):
        paper_id = a_tag["href"].split("/abs/")[-1]
        
        if paper_id and paper_id not in ids:
            ids.append(paper_id)
            print(f"Found paper ID: {paper_id}")
        
        if paper_id in _existing_ids:
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
    
    # config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # save_paper(fetch_paper(get_paper_ids(config.LISTING_URL, 1)[0]), config.OUTPUT_DIR)
    
    fetch_paper(paper_id="2603.02062")