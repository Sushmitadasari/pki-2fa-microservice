import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# For local testing: store seed under project_root/data/seed.txt
# Later in Docker, we'll override this with env var SEED_FILE_PATH=/data/seed.txt
DEFAULT_SEED_PATH = PROJECT_ROOT / "data" / "seed.txt"

SEED_FILE_PATH = Path(os.getenv("SEED_FILE_PATH", DEFAULT_SEED_PATH))
STUDENT_PRIVATE_KEY_PATH = PROJECT_ROOT / "student_private.pem"
