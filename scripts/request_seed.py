import json
from pathlib import Path

import requests


API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

# TODO: change this to your actual student ID from the portal
STUDENT_ID = "YOUR_STUDENT_ID_HERE"

# IMPORTANT: use the browser URL of your repo, WITHOUT .git at the end
GITHUB_REPO_URL = "https://github.com/Sushmitadasari/pki-2fa-microservice"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_KEY_PATH = PROJECT_ROOT / "student_public.pem"
OUTPUT_PATH = PROJECT_ROOT / "encrypted_seed.txt"


def load_public_key_pem() -> str:
    """
    Read the student public key from PEM file and return as string.
    The PEM format must be kept exactly as-is with BEGIN/END markers.
    """
    if not PUBLIC_KEY_PATH.exists():
        raise FileNotFoundError(f"Public key file not found at {PUBLIC_KEY_PATH}")

    pem_bytes = PUBLIC_KEY_PATH.read_bytes()
    # Decode to string; json will handle newlines correctly
    return pem_bytes.decode("utf-8")


def request_seed(student_id: str, github_repo_url: str, api_url: str = API_URL) -> str:
    """
    Request encrypted seed from instructor API and return the encrypted_seed string.
    Also saves encrypted_seed.txt in the project root.
    """
    public_key_pem = load_public_key_pem()

    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_pem,
    }

    print("Sending request to instructor API...")
    print(f"student_id: {student_id}")
    print(f"github_repo_url: {github_repo_url}")

    try:
        response = requests.post(
            api_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=20,
        )
    except requests.RequestException as e:
        raise SystemExit(f"Error while calling instructor API: {e}")

    if response.status_code != 200:
        raise SystemExit(
            f"API returned non-200 status: {response.status_code}\nBody: {response.text}"
        )

    try:
        data = response.json()
    except json.JSONDecodeError:
        raise SystemExit(f"Failed to parse JSON from API response: {response.text}")

    if data.get("status") != "success":
        raise SystemExit(f"API did not return success status: {data}")

    encrypted_seed = data.get("encrypted_seed")
    if not encrypted_seed:
        raise SystemExit("API response missing 'encrypted_seed' field")

    # Save to file (single line, no extra spaces)
    OUTPUT_PATH.write_text(encrypted_seed.strip(), encoding="utf-8")

    print(f"Encrypted seed received and saved to: {OUTPUT_PATH}")
    return encrypted_seed


if __name__ == "__main__":
    if STUDENT_ID == "23A91A61E9":
        raise SystemExit("Please set your STUDENT_ID in request_seed.py before running.")

    request_seed(STUDENT_ID, GITHUB_REPO_URL)
    print("Done.")
