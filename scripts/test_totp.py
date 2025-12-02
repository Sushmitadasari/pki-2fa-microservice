import sys
from pathlib import Path

# Add project root to PYTHONPATH (same trick as test_decrypt_seed.py)
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import PROJECT_ROOT, STUDENT_PRIVATE_KEY_PATH
from app.crypto_utils import load_private_key, decrypt_seed
from app.totp_utils import generate_totp_code, verify_totp_code, get_current_validity_seconds


def main():
    encrypted_seed_path = PROJECT_ROOT / "encrypted_seed.txt"

    if not encrypted_seed_path.exists():
        raise SystemExit(
            f"encrypted_seed.txt not found at {encrypted_seed_path}. "
            f"Run scripts/request_seed.py first."
        )

    encrypted_seed_b64 = encrypted_seed_path.read_text(encoding="utf-8").strip()

    print(f"Loaded encrypted seed (length={len(encrypted_seed_b64)} chars)")
    print("Loading private key...")
    private_key = load_private_key(STUDENT_PRIVATE_KEY_PATH)

    print("Decrypting to hex seed...")
    hex_seed = decrypt_seed(encrypted_seed_b64, private_key)
    print(f"Decrypted hex seed: {hex_seed}")
    print(f"Length: {len(hex_seed)} characters")

    print("\nGenerating current TOTP code...")
    code = generate_totp_code(hex_seed)
    valid_for = get_current_validity_seconds()

    print(f"Current TOTP code: {code}")
    print(f"Valid for approximately: {valid_for} seconds")

    print("\nVerifying the same code (should be True)...")
    is_valid = verify_totp_code(hex_seed, code, valid_window=1)
    print(f"Verification result for {code}: {is_valid}")

    print("\nVerifying a clearly wrong code '000000' (should be False)...")
    is_valid_wrong = verify_totp_code(hex_seed, "000000", valid_window=1)
    print(f"Verification result for 000000: {is_valid_wrong}")


if __name__ == "__main__":
    main()
