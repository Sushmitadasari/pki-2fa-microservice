import sys
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import PROJECT_ROOT, STUDENT_PRIVATE_KEY_PATH
from app.crypto_utils import load_private_key, decrypt_seed


def main():
    encrypted_seed_path = PROJECT_ROOT / "encrypted_seed.txt"

    if not encrypted_seed_path.exists():
        raise SystemExit(f"encrypted_seed.txt not found at {encrypted_seed_path}. "
                         f"Did you run request_seed.py already?")

    encrypted_seed_b64 = encrypted_seed_path.read_text(encoding="utf-8").strip()

    print(f"Loaded encrypted seed (length={len(encrypted_seed_b64)} chars)")
    print("Loading private key...")
    private_key = load_private_key(STUDENT_PRIVATE_KEY_PATH)

    print("Decrypting...")
    hex_seed = decrypt_seed(encrypted_seed_b64, private_key)

    print("Decryption successful ✅")
    print(f"Decrypted hex seed: {hex_seed}")
    print(f"Length: {len(hex_seed)} characters")


if __name__ == "__main__":
    main()
