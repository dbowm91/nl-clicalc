#!/usr/bin/env python3
"""
Build script to combine nl_calc modules into a single self-contained executable.

Supports both CLI mode (calculator) and MCP server mode (--mcp flag).

Usage:
    python3 build_single.py          # Build nl_calc.py in current directory
    python3 build_single.py -o /path/to/output  # Custom output path
"""

from __future__ import annotations

import argparse
import os
import sys


NL_CALC_DIR = os.path.join(os.path.dirname(__file__), "nl_calc")

MODULES_CALC = [
    "units",
    "evaluator",
    "normalize",
]

MODULES_EXACT = [
    "exact/primitives",
    "exact/diff",
    "exact/validate",
    "exact/measure",
    "exact/unicode_tools",
    "exact/synthesis",
    "exact/confusables",
]

MODULES_MCP = [
    "mcp/schemas",
    "mcp/tools",
    "mcp/server",
]

ALL_MODULES = MODULES_CALC + MODULES_EXACT + MODULES_MCP

HEADER = '''#!/usr/bin/env python3
from __future__ import annotations

"""
nl_calc - Natural language math expression calculator + MCP exact tools

Single-file version.

CLI mode:     python3 nl_calc.py "five plus two"
MCP mode:     python3 nl_calc.py --mcp

Or make executable: chmod +x nl_calc.py && ./nl_calc.py "five plus two"
"""

import sys
import os

os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"

'''


