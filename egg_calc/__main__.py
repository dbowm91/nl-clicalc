"""
Entry point for running eggcalc as a module.

Usage:
    python -m egg_calc "five plus two"
    python -m egg_calc --help
"""

import os
import sys

if __name__ == "__main__":
    egg_calc_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if egg_calc_dir not in sys.path:
        sys.path.insert(0, egg_calc_dir)

    from egg_calc.normalize import main

    sys.exit(main())