# Review: normalize.py Module Architecture

**Date:** 2026-05-22
**Reviewer:** Architecture Review
**Files Reviewed:**
- `architecture/normalize.md`
- `nl_calc/normalize.py`

---

## 1. Verified Claims (with Code References)

### Module Exports ✅
| Export | Status | Location |
|--------|--------|----------|
| `run` | ✅ Exists | `normalize.py:959` |
| `normalize` | ✅ Exists | `normalize.py:745` |
| `normalize_expression` | ✅ Exists | `normalize.py:912` |
| `main` | ✅ Exists | `normalize.py:1226` |
| `print_help` | ✅ Exists | `normalize.py:1059` |
| `NORMALIZE` | ✅ Exists | `normalize.py:379` |
| `PATTERNS` | ✅ Exists | `normalize.py:379` |
| `MAX_INPUT_LENGTH` | ✅ Exists (10000) | `normalize.py:42` |
| `MAX_NESTING_DEPTH` | ✅ Exists (100) | `normalize.py:43` |
| `evaluate` | ✅ Re-exported | `normalize.py:28` (imported from evaluator) |
| `EvaluationError` | ✅ Re-exported | `normalize.py:29` (imported from evaluator) |
| `UnitValue` | ✅ Re-exported | `normalize.py:30` (imported from units) |

**Note:** `__all__` exports `evaluate`, `EvaluationError`, `UnitValue` which are not defined in this module but re-exported from dependencies. This is undocumented.

### Data Structures ✅
| Structure | Status | Location |
|-----------|--------|----------|
| `OPERATOR_CONVERSIONS` | ✅ Exists, matches doc | `normalize.py:101-119` |
| `FUNCTION_MAPPINGS` | ✅ Exists, matches doc | `normalize.py:123-217` |
| `NUMBER_WORDS` | ✅ Exists, matches doc | `normalize.py:220-261` |
| `CONSTANT_WORDS` | ✅ Exists, matches doc | `normalize.py:279-300` |
| `STRIPPED_PHRASES` | ✅ Exists, matches doc | `normalize.py:264-276` |
| `_UNITS_BY_LENGTH` | ✅ Exists (list) | `normalize.py:46` |
| `_COMMON_UNITS` | ✅ Exists (list) | `normalize.py:49-91` |
| `_UNIT_PREFIXES` | ✅ Exists (set) | `normalize.py:94-97` |

### Core Functions ✅
| Function | Status | Location |
|----------|--------|----------|
| `normalize(text, NORMALIZE, PATTERNS)` | ✅ Returns `str` | `normalize.py:745` |
| `normalize_expression(...)` | ✅ Returns `tuple[str, int]` | `normalize.py:912` |
| `run(...)` | ✅ Returns `tuple[Any, int]` | `normalize.py:959` |
| `check_if_number(token)` | ✅ Returns `dict` | `normalize.py:389` |
| `_build_config()` | ✅ Exists, builds config | `normalize.py:303` |

### Constants ✅
| Constant | Value | Status |
|----------|-------|--------|
| `MAX_INPUT_LENGTH` | 10000 | ✅ `normalize.py:42` |
| `MAX_NESTING_DEPTH` | 100 | ✅ `normalize.py:43` |
| `_UNITS_BY_LENGTH` | list | ✅ `normalize.py:46` |
| `_COMMON_UNITS` | list | ✅ `normalize.py:49-91` |
| `_UNIT_PREFIXES` | set | ✅ `normalize.py:94-97` |

---

## 2. Discrepancies: Documentation vs Code

### BUG: Number Word Combination Failing (HIGH PRIORITY)

**Documentation states** (`normalize.md:159-172`):
```
Input: "what's five plus three hundred twenty two?"
    ↓
1. Strip phrases: "five plus three hundred twenty two"
    ↓
2. Tokenize: ["five", "plus", "three", "hundred", "twenty", "two"]
    ↓
3. Convert number words: [5, +, 3, 100, 20, 2]
    ↓
4. Combine numbers: [5, +, 322]
    ↓
5. Build expression: "5+322"
    ↓
Output: 327
```

**Actual behavior:**
```
run("what's five plus three hundred twenty two?") → (3100207, 0)  # Wrong!
```

The output `3100207` shows the expression `5+3100202` was built instead of `5+322`.

