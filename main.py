"""
main.py

Top-level entry point. `flowiq` lives under src/, not at the project
root, so we add src/ to Python's import path before importing it --
this lets `python main.py` work directly, without needing to set
PYTHONPATH or install the package first.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from flowiq.cli import main

if __name__ == "__main__":
    main()
