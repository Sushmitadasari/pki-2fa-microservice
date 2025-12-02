import base64
import time

import pyotp


def _hex_to_base32(hex_seed: str) -> str:
    """
    Convert 64-character hex seed to base32 encoded string.

    Steps:
        1. Convert hex string -> bytes
        2. Base32 encode the bytes
        3. Decode to UTF-8 string
    """
    # Validate basic length (not strictly necessary but useful)
    if len(hex_seed) != 64:
        raise ValueError(f"hex_seed must be 64 chars, got {len(hex_seed)}")

    try:
        seed_bytes = bytes.fromhex(hex_seed)
    except ValueError as e:
        raise ValueError(f"hex_seed is not valid hex: {e}")

    # Base32 encode
    base32_bytes = base64.b32encode(seed_bytes)
    return base32_bytes.decode("utf-8")


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current TOTP code from hex seed.

    TOTP parameters:
        - Algorithm: SHA-1 (default in pyotp)
        - Period: 30 seconds
        - Digits: 6
    """
    base32_seed = _hex_to_base32(hex_seed)

    # interval=30 => 30-second time step; digits=6 => 6-digit codes
    totp = pyotp.TOTP(base32_seed, interval=30, digits=6)
    code = totp.now()  # returns 6-digit string
    return code


def get_current_validity_seconds() -> int:
    """
    Return how many seconds the current TOTP code is still valid for
    in the current 30-second window, using Unix time.

    Example: if we are 13 seconds into the period -> valid_for = 30 - 13 = 17
    """
    current_time = int(time.time())
    elapsed_in_period = current_time % 30
    remaining = 30 - elapsed_in_period
    return remaining


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with time window tolerance.

    Args:
        hex_seed: 64-character hex string
        code: 6-digit code to verify
        valid_window: number of periods before/after to accept
                      (1 means current period ±1 => ±30 seconds)

    Returns:
        True if code is valid within the time window, False otherwise.
    """
    if not code or len(code) != 6 or not code.isdigit():
        # Not strictly required by spec, but helpful sanity check
        return False

    base32_seed = _hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, interval=30, digits=6)

    # valid_window=1 -> accepts TOTP codes for [t-1, t, t+1] periods
    return totp.verify(code, valid_window=valid_window)
