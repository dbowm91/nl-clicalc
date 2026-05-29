"""
Entry point for running nl-calc as a module.

Usage:
    python -m nl_calc "five plus two"
    python -m nl_calc --help
"""

import os
import sys

if __name__ == "__main__":
    nl_calc_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if nl_calc_dir not in sys.path:
        sys.path.insert(0, nl_calc_dir)

    from nl_calc.normalize import main

    sys.exit(main())
