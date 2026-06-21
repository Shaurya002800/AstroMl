"""Create a verified archive containing encrypted session files."""

import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

from backup import create_encrypted_backup, verify_backup


if __name__ == "__main__":
    destination = os.getenv("SERENOVA_BACKUP_DIR")
    if not destination:
        raise SystemExit("SERENOVA_BACKUP_DIR is required.")
    path = create_encrypted_backup(destination)
    print(json.dumps({"path": path, **verify_backup(path)}, indent=2))
