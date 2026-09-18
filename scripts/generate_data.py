#!/usr/bin/env python3
"""Generate all synthetic source tables into data/raw/."""
import subprocess
import sys
import os

BASE = os.path.join(os.path.dirname(__file__), "..")

if __name__ == "__main__":
    script = os.path.join(BASE, "src", "data_generation", "generate_all.py")
    sys.exit(subprocess.call([sys.executable, script]))
