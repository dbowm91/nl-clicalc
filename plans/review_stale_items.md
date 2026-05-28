# Stale Items Report

**Date:** 2026-05-28

## Dead References

### Orphaned Review Plan Links
The architecture docs reference review plan files that do not exist in `plans/`:

| Document | Line | Missing File |
|----------|------|--------------|
| `overview.md` | 510 | `plans/normalize_review.md` |
| `overview.md` | 511 | `plans/evaluator_review.md` |
| `overview.md` | 512 | `plans/units_review.md` |
| `overview.md` | 513 | `plans/primitives_review.md` |
| `overview.md` | 514 | `plans/unicode_tools_review.md` |
| `overview.md` | 516 | `plans/diff_review.md` |
| `overview.md` | 517 | `plans/validate_review.md` |
| `overview.md` | 518 | `plans/synthesis_review.md` |
| `overview.md` | 519 | `plans/confusables_review.md` |
| `overview.md` | 520 | `plans/mcp_server_review.md` |
| `overview.md` | 521 | `plans/cli_review.md` |
| `overview.md` | 523 | `review_plan.md` (at project root, not in plans/) |

The actual files in `plans/` are named `review_improvements_*.md` not `*_review.md`.

## Unimplemented Features

### None identified
All documented features exist in code. No unimplemented features found.

## Orphaned Architecture Files

### None identified
All architecture documents have corresponding source modules:
- `primitives.md` → `nl_calc/exact/primitives.py` ✓
- `unicode_tools.md` → `nl_calc/exact/unicode_tools.py` ✓
- `measure.md` → `nl_calc/exact/measure.py` ✓
- `diff.md` → `nl_calc/exact/diff.py` ✓
- `validate.md` → `nl_calc/exact/validate.py` ✓
- `synthesis.md` → `nl_calc/exact/synthesis.py` ✓
- `confusables.md` → `nl_calc/exact/confusables.py` ✓
- `mcp.md` → `nl_calc/mcp/server.py`, `schemas.py`, `tools.py` ✓

## Duplicate Documentation

### FirstDiff TypedDict Declaration (diff.md)
**Location:** `architecture/diff.md:88-92`

The `FirstDiff` TypedDict is declared twice in the same file with different content:
1. Lines 88-92 show incomplete 3-field version (stale)
2. Lines 115-121 show correct 6-field version

**Stale content:**
```python
class FirstDiff(TypedDict):
    position: int
    a_char: str
    b_char: str
```

**Should be removed or updated to match lines 115-121:**
```python
class FirstDiff(TypedDict):
    a_index: int
    b_index: int
    a_char: str
    b_char: str
    a_codepoint: str
    b_codepoint: str
```

### FirstDiff Data Structure Description (diff.md)
**Location:** `architecture/diff.md:113-121`

Describes `position` field, but actual code uses `a_index` and `b_index`.

## Outdated Examples

### common_prefix_suffix examples (diff.md)
**Location:** `architecture/diff.md:53-59`

All three examples return incorrect values:

| Input | Documented | Actual |
|-------|------------|--------|
| `"hello", "hell"` | `{'common_prefix_len': 3, 'common_suffix_len': 0}` | `{'common_prefix_len': 4, 'common_suffix_len': 0}` |
| `"hello", "yo"` | `{'common_prefix_len': 0, 'common_suffix_len': 0}` | `{'common_prefix_len': 0, 'common_suffix_len': 1}` |
| `"testing", "ing"` | `{'common_prefix_len': 0, 'common_suffix_len': 0}` | `{'common_prefix_len': 0, 'common_suffix_len': 3}` |

### diff_spans example (diff.md)
**Location:** `architecture/diff.md:105-109`

Example shows `equal` spans in output, but code filters them out (line 232: `if tag == "equal": continue`).

**Documented output:**
```python
[DiffSpan(kind='equal', ...), DiffSpan(kind='replace', ...), DiffSpan(kind='equal', ...)]
```

**Actual output:**
```python
[DiffSpan(kind='replace', ...)]  # equal spans filtered
```

### diff_spans kind values (diff.md)
**Location:** `architecture/diff.md:126`

Lists `"equal"` as a valid `kind` value, but code never returns it.

### Pipeline example (normalize.md)
**Location:** `architecture/normalize.md:185-186`

