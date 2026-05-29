# nl-calc Architecture Overview

A natural language math expression calculator that parses expressions in English (like "five plus three") and converts them to numeric results, with support for unit conversions.

**All 629 tests pass.**

---

## Table of Contents

- [System Architecture](#system-architecture)
- [Core Modules](#core-modules)
  - [normalize.py](normalize.md) — Natural Language Processing
  - [evaluator.py](evaluator.md) — AST-Based Expression Evaluation
  - [units.py](units.md) — Unit Definitions and Conversions
  - [CLI Entry Point](cli.md)
- [exact/ — Unicode Text Primitives](exact.md)
  - [primitives.py](primitives.md)
  - [unicode_tools.py](unicode_tools.md)
  - [measure.py](measure.md)
  - [diff.py](diff.md)
  - [validate.py](validate.md)
  - [synthesis.py](synthesis.md)
  - [confusables.py](confusables.md)
- [mcp/ — Model Context Protocol Server](mcp.md)
  - [schemas.py](mcp.md#schemaspy)
  - [tools.py](mcp.md#toolspy)
  - [server.py](mcp.md#serverpy)
- [Build System](#build-system)
- [Data Flow](#data-flow)
- [Key Data Structures](#key-data-structures)
- [Module Dependencies](#module-dependencies)
- [Deep Dive Reviews](#deep-dive-reviews)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI / API                                │
│                   (nl_calc/__main__.py)                         │
└────────────────────────────────────┬────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────┐
│                      normalize.py                               │
│           (Natural Language → Python Expression)                │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ Number Words │  │   Operators   │  │  Function Names  │  │
│  │    "five"    │  │    "plus"     │  │  "square root"    │  │
│  │      → 5     │  │      → +      │  │      → sqrt       │  │
│  └──────────────┘  └──────────────┘  └────────────────────┘  │
└────────────────────────────────────┬────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────┐
│                      evaluator.py                               │
│                (Python AST → Result)                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │     Math     │  │  Constants   │  │       Memory       │  │
│  │  Functions   │  │   (π, c, e)   │  │      (M, M+, MR)   │  │
│  └──────────────┘  └──────────────┘  └────────────────────┘  │
└────────────────────────────────────┬────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────┐
│                        units.py                                 │
│               (Unit Definitions & Conversions)                   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │  Length (m)  │  │   Time (s)   │  │    Energy (J)     │  │
│  │  Mass (kg)   │  │   Data (B)    │  │   Temperature (K)  │  │
│  └──────────────┘  └──────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Modules

### [normalize.py](normalize.md) — Natural Language Processing

**File:** `nl_calc/normalize.py`

Converts natural language expressions to Python syntax.

| Feature | Example |
|---------|---------|
| Number word conversion | `"five"` → `5` |
| Operator word conversion | `"plus"` → `+`, `"minus"` → `-` |
| Function name normalization | `"square root"` → `sqrt` |
| Physical constant words | `"avogadro"` → `6.022e23` |
| Stripping of filler phrases | `"what's"`, `"calculate"`, etc. |
| Unit suffix parsing | `"30m"` → number with unit `m` |

**Key exports:** `run()`, `normalize()`, `normalize_expression()`, `main()`, `print_help()`, `NORMALIZE`, `PATTERNS`

**Detailed documentation:** [normalize.md](normalize.md)

---

### [evaluator.py](evaluator.md) — AST-Based Expression Evaluation

**File:** `nl_calc/evaluator.py`

Safely evaluates mathematical expressions using Python's AST module (NOT `eval()`).

| Feature | Description |
|---------|-------------|
| Math functions | `sin`, `cos`, `tan`, `log`, `sqrt`, etc. |
| Complex number support | Full complex arithmetic |
| Statistical functions | `mean`, `median`, `std`, `variance` |
| Bitwise operations | `bitand`, `bitor`, `bitxor`, etc. |
| Memory system | `M`, `M+`, `M-`, `MR`, `MC` |
| Variable storage | `setvar`, `getvar`, `delvar` |
| Physical constants | `pi`, `e`, `c`, `h`, `avogadro`, etc. |
| Caching and async | `evaluate_cached()`, `evaluate_async()` |

**Key exports:** `evaluate()`, `evaluate_raw()`, `evaluate_cached()`, `evaluate_async()`, `evaluate_with_timeout()`, `PyCalcApp`, `Evaluator`, `EvaluationError`, `TimeoutError`

**Detailed documentation:** [evaluator.md](evaluator.md)

---

### [units.py](units.md) — Unit Definitions and Conversions

**File:** `nl_calc/units.py`

Provides comprehensive unit conversion support.

| Unit Category | Examples |
|--------------|---------|
| Length | m, km, cm, mm, in, ft, yd, mi, ly, au, pc |
| Time | s, ms, us, ns, min, h, d, wk, yr |
| Mass | kg, g, mg, lb, oz, ton, stone |
| Data | B, KB, MB, GB, TB, PB (binary), bps, Kbps, Mbps (decimal) |
| Volume | L, mL, gal, qt, pt, cup, floz, tbsp, tsp |
| Pressure | Pa, kPa, MPa, GPa, bar, mbar, atm, psi |
| Energy | J, kJ, MJ, GJ, cal, kcal, Wh, kWh, BTU, eV |
| Power | W, kW, MW, GW, mW, hp |
| Speed | m/s, km/h, mph, kn, mach |
| Temperature | K, C, F, R (special handling) |

**Key exports:** `UnitValue`, `get_conversion_factor()`, `is_unit()`, `get_unit_category()`, `get_all_units()`

**Detailed documentation:** [units.md](units.md)

---

### [CLI Entry Point](cli.md)

**File:** `nl_calc/__main__.py`

Entry point for `python -m nl_calc`. Sets up `sys.path` and delegates to `normalize.main()`, which handles CLI parsing, interactive REPL, and MCP server mode.

**CLI documentation:** [cli.md](cli.md)

---

## exact/ — Unicode Text Primitives

Low-level deterministic Unicode text analysis tools. These modules are **independent** and **testable** without semantic interpretation.

```
nl_calc/exact/
├── __init__.py       # Public API re-exports
├── primitives.py     # UTF-8, codepoints, normalization, invisibles
├── unicode_tools.py  # Script detection, confusables
├── measure.py        # Text metrics (words, lines, categories)
├── diff.py           # String diffing algorithms
├── validate.py       # JSON/bracket/regex validation
├── synthesis.py     # Higher-level text analysis
└── confusables.py   # Homoglyph identification (auto-generated)
```

**Overview documentation:** [exact.md](exact.md)

---

### [primitives.py](primitives.md)

**File:** `nl_calc/exact/primitives.py`

Core text primitives built on Python's `unicodedata` module.

| Function | Returns | Description |
|----------|---------|-------------|
| `utf8_bytes(s)` | bytes | Raw UTF-8 encoded bytes |
| `codepoints(s)` | list[CodepointInfo] | Detailed codepoint information |
| `normalize_unicode(s, form)` | str | NFC/NFD/NFKC/NFKD normalization |
| `casefold_text(s)` | str | Case-insensitive comparison |
| `raw_equal(a, b)` | bool | Exact string equality |
| `normalized_equal(a, b)` | bool | Equality after NFC normalization |
| `measure_basic(s)` | MeasureBasic | Basic text metrics |
| `count_graphemes(s)` | int | Grapheme cluster count |
| `truncate_to_grapheme(s, max_graphemes)` | str | Truncate to grapheme boundary |
| `find_invisibles(s)` | list[InvisibleCharInfo] | Detect hidden characters |
| `visible_repr(s)` | str | Display-safe representation |

**Detailed documentation:** [primitives.md](primitives.md)

---

### [unicode_tools.py](unicode_tools.md)

**File:** `nl_calc/exact/unicode_tools.py`

Unicode script detection and confusable character identification.

| Function | Returns | Description |
|----------|---------|-------------|
| `unicode_script(char)` | str | Script of a character |
| `unicode_scripts(s)` | list[str] | Scripts for all characters |
| `detect_mixed_scripts(s)` | list[ScriptInfo] | Find mixed-script runs |
| `detect_confusables(s)` | list[ConfusableInfo] | Find confusable homoglyphs |
| `confusables_count(s)` | int | Fast confusable count |

**Supported scripts:** Latin, Greek, Cyrillic, Arabic, Hebrew, Han, Hiragana, Katakana, Thai, Hangul, etc.

**Detailed documentation:** [unicode_tools.md](unicode_tools.md)

---

### [measure.py](measure.md)

**File:** `nl_calc/exact/measure.py`

Text metrics by line, word, and character category.

| Function | Returns | Description |
|----------|---------|-------------|
| `char_category_metrics(s)` | CharCategoryMetrics | Metrics by Unicode category |
| `line_metrics(s)` | LineMetrics | Line count and newline style |
| `word_metrics(s)` | WordMetrics | Word count and boundaries |

**Detailed documentation:** [measure.md](measure.md)

---

### [diff.py](diff.md)

**File:** `nl_calc/exact/diff.py`

String comparison algorithms.

| Function | Returns | Description |
|----------|---------|-------------|
| `first_diff(a, b)` | FirstDiff | Position of first difference |
| `common_prefix_suffix(a, b)` | CommonPrefixSuffix | Longest common prefix/suffix |
| `levenshtein_distance(a, b)` | int | Edit distance |
| `diff_spans(a, b)` | list[DiffSpan] | Spans that differ |
| `longest_common_subsequence(a, b)` | str | LCS via dynamic programming |

**Detailed documentation:** [diff.md](diff.md)

---

### [validate.py](validate.md)

**File:** `nl_calc/exact/validate.py`

Format validation for JSON, brackets, and regex.

| Function | Returns | Description |
|----------|---------|-------------|
| `check_brackets(s)` | CheckBracketsResult | Balanced bracket validation |
| `validate_json(s)` | ValidateJsonResult | JSON syntax validation |
| `regex_test(pattern, samples)` | RegexTestResult | Test regex against samples |

**Detailed documentation:** [validate.md](validate.md)

---

### [synthesis.py](synthesis.md)

**File:** `nl_calc/exact/synthesis.py`

Higher-level text analysis combining primitives.

| Function | Returns | Description |
|----------|---------|-------------|
| `measure_text(s)` | MeasureTextResult | Comprehensive text metrics |
| `text_equal(a, b, ...)` | TextEqualResult | String equality modes |
| `inspect_text(s, ...)` | InspectTextResult | Hidden char inspection |
| `explain_diff(a, b, ...)` | ExplainDiffResult | Detailed diff explanation |
| `count_chars(s, ...)` | CountCharsResult | Character counting |
| `list_compare(a, b)` | dict | Compare two lists |

**Detailed documentation:** [synthesis.md](synthesis.md)

---

### [confusables.py](confusables.md)

**File:** `nl_calc/exact/confusables.py`

Auto-generated Unicode confusables table (~180KB, ~6580 lines) from UTS #39.

Maps confusable characters for homoglyph attack detection.

**Detailed documentation:** [confusables.md](confusables.md)

---

## mcp/ — Model Context Protocol Server

MCP server for AI agent tool access. Provides stdio-based interface to exact/ tools.

```
nl_calc/mcp/
├── __init__.py   # Package exports
├── schemas.py    # Tool input/output schemas
├── tools.py      # Tool implementations
└── server.py     # MCP protocol handler
```

**Overview documentation:** [mcp.md](mcp.md)

---

### schemas.py

**File:** `nl_calc/mcp/schemas.py`

JSON schemas for MCP tools and error envelope definitions.

| Tool | Description |
|------|-------------|
| `math_eval` | Evaluate arithmetic, unit conversions, constants |
| `text_measure` | Measure text properties |
| `text_equal` | Compare strings with multiple equality modes |
| `text_diff_explain` | Explain string differences |
| `text_inspect` | Inspect for hidden characters, confusables |
| `text_count` | Character counting |
| `text_truncate` | Truncate to grapheme boundary |
| `validate_brackets` | Check balanced brackets |
| `validate_json` | Validate JSON syntax |
| `validate_regex` | Test regex against samples |
| `list_compare` | Compare two lists |

---

### tools.py

**File:** `nl_calc/mcp/tools.py`

Tool implementations wrapping exact/ functions with error handling, sanitization, and response envelopes.

| Function | Wraps | Description |
|---------|-------|-------------|
| `math_eval()` | `evaluate_raw()` | Math evaluation |
| `text_measure()` | `measure_text()` | Text metrics |
| `text_equal()` | `text_equal()` | String comparison |
| `text_diff_explain()` | `explain_diff()` | Diff explanation |
| `text_inspect()` | `inspect_text()` | Hidden char inspection |
| `text_count()` | `count_chars()` | Char counting |
| `text_truncate()` | `truncate_to_grapheme()` | Truncation |
| `validate_brackets()` | `check_brackets()` | Bracket validation |
| `validate_json()` | `validate_json()` | JSON validation |
| `validate_regex()` | `regex_test()` | Regex testing |
| `list_compare()` | `list_compare()` | List comparison |

**Input limits:** MAX_TEXT_LENGTH=100,000, MAX_EXPRESSION_LENGTH=10,000, MAX_LIST_ITEMS=10,000

---

### server.py

**File:** `nl_calc/mcp/server.py`

stdio-based JSON-RPC 2.0 server implementation.

| Method | Description |
|--------|-------------|
| `initialize` | Returns protocol version, capabilities |
| `tools/list` | Lists available tools with schemas |
| `tools/call` | Executes a tool |
| `notifications/initialized` | No-op acknowledgment |

**Error codes:** -32600 (InvalidRequest), -32601 (Method not found), -32602 (Invalid params), -32000 (Server error)

---

## Build System

### [build_single.py](../build_single.py)

Combines all modules into a single `nl_calc.py` file for portability.

**Module groups:**
- `MODULES_CALC`: units, evaluator, normalize
- `MODULES_EXACT`: all exact/ modules
- `MODULES_MCP`: schemas, tools, server

**Output:** Self-contained executable (~394KB) with CLI and MCP modes.

### [install.py](../install.py)

Builds and installs `nl_calc.py` to `~/.local/bin/calc`.

```bash
python install.py --install     # Install
python install.py --update      # Update
python install.py --uninstall   # Remove
```

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
| `normalize_unit` | units.py | Convert unit name to canonical form |
| `get_unit_category` | units.py | Returns unit category (length, mass, etc.) |
| `are_units_compatible` | units.py | Check if two units can be combined |
| `UnitValue` | units.py | Numeric value with optional units |
| `Memory` | evaluator.py | Calculator memory registers |
| `TOOL_SCHEMAS` | mcp/schemas.py | MCP tool definitions |

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

## Deep Dive Reviews

Detailed review documents for focused code review:

| Module | Review Document |
|--------|----------------|
| normalize.py | [plans/normalize_review.md](plans/normalize_review.md) |
| evaluator.py | [plans/evaluator_review.md](plans/evaluator_review.md) |
| units.py | [plans/units_review.md](plans/units_review.md) |
| exact/primitives.py | [plans/primitives_review.md](plans/primitives_review.md) |
| exact/unicode_tools.py | [plans/unicode_tools_review.md](plans/unicode_tools_review.md) |
| exact/measure.py | [plans/measure_review.md](plans/measure_review.md) |
| exact/diff.py | [plans/diff_review.md](plans/diff_review.md) |
| exact/validate.py | [plans/validate_review.md](plans/validate_review.md) |
| exact/synthesis.py | [plans/synthesis_review.md](plans/synthesis_review.md) |
| exact/confusables.py | [plans/confusables_review.md](plans/confusables_review.md) |
| mcp/server.py | [plans/mcp_server_review.md](plans/mcp_server_review.md) |
| CLI | [plans/cli_review.md](plans/cli_review.md) |

**Master review plan:** [review_plan.md](review_plan.md)

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