**Root cause identified:** `split_at_operators()` (`normalize.py:703`) fails to split on whitespace. When `normalize()` converts `"three hundred twenty two"` to `"3 100 20 2"`, the space-separated tokens are not split because spaces are not operators. The entire string `"3 100 20 2"` is treated as a single token by `convert_from_human_handler()` because it's not recognized as a number (contains spaces).

**Code trace:**
1. `normalize("three hundred twenty two")` → `"3 100 20 2"` (line 745)
2. `split_at_operators("3 100 20 2")` → `["3 100 20 2"]` (line 703-742) — space is not an operator, so no split occurs
3. `convert_from_human_handler(["3 100 20 2"], ...)` → `["3 100 20 2"]` — token contains spaces, check_if_number returns False
4. Final result: `"5+3100202"` instead of `"5+322"`

**Location:** `normalize.py:703-742` (`split_at_operators`)

---

## 3. Potential Bugs Identified

### BUG 1: `check_if_number` returns wrong type for hex/binary/octal (MEDIUM)

**Location:** `normalize.py:429-451`

When `check_if_number` parses hex/binary/octal, it returns the **type of the original string token** (`type(token)`), but the `converted` value is an `int`. This is inconsistent with other number types which return the parsed numeric type (`int` or `float`).

```python
# Line 433
return {"bool": True, "converted": val, "type": type(token)}
# type(token) is str, but val is int
```

The `type` field in the return dict should reflect the actual numeric type (`int`), not the original string type, for consistency.

### BUG 2: `_handle_negative_token` bounds checking (LOW)

**Location:** `normalize.py:659-671`

```python
def _handle_negative_token(tokens, index, patterns):
    if index < 2 or index >= len(tokens) or ...:
        return tokens, []
```

The bounds check at line 665 is correct (verified via testing), but the function name and comment suggest it handles a single token, when actually it requires `index >= 2` to have enough context. This is confusing but not buggy.

### BUG 3: `combine_number_parts` complexity handling (MEDIUM)

**Location:** `normalize.py:493-530`

The `combine_number_parts` function at line 493 attempts to combine number parts like `20 + 2 = 22`, but the logic is complex and doesn't handle all edge cases:

```python
# Current: combine_number_parts([20, 2]) returns ['20', '+2'] instead of ['22']
```

The result `'20+2'` evaluates correctly, but the intermediate representation is incorrect compared to what the documentation promises (combining to a single number).

---

## 4. Improvement Suggestions

### HIGH PRIORITY

1. **Fix `split_at_operators` to handle whitespace-separated number words**
   - Issue: `split_at_operators()` only splits on operator characters, not spaces
   - When `normalize()` produces `"3 100 20 2"` from `"three hundred twenty two"`, these should be split and recombined
   - Suggestion: Add whitespace splitting in `split_at_operators()` or before calling `convert_from_human_handler()`

### MEDIUM PRIORITY

2. **Fix `check_if_number` return type consistency**
   - `type` field should reflect actual numeric type for hex/binary/octal
   - Location: `normalize.py:429-451`

3. **Simplify `combine_number_parts` logic**
   - The current logic at line 493 is complex and hard to verify
   - Consider a clearer algorithm or additional test cases

### LOW PRIORITY

4. **Document re-exported symbols in `__all__`**
   - `evaluate`, `EvaluationError`, `UnitValue` are re-exported but not documented in Key Exports section
   - Consider separating into a "Re-exports" section or importing directly

5. **Add docstring to `validate_for_eval`**
   - Location: `normalize.py:475`
   - Function exists but lacks docstring

6. **Add type annotations where missing**
   - Some internal functions lack complete type annotations

---

## 5. Summary of Findings

| Category | Count |
|----------|-------|
| Verified correct exports | 12 |
| Verified correct data structures | 6 |
| Verified correct core functions | 5 |
| Discrepancies (bugs) | 1 HIGH, 2 MEDIUM |
| Improvement suggestions | 6 total |

**Critical bug:** Number word combination (`"three hundred twenty two"` → `3100202` instead of `322`) affects the documented pipeline example. This needs fixing before the module can claim to work as documented.

**Code references for the critical bug:**
- `normalize.py:745` - `normalize()` function
- `normalize.py:703-742` - `split_at_operators()` fails to split on spaces
- `normalize.py:627-656` - `convert_from_human_handler()` receives unsplit tokens