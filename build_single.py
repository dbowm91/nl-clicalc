#!/usr/bin/env python3
"""
Build script to combine nl_calc modules into a single self-contained executable.

Usage:
    python3 build_single.py          # Build nl_calc.py in current directory
    python3 build_single.py -o /path/to/output  # Custom output path
"""

import argparse
import os
import sys

MODULES = ["units", "evaluator", "normalize", "__main__"]

HEADER = '''#!/usr/bin/env python3
from __future__ import annotations

"""
nl_calc - Natural language math expression calculator

Single-file version. Run: python3 nl_calc.py "five plus two"
Or make executable: chmod +x nl_calc.py && ./nl_calc.py "five plus two"
"""

import sys
import os

# Prevent pip from auto-installing dependencies
os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"

'''


def get_version():
    """Get version from __init__.py"""
    init_path = os.path.join(os.path.dirname(__file__), "nl_calc", "__init__.py")
    with open(init_path, "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"')
    return "1.0.0"


def get_module_code(module_name):
    """Extract code from a module, removing docstring and imports that will be inlined."""
    module_path = os.path.join(os.path.dirname(__file__), "nl_calc", f"{module_name}.py")

    with open(module_path, "r") as f:
        lines = f.readlines()

    # Find where code starts (after docstring)
    in_docstring = False
    start_idx = 0
    for i, line in enumerate(lines):
        if i == 0 and '"""' in line:
            in_docstring = True
        if in_docstring:
            if '"""' in line and i > 0:
                in_docstring = False
                start_idx = i + 1
                break
        elif line.startswith('"""'):
            in_docstring = True

    # Get the code
    code_lines = lines[start_idx:]

    # Remove relative imports and from __future__ that will be inlined
    cleaned = []
    in_main_block = False
    in_multiline_import = False
    for i, line in enumerate(code_lines):
        stripped = line.strip()
        # Check if we're entering a multi-line import
        if stripped.startswith("from .") and "(" in stripped:
            in_multiline_import = True
            continue
        if stripped.startswith("from ."):
            # Handle specific imports that need replacement
            if "import _default_evaluator" in stripped:
                # _default_evaluator is defined in the same file, no import needed
                continue
            elif "from .units import" in stripped:
                # units code is inlined, no import needed
                continue
            elif "from .evaluator import" in stripped:
                # evaluator code is inlined, no import needed
                continue
            elif "from .normalize import" in stripped:
                # normalize code is inlined, no import needed
                continue
            # Skip other relative imports
            continue
        # Handle multi-line imports we're skipping
        if in_multiline_import:
            if ")" in stripped:
                in_multiline_import = False
            continue
        if "from __future__" in line:
            continue
        # Skip if __name__ == "__main__" blocks (we'll add our own)
        if line.startswith("if __name__") and "__main__" in line:
            in_main_block = True
            continue
        if in_main_block:
            if line.strip() and not line[0].isspace():
                in_main_block = False
            else:
                continue
        # Skip empty lines at start
        if not cleaned and line.strip() == "":
            continue
        cleaned.append(line)

    code = "".join(cleaned)

    # Fix version import in normalize.py
    code = code.replace(
        "from nl_calc import __version__", "# __version__ is defined at module level"
    )

    # Replace units module references with direct variable access
    # (since units code is inlined, not a separate module)
    code = code.replace("units.UNIT_BASE", "UNIT_BASE")
    code = code.replace("units.UNIT_ALIASES", "UNIT_ALIASES")
    code = code.replace("units.TEMPERATURE_CONVERSIONS", "TEMPERATURE_CONVERSIONS")
    code = code.replace("units._rebuild_conversions()", "_rebuild_conversions()")

    return code


def build_single_file(output_path=None):
    """Combine all nl_calc modules into a single file."""
    version = get_version()

    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "nl_calc.py")

    content = [HEADER]
    content.append(f'__version__ = "{version}"\n')
    content.append("# === units.py ===\n")
    content.append(get_module_code("units"))
    content.append("\n# === evaluator.py ===\n")
    content.append(get_module_code("evaluator"))
    content.append("\n# === normalize.py ===\n")
    content.append(get_module_code("normalize"))
    content.append("\n# === Entry point ===\n")
    content.append('if __name__ == "__main__":\n')
    content.append("    sys.exit(main())\n")

    final_content = "".join(content)

    with open(output_path, "w") as f:
        f.write(final_content)

    # Make executable
    os.chmod(output_path, os.stat(output_path).st_mode | 0o111)

    print(f"Built: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Build single-file nl_calc")
    parser.add_argument("-o", "--output", help="Output file path")
    args = parser.parse_args()

    build_single_file(args.output)


if __name__ == "__main__":
    main()
