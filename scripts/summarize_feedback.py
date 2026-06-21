"""Summarize privacy-minimized consultant feedback."""

import argparse
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

from evaluation.feedback_metrics import (
    load_feedback_records,
    summarize_feedback,
)
from feedback import FEEDBACK_PATH


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=FEEDBACK_PATH)
    arguments = parser.parse_args()
    records = (
        load_feedback_records(arguments.path)
        if os.path.exists(arguments.path)
        else []
    )
    print(json.dumps(summarize_feedback(records), indent=2))
