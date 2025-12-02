import base64
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def load_private_key(path: Path):
    """
    Load RSA private key from PEM file.
    """
    if not path.exists():
        raise FileNotFoundError(f"Private key file not found at {path}")

    pem_data = path.read_bytes()
    private_key = serialization.load_pem_private_key(
        pem_data,
        password=None,  # we didn't set a password when generating
    )
    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise TypeError("Loaded key is not an RSA private key")

    return private_key


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP.

    Args:
        encrypted_seed_b64: Base64-encoded ciphertext string
        private_key: RSA private key object

    Returns:
        Decrypted hex seed (64-character string)

    Steps:
        1. Base64 decode the encrypted seed string
        2. RSA/OAEP decrypt with:
           - Padding: OAEP
           - MGF: MGF1(SHA-256)
           - Hash: SHA-256
           - Label: None
        3. Decode bytes to UTF-8 string
        4. Validate: must be 64-character hex string
           - Check length is 64
           - Check all characters are in '0123456789abcdef'
        5. Return hex seed
    """
    # 1. Base64 decode
    try:
        ciphertext = base64.b64decode(encrypted_seed_b64, validate=True)
    except Exception as e:
        raise ValueError(f"Invalid base64 for encrypted seed: {e}")

    # 2. RSA/OAEP decrypt with SHA-256 + MGF1(SHA-256)
    try:
        plaintext_bytes = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    except Exception as e:
        # Any error here means decryption failed (wrong key/params/data)
        raise ValueError(f"RSA decryption failed: {e}")

    # 3. Decode to UTF-8 string
    try:
        hex_seed = plaintext_bytes.decode("utf-8").strip()
    except UnicodeDecodeError as e:
        raise ValueError(f"Decrypted bytes are not valid UTF-8: {e}")

    # 4. Validate hex seed format: 64 hex characters
    if len(hex_seed) != 64:
        raise ValueError(f"Decrypted seed must be 64 characters, got {len(hex_seed)}")

    allowed_chars = set("0123456789abcdef")
    if any(ch not in allowed_chars for ch in hex_seed):
        raise ValueError("Decrypted seed contains non-hex characters")

    return hex_seed
