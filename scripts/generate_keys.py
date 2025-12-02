from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_rsa_keypair(key_size: int = 4096):
    """
    Generate RSA key pair

    Returns:
        Tuple of (private_key, public_key) objects
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    public_key = private_key.public_key()
    return private_key, public_key


def save_keys(private_key, public_key, base_dir: Path):
    """
    Save private and public keys in PEM format in the repo root.
    Filenames:
        - student_private.pem
        - student_public.pem
    """
    private_path = base_dir / "student_private.pem"
    public_path = base_dir / "student_public.pem"

    # Private key in PEM (PKCS8, no password)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Public key in PEM (SubjectPublicKeyInfo)
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    private_path.write_bytes(private_pem)
    public_path.write_bytes(public_pem)

    print(f"Saved private key to: {private_path}")
    print(f"Saved public key  to: {public_path}")


if __name__ == "__main__":
    # project root = parent of 'scripts' folder
    project_root = Path(__file__).resolve().parent.parent

    print("Generating 4096-bit RSA key pair with public exponent 65537...")
    private_key, public_key = generate_rsa_keypair()

    save_keys(private_key, public_key, project_root)
    print("Done.")
