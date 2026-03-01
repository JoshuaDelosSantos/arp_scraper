from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://arxiv.org")
LISTING_URL = os.getenv("LISTING_URL", "https://arxiv.org/list/cs.AI/recent")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "papers"))
NUM_PAPERS = int(os.getenv("NUM_PAPERS"))
DELAY = int(os.getenv("DELAY"))