def get_version() -> str:
    """Get version from __init__.py"""
    init_path = os.path.join(NL_CALC_DIR, "__init__.py")
    with open(init_path, "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"')
    return "1.0.0"


def get_module_code(module_name: str) -> tuple[str, list[str]]:
    """Extract code from a module, removing docstring and imports that will be inlined.

    Handles nested paths like 'exact/primitives' or 'mcp/tools'.

    Returns:
        Tuple of (cleaned_code, list_of_import_statements)
    """
    module_path = os.path.join(NL_CALC_DIR, f"{module_name}.py")

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

    # Modules being inlined (for import cleaning)
    inlined_modules = set()
    for mod in ALL_MODULES:
        if "/" in mod:
            pkg, name = mod.split("/")
            inlined_modules.add(f"{pkg}.{name}")
        else:
            inlined_modules.add(mod)

    # Collect imports separately
    imports: list[str] = []
    cleaned: list[str] = []
    in_main_block = False
    in_multiline_import = False

    def is_relative_import_stripped(stripped: str) -> bool:
        """Check if a relative import should be skipped because module is inlined."""
        for mod in ALL_MODULES:
            if "/" in mod:
                pkg, name = mod.split("/")
                if f"from .{pkg}.{name} import" in stripped or f"from .{name} import" in stripped:
                    return True
            elif f"from .{stripped.split('.')[1]} import" in stripped:
                return True
        return False

    def should_replace_import(stripped: str) -> bool:
        """Check if this import should be replaced rather than skipped."""
        if "import _default_evaluator" in stripped:
            return True
        if "from .units import" in stripped:
            return True
        if "from .evaluator import" in stripped:
            return True
        if "from .normalize import" in stripped:
            return True
        return False

    def is_valid_single_line_import(stripped: str) -> bool:
        """Check if this is a valid single-line import to collect."""
        # Must start with "import " or "from "
        if not (stripped.startswith("import ") or stripped.startswith("from ")):
            return False
        # Skip __future__ imports
        if "__future__" in stripped:
            return False
        # Skip relative imports (they reference inlined modules)
        if stripped.startswith("from ."):
            return False
        # Skip nl_calc imports (package reference)
        if "nl_calc" in stripped:
            return False
        # Must be a complete single-line import (ends without_open paren, no backslash)
        if "(" in stripped or ")" in stripped:
            return False
        if "\\" in stripped:
            return False
        return True

    for i, line in enumerate(code_lines):
        stripped = line.strip()

        # Check if we're entering a multi-line import (skip until closed)
        if ("from " in stripped or stripped.startswith("import ")) and "(" in stripped and ")" not in stripped:
            in_multiline_import = True
            continue

        # Handle multi-line imports - skip until closed
        if in_multiline_import:
            if ")" in stripped:
                in_multiline_import = False
            continue

        # Handle relative imports
        if stripped.startswith("from ."):
            if is_relative_import_stripped(stripped):
                continue
            if should_replace_import(stripped):
                continue
            # Skip other relative imports
            continue

        # Remove __future__ imports (will be inlined once)
        if "from __future__" in line:
            continue

        # Handle simple "import X" statements - collect them
        if stripped.startswith("import ") and not stripped.startswith("import nl_calc"):
            if is_valid_single_line_import(stripped):
                imports.append(line)
            continue

        # Handle simple "from X import" statements that are NOT relative or inlined
        if stripped.startswith("from ") and " import " in stripped:
            if is_valid_single_line_import(stripped):
                imports.append(line)
            continue

        # Skip if __name__ == "__main__" blocks
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

    # Handle cross-module references within packages being inlined

    # Units module references
    code = code.replace("units.UNIT_BASE", "UNIT_BASE")
    code = code.replace("units.UNIT_ALIASES", "UNIT_ALIASES")
    code = code.replace("units.TEMPERATURE_CONVERSIONS", "TEMPERATURE_CONVERSIONS")
    code = code.replace("units._rebuild_conversions()", "_rebuild_conversions()")

    # Normalize references to modules now inlined
    code = code.replace("from nl_calc import __version__", "# __version__ is defined at module level")

    # Rename normalize.main() to normalize_main() to avoid conflict with MCP main()
    if '"""Main entry point for CLI."""' in code:
        code = code.replace("def main() -> int:", "def normalize_main() -> int:")

    # Exact module internal references (within exact package)
    # These are relative imports that now become direct
    code = code.replace("from .primitives import", "from primitives import")
    code = code.replace("from .diff import", "from diff import")
    code = code.replace("from .validate import", "from validate import")
    code = code.replace("from .measure import", "from measure import")
    code = code.replace("from .unicode_tools import", "from unicode_tools import")
    code = code.replace("from .synthesis import", "from synthesis import")
    code = code.replace("from .confusables import", "from confusables import")

    # MCP module internal references
    code = code.replace("from .schemas import", "from schemas import")
    code = code.replace("from .tools import", "from tools import")
    code = code.replace("from .server import", "from server import")

    # Rename MCP server main to mcp_main to avoid conflict with normalize.main()
    # Only replace when it's specifically the MCP server main (has MCP docstring)
    if '"""Main entry point for MCP server.' in code:
        code = code.replace("def main() -> int:", "def mcp_main() -> int:")

    # Exact imports into synthesis
    code = code.replace("from ..exact import", "from exact import")

    # MCP imports from nl_calc
    code = code.replace("from .. import EvaluationError, evaluate_raw", "from evaluator import EvaluationError, evaluate_raw")
    code = code.replace("from ..exact import", "from exact import")

    # Synthesis imports from exact submodules
    code = code.replace(
        "from .primitives import (",
        "# primitives imports handled inline"
    )
    code = code.replace(
        "from .unicode_tools import (",
        "# unicode_tools imports handled inline"
    )
    code = code.replace(
        "from .diff import (",
        "# diff imports handled inline"
    )
    code = code.replace(
        "from .validate import (",
        "# validate imports handled inline"
    )
    code = code.replace(
        "from .measure import (",
        "# measure imports handled inline"
    )
    code = code.replace(
        "from .synthesis import (",
        "# synthesis imports handled inline"
    )

    # Rename aliased primitives imports in synthesis to their actual names
    # (since they're now in the same file and not imported)
    code = code.replace("_measure_basic(", "measure_basic(")
    code = code.replace("_char_category_metrics(", "char_category_metrics(")
    code = code.replace("_line_metrics(", "line_metrics(")
    code = code.replace("_word_metrics(", "word_metrics(")
    code = code.replace("_find_invisibles(", "find_invisibles(")
    code = code.replace("_casefold_text(", "casefold_text(")
    code = code.replace("_normalize_unicode(", "normalize_unicode(")
    code = code.replace("_normalized_equal(", "normalized_equal(")
    code = code.replace("_raw_equal(", "raw_equal(")
    code = code.replace("_visible_repr(", "visible_repr(")
    code = code.replace("_detect_confusables(", "detect_confusables(")
    code = code.replace("_detect_mixed_scripts(", "detect_mixed_scripts(")
    code = code.replace("_common_prefix_suffix(", "common_prefix_suffix(")
    code = code.replace("_diff_spans(", "diff_spans(")
    code = code.replace("_first_diff(", "first_diff(")
    code = code.replace("_levenshtein_distance(", "levenshtein_distance(")

    return code, imports


def build_single_file(output_path: str | None = None) -> str:
    """Combine all nl_calc modules into a single file."""
    version = get_version()

    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "nl_calc.py")

    content: list[str] = [HEADER]
    content.append(f'__version__ = "{version}"\n')

    # Collect all imports from all modules
    all_imports: list[str] = []
    all_module_code: list[str] = []

    # Core calculator modules
    for mod in MODULES_CALC:
        code, imports = get_module_code(mod)
        all_module_code.append(f"\n# === {mod}.py ===\n")
        all_module_code.append(code)
        all_imports.extend(imports)

    # Exact text tools
    all_module_code.append("\n# === Exact text tools ===\n")
    for mod in MODULES_EXACT:
        code, imports = get_module_code(mod)
        all_module_code.append(f"\n# === {mod}.py ===\n")
        all_module_code.append(code)
        all_imports.extend(imports)

    # MCP server
    all_module_code.append("\n# === MCP server ===\n")
    for mod in MODULES_MCP:
        code, imports = get_module_code(mod)
        all_module_code.append(f"\n# === {mod}.py ===\n")
        all_module_code.append(code)
        all_imports.extend(imports)

    # Deduplicate imports while preserving order
    seen: set[str] = set()
    unique_imports: list[str] = []
    for imp in all_imports:
        # Normalize for deduplication (strip whitespace and indentation)
        normalized = imp.strip()
        if normalized not in seen:
            seen.add(normalized)
            # Strip any leading indentation so imports are at column 0
            unique_imports.append(normalized + "\n")

    # Add unique imports at the top (after header)
    if unique_imports:
        content.append("\n# === Collected imports ===\n")
        content.extend(unique_imports)
        content.append("\n")

    # Add module code
    content.extend(all_module_code)

    # Combined entry point
    content.append("\n# === Entry point ===\n")
    content.append("""
# NOTE: All modules are inlined into this file.
# Functions are available in global scope - no import needed.

def _main():
    import argparse
    import sys
    parser = argparse.ArgumentParser(description="nl_calc - Natural language calculator + MCP server")
    parser.add_argument("--mcp", action="store_true", help="Run as MCP server")
    parser.add_argument("expression", nargs="*", help="Math expression to evaluate")
    parser.add_argument("-e", "--expression", dest="single_expr", metavar="<expr>", help="Evaluate a single expression (useful for piping)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress expression in output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--usage", action="store_true", help="Show full usage information and examples")
    args = parser.parse_args()

    if args.mcp:
        return mcp_main()
    elif args.usage:
        print_help()
        return 0
    elif args.expression or args.single_expr:
        sys.argv = ["nl_calc"]
        if args.single_expr:
            sys.argv.extend(["-e", args.single_expr])
        else:
            sys.argv.extend(args.expression)
        if args.json:
            sys.argv.append("--json")
        if args.quiet:
            sys.argv.append("-q")
        return normalize_main()
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    raise SystemExit(_main())
""")

    final_content = "".join(content)

    with open(output_path, "w") as f:
        f.write(final_content)

    os.chmod(output_path, os.stat(output_path).st_mode | 0o111)

    print(f"Built: {output_path}")
    print(f"  Core modules: {len(MODULES_CALC)}")
    print(f"  Exact modules: {len(MODULES_EXACT)}")
    print(f"  MCP modules: {len(MODULES_MCP)}")
    print(f"  Unique imports: {len(unique_imports)}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Build single-file nl_calc")
    parser.add_argument("-o", "--output", help="Output file path")
    args = parser.parse_args()

    build_single_file(args.output)


if __name__ == "__main__":
    main()
