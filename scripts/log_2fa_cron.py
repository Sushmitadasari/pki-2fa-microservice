#!/usr/bin/env python3

import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to PYTHONPATH so imports work when running from /app
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import SEED_FILE_PATH  # will be /data/seed.txt inside container
from app.totp_utils import generate_totp_code


def main():
    try:
        seed_path: Path = SEED_FILE_PATH
        if not seed_path.exists():
            # If seed not yet decrypted, print error to stderr and exit gracefully
            print(f"[WARN] Seed file not found at {seed_path}", file=sys.stderr)
            return

        hex_seed = seed_path.read_text(encoding="utf-8").strip()
        if not hex_seed:
            print(f"[WARN] Seed file {seed_path} is empty", file=sys.stderr)
            return

        # Generate current TOTP code
        code = generate_totp_code(hex_seed)

        # Get current UTC timestamp
        now_utc = datetime.now(timezone.utc)
        timestamp_str = now_utc.strftime("%Y-%m-%d %H:%M:%S")

        # Output in required format
        # This goes to stdout; cron will append it to /cron/last_code.txt
        print(f"{timestamp_str} - 2FA Code: {code}")

    except Exception as e:
        # Any unexpected error goes to stderr so it won't break cron daemon
        print(f"[ERROR] log_2fa_cron failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
