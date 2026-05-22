# Overview Module Architecture Review - Improvement Plan

## Review Summary

Reviewed `architecture/overview.md` against individual module documentation to identify discrepancies between documented and actual architecture.

---

## Verified Claims

### Core Modules
1. **normalize.py** - Exports correctly documented: `run()`, `normalize()`, `normalize_expression()`, `main()`, `NORMALIZE`, `PATTERNS`, `MAX_INPUT_LENGTH`, `MAX_NESTING_DEPTH`
2. **evaluator.py** - Exports correctly documented: `evaluate()`, `evaluate_raw()`, `evaluate_cached()`, `PyCalcApp`, memory functions, variable functions
3. **units.py** - Exports correctly documented: `UnitValue`, `get_conversion_factor()`, `is_unit()`, `get_all_units()`, plus additional `get_unit_category()`
4. **__main__.py** - Correctly delegates to `normalize.main()`

### exact/ Module Structure
- Directory structure matches: `primitives.py`, `unicode_tools.py`, `measure.py`, `diff.py`, `validate.py`, `synthesis.py`, `confusables.py`
- `__init__.py` properly re-exports functions from submodules

### Data Flow Description
- `run()` pipeline correctly described (normalize → tokenize → unit convert → evaluate)
- `evaluate()` correctly described as direct AST (no normalization)
- Unit conversion flow correctly documented

### Module Dependencies
- Dependencies graph correctly shows:
  - `normalize.py` depends on `evaluator.py` and `units.py`
  - `units.py` has no dependencies on other nl_calc modules
  - `exact/` modules are independent

---

## Discrepancies

### High Priority

**1. `unicode_scripts()` - Documented but not exported**
- **Overview line 123**: Documents `unicode_scripts()` function
- **Actual**: Function exists in `unicode_tools.py:123` but is NOT re-exported in `__init__.py`
- **Impact**: Users cannot import this function; docs reference it but code doesn't support it

**2. `confusables_count()` - Documented but not exported**
- **Overview line 123**: Documents `confusables_count()` function
- **Actual**: Function exists in `unicode_tools.py:218` but is NOT re-exported in `__init__.py`
- **Impact**: Users cannot import this function

**3. `longest_common_subsequence()` - Documented but not exported**
- **Overview line 140**: Documents `longest_common_subsequence()` in diff.py
- **Actual**: Function exists in `diff.py:164` but is NOT re-exported in `__init__.py`
- **Impact**: Users cannot import this function

### Medium Priority

**4. `evaluate_raw()` - Incomplete description**
- **Overview line 219**: "Evaluates with NL normalization (calls `normalize_expression` first)"
- **Actual**: Documentation omits that `evaluate_raw()` is a standalone function not requiring `NORMALIZE`/`PATTERNS` parameters (it loads them internally via `_ensure_config_loaded()`)
- **Impact**: Minor confusion about API usage

**5. `get_unit_category()` - Documented in units.md but not in overview**
- **Overview table (line 262)**: Lists only `UnitValue` for units.py
- **Actual**: `get_unit_category()` exists and is exported (verified)
- **Impact**: Incomplete view of units.py API

### Low Priority

**6. `SuccessEnvelope` - Documented but unused**
- **Overview line 41-44**: Documents `SuccessEnvelope` TypedDict
- **Actual**: Defined in `schemas.py` but never imported or used in `tools.py`
- **Impact**: Documentation references a type that has no actual usage in codebase

**7. Line counts for confusables.py**
- **Overview line 160**: "~6500 lines"
- **Actual**: ~6581 lines
- **Impact**: Minor inaccuracy

---

## Improvements with Priority

### High Priority

| # | Issue | Fix | Files Affected |
|---|-------|-----|----------------|
| H1 | Add `unicode_scripts` to `__init__.py` exports | Add `unicode_scripts` to re-exports from `unicode_tools` | `nl_calc/exact/__init__.py` |
| H2 | Add `confusables_count` to `__init__.py` exports | Add `confusables_count` to re-exports from `unicode_tools` | `nl_calc/exact/__init__.py` |
| H3 | Add `longest_common_subsequence` to `__init__.py` exports | Add `longest_common_subsequence` to re-exports from `diff` | `nl_calc/exact/__init__.py` |

### Medium Priority

| # | Issue | Fix | Files Affected |
|---|-------|-----|----------------|
| M1 | Document `evaluate_raw()` behavior more accurately | Update evaluator.md to clarify it loads config internally | `architecture/evaluator.md` |
| M2 | Add `get_unit_category()` to overview's Key Data Structures table | Add row for the function | `architecture/overview.md` line ~262 |

### Low Priority

| # | Issue | Fix | Files Affected |
|---|-------|-----|----------------|
| L1 | Remove or mark `SuccessEnvelope` as unused | Either remove from docs or note it's defined but unused | `architecture/mcp.md`, `architecture/overview.md` |
| L2 | Correct confusables.py line count | Update "~6500 lines" to "~6580 lines" | `architecture/overview.md` line 160, `architecture/confusables.md` |

---

## Implementation Notes

The missing exports (H1-H3) appear to be genuine omissions - the `__all__` list in `__init__.py` includes these names but the actual re-export statements don't include them. This is a bug in the module's public API.

```python
# Current (broken):
__all__ = [
    ...
    "unicode_scripts",   # Listed but not actually imported
    "confusables_count", # Listed but not actually imported
    ...
]

# Should add:
from .unicode_tools import (
    ...
    unicode_scripts,
    confusables_count,
)
```