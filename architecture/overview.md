# nl-calc Architecture Overview

A natural language math expression calculator that parses expressions in English (like "five plus three") and converts them to numeric results, with support for unit conversions.

## System Architecture

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                        CLI / API                         │
                    │                   (nl_calc/__main__.py)                  │
                    └──────────────────────────┬──────────────────────────────┘
                                               │
                    ┌──────────────────────────▼──────────────────────────────┐
                    │                    normalize.py                         │
                    │         (Natural Language → Python Expression)          │
                    │                                                              │
                    │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
                    │  │ Number Words │  │   Operators   │  │ Function Names │ │
                    │  │    "five"   │  │    "plus"    │  │  "square root" │ │
                    │  │     → 5     │  │     → +      │  │     → sqrt     │ │
                    │  └──────────────┘  └──────────────┘  └────────────────┘ │
                    └──────────────────────────┬──────────────────────────────┘
                                               │
                    ┌──────────────────────────▼──────────────────────────────┐
                    │                     evaluator.py                         │
                    │               (Python AST → Result)                     │
                    │                                                              │
                    │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
                    │  │    Math      │  │  Constants   │  │    Memory     │ │
                    │  │  Functions   │  │   (π, c, e)   │  │   (M, M+, MR) │ │
                    │  └──────────────┘  └──────────────┘  └────────────────┘ │
                    └──────────────────────────┬──────────────────────────────┘
                                               │
                    ┌──────────────────────────▼──────────────────────────────┐
                    │                       units.py                          │
                    │              (Unit Definitions & Conversions)           │
                    │                                                              │
                    │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
                    │  │  Length (m) │  │   Time (s)   │  │   Energy (J)  │ │
                    │  │  Mass (kg)  │  │    Data (B)  │  │  Temperature  │ │
                    │  └──────────────┘  └──────────────┘  └────────────────┘ │
                    └─────────────────────────────────────────────────────────┘
