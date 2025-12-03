from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .config import SEED_FILE_PATH, STUDENT_PRIVATE_KEY_PATH
from .crypto_utils import load_private_key, decrypt_seed
from .totp_utils import generate_totp_code, verify_totp_code, get_current_validity_seconds


app = FastAPI(title="PKI-based 2FA Microservice")


# ---------- Pydantic Models ----------

class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class Generate2FAResponse(BaseModel):
    code: str
    valid_for: int


class Verify2FARequest(BaseModel):
    code: str | None = None


class Verify2FAResponse(BaseModel):
    valid: bool


# ---------- Helper Functions ----------

def _ensure_seed_dir_exists():
    seed_dir: Path = SEED_FILE_PATH.parent
    seed_dir.mkdir(parents=True, exist_ok=True)


def _load_hex_seed_from_file() -> str:
    if not SEED_FILE_PATH.exists():
        # As per spec: 500 error if seed unavailable
        raise FileNotFoundError("Seed not decrypted yet")

    hex_seed = SEED_FILE_PATH.read_text(encoding="utf-8").strip()
    if not hex_seed or len(hex_seed) != 64:
        raise ValueError("Stored seed is invalid")
    return hex_seed


# ---------- Endpoints ----------

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(payload: DecryptSeedRequest):
    """
    POST /decrypt-seed
    Request:
        {
          "encrypted_seed": "BASE64_STRING..."
        }
    Success (200):
        { "status": "ok" }
    Failure (500):
        { "error": "Decryption failed" }
    """
    encrypted_seed_b64 = payload.encrypted_seed

    try:
        private_key = load_private_key(STUDENT_PRIVATE_KEY_PATH)
        hex_seed = decrypt_seed(encrypted_seed_b64, private_key)
    except Exception:
        # Do NOT leak internal error details per spec
        return JSONResponse(
            status_code=500,
            content={"error": "Decryption failed"},
        )

    # Save seed to /data/seed.txt (or path from config)
    try:
        _ensure_seed_dir_exists()
        SEED_FILE_PATH.write_text(hex_seed, encoding="utf-8")
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Decryption failed"},
        )

    return {"status": "ok"}


@app.get("/generate-2fa", response_model=Generate2FAResponse)
def generate_2fa_endpoint():
    """
    GET /generate-2fa
    Success (200):
        {
          "code": "123456",
          "valid_for": 30
        }
    Error when seed missing (500):
        { "error": "Seed not decrypted yet" }
    """
    try:
        hex_seed = _load_hex_seed_from_file()
        code = generate_totp_code(hex_seed)
        valid_for = get_current_validity_seconds()
    except FileNotFoundError:
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"},
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"},
        )

    return Generate2FAResponse(code=code, valid_for=valid_for)


@app.post("/verify-2fa", response_model=Verify2FAResponse)
def verify_2fa_endpoint(payload: Verify2FARequest):
    """
    POST /verify-2fa
    Request:
        { "code": "123456" }

    Responses:
        200:
          { "valid": true } or { "valid": false }
        400:
          { "error": "Missing code" }
        500:
          { "error": "Seed not decrypted yet" }
    """
    if payload.code is None or payload.code == "":
        return JSONResponse(
            status_code=400,
            content={"error": "Missing code"},
        )

    code = payload.code

    try:
        hex_seed = _load_hex_seed_from_file()
    except FileNotFoundError:
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"},
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"},
        )

    # Verify TOTP with ±1 period tolerance
    try:
        is_valid = verify_totp_code(hex_seed, code, valid_window=1)
    except Exception:
        # Treat any internal error as "invalid code" but still 200
        is_valid = False

    return Verify2FAResponse(valid=is_valid)


@app.get("/health")
def health_check():
    """
    Optional health endpoint to quickly verify container is running.
    Not required by spec, but useful for testing.
    """
    return {"status": "healthy"}
