#!/usr/bin/env python3
"""Build outputs/dashboard/dashboard.html (and docs/index.html for GitHub Pages)."""
import subprocess
import sys
import os

BASE = os.path.join(os.path.dirname(__file__), "..")

if __name__ == "__main__":
    for rel in ["src/dashboard/build_dashboard_data.py", "src/dashboard/build_dashboard.py"]:
        rc = subprocess.call([sys.executable, os.path.join(BASE, rel)])
        if rc != 0:
            sys.exit(rc)