```

## Core Modules

### [normalize.py](normalize.md) — Natural Language Processing
**Purpose:** Converts natural language expressions to Python syntax

- Number word conversion (`"five"` → `5`)
- Operator word conversion (`"plus"` → `+`, `"minus"` → `-`)
- Function name normalization (`"square root"` → `sqrt`)
- Physical constant words (`"avogadro"` → `6.022e23`)
- Stripping of filler phrases (`"what's"`, `"calculate"`, etc.)
- Unit suffix parsing (`"30m"` → number with unit `m`)

**Key exports:** `run()`, `normalize()`, `normalize_expression()`, `main()`

### [evaluator.py](evaluator.md) — AST-Based Expression Evaluation
**Purpose:** Safely evaluates mathematical expressions using Python's AST

- Uses `ast.parse()` instead of `eval()` for security
- Built-in math functions: `sin`, `cos`, `tan`, `log`, `sqrt`, etc.
- Complex number support
- Statistical functions: `mean`, `median`, `std`, `variance`
- Bitwise operations
- Memory system (M, M+, M-, MR, MC)
- Variable storage (`setvar`, `getvar`, `delvar`)
- Caching and async evaluation
- Timeout and recursion depth limits

**Key exports:** `evaluate()`, `evaluate_raw()`, `evaluate_cached()`, `PyCalcApp`

### [units.py](units.md) — Unit Definitions and Conversions
**Purpose:** Provides comprehensive unit conversion support

- `UnitValue` class: represents numeric values with units
- Unit categories: length, mass, time, data, volume, pressure, energy, power, speed, temperature, etc.
- Conversion factors between units
- Temperature conversions (special handling for offset)
- Unit alias system for plurals and variations

**Key exports:** `UnitValue`, `get_conversion_factor()`, `is_unit()`, `get_all_units()`

### [__main__.py](../nl_calc/__main__.py) — CLI Entry Point
**Purpose:** Module entry point for `python -m nl_calc`

---

## exact/ — Unicode Text Primitives

Low-level deterministic Unicode text analysis tools. These modules are independent and testable without semantic interpretation.

```
exact/
├── primitives.py     # UTF-8, codepoints, normalization, invisibles
├── unicode_tools.py  # Script detection, confusables
├── measure.py        # Text metrics (words, lines, categories)
├── diff.py           # String diffing algorithms
├── validate.py       # JSON/bracket/regex validation
├── synthesis.py     # Higher-level text analysis
└── confusables.py   # Homoglyph identification (auto-generated)
```

### [primitives.py](exact/primitives.md)
Core text primitives built on Python's `unicodedata` module.

- `utf8_bytes()` — Raw UTF-8 encoded bytes
- `codepoints()` — Detailed codepoint information
- `normalize_unicode()` — NFC/NFD/NFKC/NFKD normalization
- `casefold_text()` — Case-insensitive comparison
- `raw_equal()` / `normalized_equal()` — String equality checks
- `find_invisibles()` — Detect hidden characters (ZWSP, BOM, etc.)
- `visible_repr()` — Display-safe representation
- `count_graphemes()` — Grapheme cluster counting

### [unicode_tools.py](exact/unicode_tools.md)
Unicode script and confusables detection.

- `unicode_script()` — Script of a character
- `detect_mixed_scripts()` — Detect mixed-script strings
- `detect_confusables()` — Find confusable homoglyphs
- `confusables_count()` — Fast confusable counting

### [measure.py](exact/measure.md)
Text metrics by category.

- `measure_basic()` — Basic metrics (bytes, codepoints, graphemes)
- `char_category_metrics()` — Metrics by Unicode category (Lu, Nd, Po, etc.)
- `line_metrics()` — Line count and newline style detection
- `word_metrics()` — Word count and boundaries

### [diff.py](exact/diff.md)
String comparison algorithms.

- `first_diff()` — Position of first difference
- `common_prefix_suffix()` — Longest common prefix/suffix
- `levenshtein_distance()` — Edit distance
- `diff_spans()` — Diff spans between strings
- `longest_common_subsequence()` — LCS via dynamic programming

### [validate.py](exact/validate.md)
Format validation.

- `check_brackets()` — Balanced bracket validation
- `validate_json()` — JSON syntax validation
- `regex_test()` — Test regex against samples

### [synthesis.py](exact/synthesis.md)
Higher-level text analysis combining primitives.

- `measure_text()` — Comprehensive text metrics
- `text_equal()` — String equality with multiple modes
- `inspect_text()` — Hidden character and confusable inspection
- `explain_diff()` — Detailed diff explanation
- `count_chars()` — Character counting/frequency
- `list_compare()` — Compare two lists

### [confusables.py](exact/confusables.md)
Auto-generated data file mapping confusable characters. ~180KB, ~6500 lines.

---

## mcp/ — Model Context Protocol Server

MCP server for AI agent tool access. Provides stdio-based interface to exact/ tools.

```
mcp/
├── schemas.py   # Tool input/output schemas
├── tools.py     # Tool implementations
└── server.py    # MCP protocol handler
```

### [schemas.py](mcp/schemas.md)
JSON schemas for MCP tools:

- `math_eval` — Evaluate math expressions
- `text_measure` — Measure text properties
- `text_equal` — Compare strings
- `text_diff_explain` — Explain string differences
- `text_inspect` — Inspect for hidden characters
- `text_count` — Character counting
- `text_truncate` — Truncate to grapheme
- `validate_brackets`, `validate_json`, `validate_regex` — Validation tools
- `list_compare` — List comparison

### [tools.py](mcp/tools.md)
Tool implementations wrapping exact/ functions with error handling, sanitization, and response envelopes.

### [server.py](mcp/server.md)
stdio-based MCP protocol implementation handling JSON-RPC requests.

---

## Build System

### [build_single.py](../build_single.py)
Combines all modules into a single `nl_calc.py` file for portability.

**Module groups:**
- `MODULES_CALC`: units, evaluator, normalize
- `MODULES_EXACT`: all exact/ modules
- `MODULES_MCP`: schemas, tools, server

**Output:** Self-contained executable with CLI and MCP modes.

### [install.py](../install.py)
Builds and installs `nl_calc.py` to `~/.local/bin/calc`.

---

## Data Flow

### Natural Language Evaluation (`run()`)
```
Input: "five plus three"
    ↓
