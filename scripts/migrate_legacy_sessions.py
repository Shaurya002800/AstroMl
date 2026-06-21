"""Encrypt legacy plaintext session files."""

import argparse
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

from legacy_migration import migrate_plaintext_sessions


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--session-dir",
        default=os.path.join(ROOT, "data", "sessions"),
    )
    parser.add_argument(
        "--delete-plaintext",
        action="store_true",
        help="Delete each plaintext source only after encrypted output is written.",
    )
    arguments = parser.parse_args()
    print(json.dumps(
        migrate_plaintext_sessions(
            arguments.session_dir,
            delete_plaintext=arguments.delete_plaintext,
        ),
        indent=2,
    ))
