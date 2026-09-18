#!/usr/bin/env python3
"""Build outputs/excel/RETAIL_BANKING_ANALYTICS.xlsx."""
import subprocess
import sys
import os

BASE = os.path.join(os.path.dirname(__file__), "..")

if __name__ == "__main__":
    script = os.path.join(BASE, "src", "reporting", "build_excel.py")
    sys.exit(subprocess.call([sys.executable, script]))
