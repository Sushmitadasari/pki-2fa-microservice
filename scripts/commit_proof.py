import base64
import subprocess
import sys
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Add project root to PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from app.config import STUDENT_PRIVATE_KEY_PATH
from app.crypto_utils import load_private_key

INSTRUCTOR_PUBLIC_KEY_PATH = PROJECT_ROOT / "instructor_public.pem"


def get_latest_commit_hash() -> str:
    """
    Get the latest git commit hash (40-character hex string).
    Uses: git log -1 --format=%H
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"Failed to get git commit hash: {e.stderr}") from e

    commit_hash = result.stdout.strip()

    if len(commit_hash) != 40:
        raise ValueError(f"Commit hash must be 40 characters, got {len(commit_hash)}")

    allowed = set("0123456789abcdef")
    if any(ch not in allowed for ch in commit_hash):
        raise ValueError("Commit hash is not a valid lowercase hex string")

    return commit_hash


def sign_message(message: str, private_key) -> bytes:
    """
    Sign a message using RSA-PSS with SHA-256

    Implementation:
    1. Encode commit hash as ASCII/UTF-8 bytes
       - CRITICAL: Sign the ASCII string, NOT binary hex!
       - Use message.encode('utf-8')

    2. Sign using RSA-PSS with SHA-256
       - Padding: PSS
       - MGF: MGF1(SHA-256)
       - Hash Algorithm: SHA-256
       - Salt Length: Maximum (PSS.MAX_LENGTH)

    3. Return signature bytes
    """
    data = message.encode("utf-8")
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return signature


def load_instructor_public_key(path: Path):
    """
    Load instructor's public key from PEM file.
    """
    if not path.exists():
        raise FileNotFoundError(f"Instructor public key not found at {path}")
    pem = path.read_bytes()
    public_key = serialization.load_pem_public_key(pem)
    return public_key


def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt data using RSA/OAEP with public key.

    Implementation:
    1. Encrypt signature bytes using RSA/OAEP with SHA-256
       - Padding: OAEP
       - MGF: MGF1 with SHA-256
       - Hash Algorithm: SHA-256
       - Label: None

    2. Return encrypted ciphertext bytes
    """
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return ciphertext


def main():
    # 1. Get current commit hash (40-char hex)
    commit_hash = get_latest_commit_hash()
    print(f"Commit Hash: {commit_hash}")

    # 2. Load student private key
    private_key = load_private_key(STUDENT_PRIVATE_KEY_PATH)

    # 3. Sign commit hash with student private key (RSA-PSS-SHA256)
    signature = sign_message(commit_hash, private_key)

    # 4. Load instructor public key
    instructor_public_key = load_instructor_public_key(INSTRUCTOR_PUBLIC_KEY_PATH)

    # 5. Encrypt signature with instructor public key (RSA/OAEP-SHA256)
    encrypted_signature = encrypt_with_public_key(signature, instructor_public_key)

    # 6. Base64 encode encrypted signature (single line)
    encrypted_signature_b64 = base64.b64encode(encrypted_signature).decode("utf-8")

    print("\nEncrypted Signature (Base64, single line):")
    print(encrypted_signature_b64)


if __name__ == "__main__":
    main()
