from pathlib import Path

# Project root = parent of this "app" directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Path to student private key
STUDENT_PRIVATE_KEY_PATH = PROJECT_ROOT / "student_private.pem"

# Path where decrypted seed will be stored INSIDE CONTAINER
# (Later Docker will mount /data as a volume; for now for local tests we can still use this constant)
SEED_FILE_PATH = Path("/data/seed.txt")