Step 4 shows `[5, +, 322]` but "three hundred twenty two" should be `3*100+22`, not combined into a single `322` token. The actual expression is `5+3*100+22=327`, not `5+322=327`.

### bitnot documentation (evaluator.md)
**Location:** `architecture/evaluator.md:116`

Documents `bitnot(a)` without noting it requires an integer operand. Code correctly raises `EvaluationError` for non-integer operands.

## Outdated Counts/Metadata

### Test Count (overview.md)
**Location:** `architecture/overview.md:5`

**Documented:** "**All 350 tests pass.**"

**Actual:** Test count should be verified - this appears to be a static claim that may become stale as tests are added/removed. No automated verification.

### Build Output Size (overview.md)
**Location:** `architecture/overview.md:395`

**Documented:** "**Output:** Self-contained executable (~394KB)"

**Actual:** Size may vary and is not tracked. Could become stale.

## Other Documentation Issues

### MAX_INPUT_LENGTH Inconsistency
Two different values exist:

| Module | Value |
|--------|-------|
| `normalize.py:42` | 10000 |
| `validate.py:14` | 100000 |

This is documented in `review_improvements_overview.md` but not fixed. The API docs (api.md:164) only mention the 10000 value.

### normalize_expression return type (api.md)
**Location:** `architecture/api.md:130`

**Documented:** `normalize_expression(expression: str) -> str`

**Actual:** Returns `tuple[str, int]` (normalized_expression, exit_code)

### Variable functions return types (api.md)
**Location:** `architecture/api.md:120-126`

| Function | Documented | Actual |
|----------|------------|--------|
| `setvar` | `dict[str, Any]` | `Any` (the value) |
| `getvar` | `dict[str, Any]` | `Any` (the value, or 0 if not found) |
| `delvar` | `dict[str, Any]` | `None` |
| `listvars` | `dict[str, Any]` | `dict[str, Any]` (correct) |
| `clearvars` | `dict[str, Any]` | `None` |

### Undocumented exports in api.md
The following are exported from `__init__.py` but not documented in `api.md`:
- `load_user_config_extended()` (exists in evaluator.py:168)
- `register_function()` (exists in evaluator.py:73)
- `get_default_evaluator()` (exists in evaluator.py:1387)
- `FLOAT_EPSILON` (exists in units.py:20)
- `MAX_INPUT_LENGTH` from normalize (exported but not documented)
- `MAX_NESTING_DEPTH` (duplicated in evaluator and normalize)

### Undocumented function in evaluate_raw (evaluator.md, normalize.md)
`evaluate_raw()` is exported and useful but has no dedicated documentation section. It appears in Key Exports but not in Evaluation Functions section.

## Recommendations

### HIGH Priority (should fix)

1. **Fix orphaned links in overview.md** (lines 505-523)
   - Either create the missing `plans/*_review.md` files, OR
   - Update links to point to existing `review_improvements_*.md` files

2. **Fix FirstDiff TypedDict in diff.md** (lines 88-92)
   - Remove duplicate declaration or update to match actual 6-field structure

3. **Fix common_prefix_suffix examples in diff.md** (lines 53-59)
   - All three examples are incorrect - update to match actual output

4. **Fix diff_spans example in diff.md** (lines 105-109)
   - Either show actual output (no `equal` spans) or clarify they are filtered

### MEDIUM Priority (should review)

5. **Remove "equal" from DiffSpan kind values** (diff.md:126)
   - Code never returns `equal` - update documentation

6. **Fix normalize_expression return type in api.md** (line 130)
   - Change from `-> str` to `-> tuple[str, int]`

7. **Fix variable functions return types in api.md** (lines 120-126)
   - setvar: `-> Any`
   - getvar: `-> Any`
   - delvar: `-> None`
   - listvars: `-> dict[str, Any]` (correct)
   - clearvars: `-> None`

8. **Document load_user_config_extended(), register_function(), get_default_evaluator()** in api.md

9. **Document evaluate_raw()** in evaluator.md

### LOW Priority (consider fixing)

10. **Update bitnot documentation to mention integer requirement** (evaluator.md:116)

11. **Fix pipeline example in normalize.md** (line 185-186)
    - Clarify that "three hundred twenty two" becomes `3*100+22`

12. **Consider removing test count claim from overview.md** (line 5)
    - Static counts become stale; rely on CI to verify

13. **Remove build output size claim from overview.md** (line 395)
    - Size varies; not meaningful to track in docs