normalize(): tokenize → convert words → parse units
    ↓
normalize_expression(): build Python syntax string "5+3"
    ↓
evaluator.evaluate(): AST parse → safe evaluation
    ↓
Output: 8
```

### Direct Evaluation (`evaluate()`)
```
Input: "5 + 3"
    ↓
evaluator.evaluate(): AST parse → safe evaluation
    ↓
Output: 8
```

### Unit Conversion (`run()`)
```
Input: "30m + 100ft in meters"
    ↓
normalize(): parse units, recognize "in" conversion
    ↓
evaluator: UnitValue(30, "m") + UnitValue(100, "ft")
    ↓
UnitValue.convert_to(): apply conversion factor
    ↓
Output: UnitValue(60.48, "m")
```

---

## Key Data Structures

| Structure | Module | Purpose |
|-----------|--------|---------|
| `NUMBER_WORDS` | normalize.py | Maps number values to word variants |
| `OPERATOR_CONVERSIONS` | normalize.py | Maps operator symbols to word forms |
| `FUNCTION_MAPPINGS` | normalize.py | Maps function name aliases to canonical names |
| `CONSTANT_WORDS` | normalize.py | Maps physical constant names to symbols |
| `UNIT_BASE` | units.py | Base units and their conversion factors |
| `UNIT_CONVERSIONS` | units.py | Cached pairwise conversion factors |
| `UNIT_ALIASES` | units.py | Maps unit variants to canonical forms |
| `get_unit_category` | units.py | Returns unit category (length, mass, etc.) |
| `UnitValue` | units.py | Numeric value with optional units |
| `Memory` | evaluator.py | Calculator memory registers |
| `TOOL_SCHEMAS` | mcp/schemas.py | MCP tool definitions |

---

## Processing Pipeline Summary

```
┌──────────────────────────────────────────────────────────────────────┐
│                         run() - Full Pipeline                         │
├──────────────────────────────────────────────────────────────────────┤
│  Input → Normalize → Tokenize → Unit Convert → Evaluate → Result      │
│     ↑                                                                  │
│     └── Handles NL ("five plus three"), unit syntax ("30m + 100ft")   │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                    evaluate() - Direct AST                            │
├──────────────────────────────────────────────────────────────────────┤
│  Input → AST Parse → Evaluate → Result                                 │
│     ↑                                                                   │
│     └── Expects valid Python syntax, NO normalization                  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Module Dependencies

```
__main__.py
    └── normalize.main()

normalize.py
    ├── evaluator.evaluate()
    ├── units.UnitValue, UNIT_ALIASES, is_unit
    └── exact (inspect_text, count_chars, regex_test)

evaluator.py
    └── units (UnitValue, UNIT_ALIASES, convert_temperature)

units.py (no dependencies on other nl_calc modules)

exact/
    ├── primitives.py (no dependencies)
    ├── unicode_tools.py → primitives
    ├── measure.py → primitives
    ├── diff.py → primitives
    ├── validate.py → primitives
    ├── synthesis.py → all exact modules
    └── confusables.py (data only)

mcp/
    ├── schemas.py (no dependencies)
    ├── tools.py → exact/, evaluator
    └── server.py → tools, schemas
```

---

## API Quick Reference

### CLI Usage
```bash
python -m nl_calc "five plus three"
python -m nl_calc "30m + 100ft"
python -m nl_calc -i  # Interactive REPL
```

### Library Usage
```python
from nl_calc import evaluate, run, UnitValue

# Direct math (valid Python syntax)
evaluate("5 + 3")  # → 8

# Natural language (requires run())
run("five plus three", NORMALIZE, PATTERNS)  # → 8

# Unit conversion
run("30m + 100ft", NORMALIZE, PATTERNS)  # → UnitValue(60.48, "m")
```

### MCP Server
```bash
python nl_calc.py --mcp
```