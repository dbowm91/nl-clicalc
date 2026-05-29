# AGENTS.md

## Overview
`nl-clicalc` is a natural language math expression calculator that uses only Python's standard library. It parses math expressions in English (like "five plus three") and converts them to numeric results, with support for unit conversions.

## Architecture

### Build Process
The codebase is designed to be assembled into a **single self-contained Python script** for portability:

1. **`build_single.py`** - Combines modules into `nl_calc.py`:
   - `units.py` - Unit definitions and conversion factors
   - `evaluator.py` - AST-based expression evaluation
   - `normalize.py` - Natural language processing
   - `__main__.py` - CLI entry point

2. **`install.py`** - Calls `build_single.py` then installs the result to `~/.local/bin/calc`

**Critical:** When modifying the codebase, ensure changes work with `build_single.py` assembling everything into one file. All code must be in one of the four core modules.

### Processing Pipeline
Understanding the two evaluation paths is critical:

1. **`run()` (full pipeline)** - `normalize.py` processes input first, then passes to evaluator:
   ```
   Input → Normalization → Tokenization → Unit Conversion → Evaluation → Result
   ```
   - Handles natural language ("five plus three")
   - Handles unit syntax ("30m + 100ft")
   - Uses `evaluate()` internally after normalization

2. **`evaluate()` (direct AST)** - Skips normalization, directly parses via Python AST:
   ```
   Input → Python AST Parse → Evaluation → Result
   ```
   - Expects valid Python syntax
   - Does NOT handle NL input
   - Does NOT handle unit suffixes like "km" or "m"

**Example of what each handles:**
```python
run("five plus three", NORMALIZE, PATTERNS)  # ✓ Works
run("30m + 100ft", NORMALIZE, PATTERNS)      # ✓ Works
evaluate("5 + 3")                            # ✓ Works
evaluate("five plus three")                  # ✗ Fails (invalid Python)
evaluate("1km in m")                         # ✗ Fails (invalid Python)
```

### Core Modules

| Module | Purpose |
|--------|---------|
| `nl_calc/normalize.py` | NL tokenization, number word conversion, expression normalization |
| `nl_calc/evaluator.py` | AST parsing and evaluation, mathematical operations |
| `nl_calc/units.py` | Unit definitions, conversion factors, temperature conversions |
| `nl_calc/__main__.py` | CLI interface |

### Supporting Modules (exact/)

Located in `nl_calc/exact/` - Provides low-level Unicode text primitives for detecting hidden characters, confusables, and text metrics:

| Module | Purpose |
|--------|---------|
| `primitives.py` | UTF-8 encoding, codepoint iteration, Unicode normalization |
| `unicode_tools.py` | Script detection, confusable character detection |
| `confusables.py` | Confusable character identification (homoglyphs) - large file (~180KB) |
| `validate.py` | JSON/bracket/regex validation |
| `diff.py` | String diffing algorithms |
| `measure.py` | Text metrics (words, lines, categories) |
| `synthesis.py` | Higher-level text analysis tools |

### Supporting Modules (mcp/)

Located in `nl_calc/mcp/` - Model Context Protocol server for AI agent tool access:

| Module | Purpose |
|--------|---------|
| `server.py` | MCP server implementation, stdio-based request handling |
| `tools.py` | MCP tool definitions |
| `schemas.py` | JSON schemas for MCP tool definitions |

### Key Data Structures

- **`NUMBER_WORDS`** - Dictionary mapping number values to word variants ("one", "five", etc.)
- **`OPERATOR_CONVERSIONS`** - Maps operator words to symbols ("plus" → "+")
- **`FUNCTION_MAPPINGS`** - Maps function name variants to canonical names (e.g., "square root" → "sqrt")
- **`CONSTANT_WORDS`** - Maps physical constant names (avogadro, planck, etc.) to symbols
- **`STRIPPED_PHRASES`** - Filler words removed during normalization ("what's", "calculate", etc.)
- **`UNIT_BASE`** - Base units and their conversion factors
- **`UNIT_CONVERSIONS`** - Cached pairwise conversion factors
- **`UNIT_ALIASES`** - Maps all unit variants to canonical forms

## Guardrails

### Dependencies
- **Standard library only** - No external packages allowed
- All imports must be from: `argparse`, `os`, `sys`, `re`, `math`, `ast`, `functools`, `typing`, `stat`, `shutil`, `subprocess`, `traceback`

### Typing
- Use type annotations for function signatures
- Use `Mapping[str, Pattern]` from `typing` for pattern collections
- Return types must be declared

### Testing
- All tests must pass (`python -m pytest tests/`)
- New tests must use the correct API:
  - For NL/unit functionality → use `run()` or test through CLI
  - For pure math expressions → use `evaluate()`
- 631 tests currently pass (as of last run)

### Code Style
- Follow existing patterns in the codebase
- Use `lru_cache` for expensive operations that can be memoized
- All code must work when inlined by `build_single.py`

## Working with Tests

### Current Test Structure
```
tests/
├── conftest.py              # Shared fixtures
├── test_clicalc.py          # Core functional tests
├── test_security_fuzz.py    # Security/fuzz tests
├── test_tokenization.py     # Tokenization edge cases
├── test_math_identities.py  # Mathematical laws verification
├── test_mcp_server.py       # MCP server integration tests
├── test_exact.py            # Exact module tests
└── test_cli_text.py         # CLI text tools tests
```

### API Usage Reminder
- `evaluate("five plus three")` → Fails (invalid Python syntax)
- `evaluate("1km in m")` → Fails (invalid Python syntax)
- `evaluate("30m + 100ft")` → Fails (invalid Python syntax)

These work through `run()` because normalization converts NL to Python first.

**When writing tests:**
1. For mathematical operations (`5+3`, `2**10`) → `evaluate()`
2. For natural language (`"five plus three"`) → Use CLI or `run()`
3. For unit conversions with operators → Use CLI or `run()`
4. Direct unit suffix parsing (`"1km"`) does not work with `evaluate()`

### Helper Patterns
```python
def get_value(result):
    """Extract numeric value from result, handling UnitValue."""
    if isinstance(result, UnitValue):
        return result.value
    return result

def val(expr):
    """Evaluate and extract value, handling UnitValue."""
    result = evaluate(expr)
    if isinstance(result, UnitValue):
        return result.value
    return result
```

## Common Patterns

### Adding a New Math Function
1. Add to `FUNCTION_MAPPINGS` in `normalize.py`
2. Implement in `evaluator.py`
3. Add test in `test_clicalc.py`

### Adding a New Unit
1. Add to appropriate category in `UNIT_BASE` in `units.py`
2. Rebuild `UNIT_CONVERSIONS` cache (automatic)
3. Add test via CLI or `run()`

### Adding Number Word Support
1. Add word to `NUMBER_WORDS` in `normalize.py`
2. The normalization pipeline handles word-to-number conversion

## File Locations

- **CLI entry**: `nl_calc/__main__.py`
- **Normalize functions**: `nl_calc/normalize.py` (1525 lines)
- **Evaluator functions**: `nl_calc/evaluator.py`
- **Unit definitions**: `nl_calc/units.py` (lines 145-600)
- **Tests**: `tests/`
- **Build script**: `build_single.py`
- **Install script**: `install.py`
- **Active plan**: `plans/plan.md`

## Debugging Tips

### Checking what `evaluate()` returns
```python
from nl_calc import evaluate, UnitValue
result = evaluate("5 + 3")
print(f"Type: {type(result)}, Value: {result}")
if isinstance(result, UnitValue):
    print(f"Unit: {result.unit}, Value: {result.value}")
```

### Checking normalization
```python
from nl_calc.normalize import normalize, NORMALIZE, PATTERNS
normalized = normalize("five plus three", NORMALIZE, PATTERNS)
print(f"Normalized: {normalized}")  # Should show "5+3"
```

### Checking unit conversion
```python
from nl_calc.units import get_conversion_factor
factor = get_conversion_factor("km", "m")
print(f"km to m factor: {factor}")  # Should be 1000.0
```

## Implementation Notes

### exact/ Module Conventions
- **`utf8_bytes()` returns `bytes`** - Not an int count, returns actual UTF-8 encoded bytes
- **`visible_repr()` display order matters** - Variation selector checks must come BEFORE combining mark checks (U+FE00-U+FE0F should be checked before category 'M'). The code at primitives.py:273-276 is correct.
- **WORD JOINER (U+2060)** - Now handled by `_INVISIBLE_CHARS` dict lookup, redundant explicit check removed
- **Newline detection `mixed` value** - The `mixed` newline style can be returned but was not properly detected in original implementation
- **`_get_script_heuristic()` benefits from caching** - Now has `@functools.lru_cache` decorator
- **Cf (format) characters intentionally excluded** - `control_chars` in `measure.py` excludes `Cf` category; format characters are silently ignored per UTS #55
- **confusables.py is a data file** - The file `nl_calc/exact/confusables.py` is auto-generated data only (~176KB, 6580 lines). TypedDict classes are in their logical modules, NOT in confusables.py
- **`confusables_count()` helper** - Fast function to count confusables without building full list (unicode_tools.py)
- **`reverse_confusables()` helper** - Given a character, returns all characters that confusable-map TO it using a cached inverted index (unicode_tools.py)
- **`unicode_scripts()` batch function** - Returns script list for all chars in string (unicode_tools.py)
- **`longest_common_subsequence()`** - Implemented in diff.py using dynamic programming
- **`accent_or_diacritic_difference` classification** - Returned when NFC equal but casefold differs (e.g., "café" vs "cafe\u0301"). This IS reachable - verified with precomposed vs decomposed forms.
- **`common_prefix_suffix()` examples fixed** - Docstring now has working examples showing overlap prevention behavior
- **validate.py input limits** - `MAX_INPUT_LENGTH = 100_000` enforced in `check_brackets()` and `validate_json()`, raises `ValueError`
- **`_INVISIBLE_CHARS` contains 22 characters** - Documentation only shows 12; missing: U+180e, U+034f, U+202b-202e, U+2066-2069

### TypedDict vs NamedTuple
- Architecture docs may show `@dataclass class Xxx(NamedTuple)` but code uses `class Xxx(TypedDict)`
- TypedDict is used throughout for consistency with Python 3.14+ typing patterns
- Always check actual code for exact return type signatures
- **TypedDict classes do NOT support `__slots__`** - Only regular classes (with actual implementations) support `__slots__`

### MCP Server Conventions
- Tool names in `schemas.py` and `server.py` are now unified via `TOOL_SCHEMAS`
- Response handling is now consistent - `math_eval` returns direct result dict
- `MAX_TEXT_LENGTH` is enforced on `math_eval` tool
- Error messages are sanitized for non-ASCII characters
- Case-insensitive tool matching with suggestions for unknown tools
- `mcp_main` is defined in `server.py:234` as `mcp_main = main`

### Unit Conversion Conventions
- Prefixed units like `kN`, `mV`, `mA` map to themselves in `UNIT_ALIASES`
- Temperature conversions use offset math, not multiplicative factors
- `mps` (meters per second) is in `UNIT_CATEGORIES` as "speed"

## Deferred Items

The implementation plan at `plans/plan.md` has been pruned. All 35 original items are complete. Deferred items for design review remain in plan.md.

(End of file)
