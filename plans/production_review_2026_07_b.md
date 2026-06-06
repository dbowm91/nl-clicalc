# Production Code Review — 2026-07-b (Independent Re-Review)

## Status: COMPLETE

Independent re-review of eggcalc focused on correctness, MCP server
validation, and edge cases. The prior 2026-06 and 2026-07 reviews
addressed many issues; this round found **6 new high-severity bugs** not
covered by earlier work, plus several lower-severity findings tracked
for future work. All 6 high-severity findings are fixed and have
regression tests.

All findings have a regression test in
`tests/test_production_review_2026_07_b.py` (16 tests, all pass).
Final test suite: 1777 passed, 32 skipped (up from 1761 baseline;
the +16 are the new regression tests for this review).

## Summary

| ID  | Severity | File                          | Summary |
|-----|----------|-------------------------------|---------|
| B1  | High     | `eggcalc/mcp/server.py:824`   | JSON-RPC `id` accepts `True`/`False` (bool is `int` subclass) |
| B2  | High     | `eggcalc/mcp/tools.py:4096`   | `identifier_table_inspect` overwrites `language` parameter in loop |
| B3  | High     | `eggcalc/exact/patch.py:555`  | `patch_summary` flags every standard diff as a rename |
| B4  | High     | `eggcalc/evaluator.py:1391`   | Public `setvar()` bypasses `MAX_USER_VARIABLES=1000` cap |
| B5  | High     | `eggcalc/units.py:171`        | `1/m` returns `UnitValue(1, None)`, unit silently lost |
| B6  | High     | `eggcalc/units.py:1564`       | Compound units (`m**2`, `m/s**2`) have no category, can't add/convert |

Additional lower-severity findings tracked in the **Deferred** section.

---

## HIGH SEVERITY

### B1. JSON-RPC `id` accepts boolean values

**File:** `eggcalc/mcp/server.py:822-828`

**Reproduction:**
```python
from eggcalc.mcp.server import handle_request
r = handle_request({"jsonrpc": "2.0", "id": True, "method": "ping", "params": {}})
# Returns: {"jsonrpc": "2.0", "id": true, "result": {}}  ← WRONG
```

JSON-RPC 2.0 spec says the `id` member, if present, MUST be a String,
Number, or Null. `True` and `False` are not valid. The check
`isinstance(request_id, (str, int))` returns `True` for `bool` because
`bool` is a subclass of `int` in Python.

The same bug exists in the `notifications/cancelled` handler at
`server.py:855-857`, but that handler does have a guard:
`isinstance(cancelled_id, bool)` is excluded. The main `id` check does
not.

This is the same bug flagged by `plans/bug-hunt-mcp-units.md` as BUG 3
but never fixed.

**Fix:** Add `and not isinstance(request_id, bool)` to the id check.

**Status:** FIXED — `eggcalc/mcp/server.py:824` now excludes `bool`.

---

### B2. `identifier_table_inspect` overwrites `language` parameter

**File:** `eggcalc/mcp/tools.py:4096`

**Reproduction:**
```python
from eggcalc.mcp.server import handle_request
r = handle_request({
    "jsonrpc": "2.0", "id": 1, "method": "tools/call",
    "params": {"name": "identifier_table_inspect",
               "arguments": {"identifiers": [{"name": "for"}, {"name": "x"}]}},
})
# Returns error: "Unsupported language: None"
```

The handler signature is `identifier_table_inspect_mcp(
identifiers, language="python", checks=None)`. Inside the validation
loop at line 4096:

```python
language = entry.get("language")  # ← overwrites parameter!
```

This shadows the parameter with the per-entry field. Most entries don't
have a `language` key, so the parameter becomes `None` and the
downstream `if language not in valid_languages` check fails.

The schema in `schemas.py:1971` documents `language` as a top-level
parameter; the per-entry `language` is undocumented and not in the
schema. The fix is to rename the inner variable.

**Fix:** Rename `language = entry.get("language")` to `entry_lang =
entry.get("language")` and only validate `entry_lang`.

**Status:** FIXED — `eggcalc/mcp/tools.py:4096` uses `entry_lang`.

---

### B3. `patch_summary` reports renames for every standard diff

**File:** `eggcalc/exact/patch.py:555`

**Reproduction:**
```python
from eggcalc.mcp.server import handle_request
r = handle_request({
    "jsonrpc": "2.0", "id": 1, "method": "tools/call",
    "params": {"name": "patch_summary",
               "arguments": {"patch_text": "--- a\n+++ b\n@@ -1,1 +1,1 @@\n-old\n+new\n"}},
})
# Returns: renames_detected: [{from: "a", to: "b"}]  ← WRONG
```

In a unified diff, `--- <old>\n+++ <new>` is the standard file header
indicating the source and destination paths of a modification. They are
almost always different (e.g., `a/foo.txt` vs `b/foo.txt` from
`git diff`), but this is normal and not a rename. A rename requires
explicit `rename from X` / `rename to Y` directives (used by
`git diff -M` or similar extended formats).

The current code at line 555-556 unconditionally appends a "rename" for
any diff where the two filenames differ, producing false positives on
100% of normal diffs.

**Fix:** Only treat as a rename when an explicit `rename from/to`
directive is present in the file entry, or when the file content has
been moved (zero additions/deletions with only a path change). For
now, the simplest correct fix is to remove this block entirely and
only populate `renames_detected` from explicit rename metadata.

**Status:** FIXED — `eggcalc/exact/patch.py:555` no longer populates
`renames_detected` from standard diff headers. The list stays empty
until explicit rename support is added. Test
`tests/test_patch_tools.py:test_rename_detection` updated to match.

---

### B4. Public `setvar()` bypasses the documented `MAX_USER_VARIABLES` cap

**File:** `eggcalc/evaluator.py:1379-1392`

**Reproduction:**
```python
from eggcalc import setvar, clearvars
from eggcalc.evaluator import _default_evaluator, MAX_USER_VARIABLES
clearvars()
for i in range(MAX_USER_VARIABLES + 50):
    setvar(f"v{i}", i)
print(len(_default_evaluator._user_variables))  # → 1050, not 1000
```

The cap (`MAX_USER_VARIABLES = 1000`) is only enforced in
`_fn_setvar` (the expression-level function at line 1248). The public
Python API `setvar()` at line 1379 directly writes to
`ev._user_variables[name] = value` with no cap check, no identifier
validation, and no type validation on `value`.

This means a long-running process that calls `setvar()` in a loop can
grow `_user_variables` unbounded. Worse, `setvar("", 5)` or
`setvar("with space", 5)` from Python directly bypasses the identifier
check that the expression-level setvar enforces.

**Fix:** Refactor the cap+validation logic into a helper
`_set_user_variable(ev, name, value)` and call it from both
`_fn_setvar` and the public `setvar()`.

**Status:** FIXED — `_set_user_variable` extracted in
`eggcalc/evaluator.py` and called from both `_fn_setvar` and the
public `setvar()` at line 1391.

---

### B5. `UnitValue(1, None) / UnitValue(1, "m")` silently loses the unit

**File:** `eggcalc/units.py:171`

**Reproduction:**
```python
from eggcalc.units import UnitValue
result = UnitValue(1, None) / UnitValue(1, "m")
print(result.unit)  # → None  ← WRONG, should be "1/m" or "m**-1"
```

The `__truediv__` method's "else" branch (for cases where
`self.unit and other.unit` is False) falls through to `unit =
self.unit`. When `self.unit is None` and `other.unit is "m"`, the
result is dimensionless — but mathematically `1 / m` is a reciprocal
unit (1/m), not dimensionless.

The same pattern is in `__floordiv__` (line 195), `__mod__` (line 224).

Note: the inverse `1 / UnitValue(2, "m")` works correctly because it
goes through `__rtruediv__` (or rather, the actual `__rtruediv__`
behavior is delegated elsewhere). The bug is specifically in
`__truediv__` when `self` is dimensionless and `other` is a unit.

**Fix:** When `self.unit is None` and `other.unit` is not None, set
`unit = f"1/{other.unit}"` (or `f"{other.unit}**-1"`).

**Status:** FIXED — `__truediv__`, `__floordiv__`, `__mod__` in
`eggcalc/units.py:171-225` now produce `1/{other.unit}` reciprocal
units when `self.unit is None` and `other.unit` is set.

---

### B6. Compound units (`m**2`, `m**3`, `m/s**2`) have no category

**File:** `eggcalc/units.py:1564-1591`

**Reproduction:**
```python
from eggcalc.units import UnitValue, get_conversion_factor
# 1) Self-addition fails
UnitValue(5, "m**2") + UnitValue(3, "m**2")
# → ValueError: Cannot add incompatible units: m**2 + m**2

# 2) Cross-compound conversion fails
get_conversion_factor("m**2", "cm**2")
# → ValueError: Cannot convert from m**2 to cm**2

# 3) Category is None
get_unit_category("m**2")  # → None
get_unit_category("m/s**2")  # → None
```

The unit arithmetic produces compound units like `"m**2"`, `"m**3"`,
`"m/s**2"` via the `__pow__` and `__truediv__` methods. But
`UNIT_CATEGORIES` is keyed only on base unit names (`m`, `kg`, `s`),
not on derived forms. So:
- `5 m**2 + 3 m**2` fails (units are "m**2" and "m**2" with category
  None, so `are_units_compatible` returns False).
- `m**2 → cm**2` has no entry in `UNIT_CONVERSIONS` (only `m → cm`
  does).
- `m/s**2 → ft/s**2` similarly fails.

**Fix:** Add a helper `_derived_category(unit: str) -> str | None` that
parses compound unit strings and returns the appropriate category
(area, volume, acceleration, etc.). Use it in `get_unit_category` and
in `_rebuild_conversions` to populate compound-unit conversion factors.

**Status:** FIXED — Added `_DERIVED_CATEGORIES` dict mapping canonical
compound expressions to their categories. `_derived_category()`
parses the unit string and looks it up. `_add_compound_conversions()`
populates pairwise conversion factors in `UNIT_CONVERSIONS` for
units sharing the same category (e.g. `m**2 <-> cm**2 <-> ft**2`,
`m/s <-> km/h <-> mi/h`, `m/s**2 <-> ft/s**2`). Implementation uses
a flat `literal_factor` lookup keyed by unit name to avoid
cartesian-product explosion (the previous naive approach
generated 23M entries and made import 18s slow).

---

## DEFERRED (lower priority, tracked for future reviews)

These were observed but not addressed in this round:

- **D1.** `(a|aa)+$` and similar alternation-with-quantifier patterns
  slip past `_regex_safety_check` (rated "low" risk) but actually
  cause exponential backtracking. The 5-second subprocess timeout
  catches it, but the safety check is incomplete.
- **D2.** `_INSTRUCTION_RE` caching in `inspect_prompt.py` (flagged in
  the 2026-06 review as M1) — still appears to rebuild the regex on
  every call.
- **D3.** `prompt_input_inspect` with `phrase_patterns=['']` (empty
  string) generates 1 finding per character position because an empty
  regex matches everywhere. Should reject empty patterns or compile
  them as literal empty matches.
- **D4.** `unit_convert` schema doesn't document that `value` must be
  a real number (NaN/Inf are caught but the schema should declare it).
- **D5.** `m / s` produces unit `"m/s"` (good), but `m / s * s`
  produces `"m/s*s"` instead of `"m"`. No algebraic simplification.
- **D6.** `m*m/m` and similar compound units are not simplified.
- **D7.** Subprocess semaphore leak warning observed at Python 3.14
  shutdown ("leaked semaphore objects"). The `_SPAWN_SEMAPHORE` is
  never explicitly released on Python interpreter shutdown.
- **D8.** `Cargo.toml` `cargo_toml_inspect` reports
  `"Missing 'edition' in [package]"` as a warning but edition is only
  required for published crates; a library or workspace member may
  not have it.
- **D9.** `_INVISIBLE_CHARS` / `unicode_policy.py` doesn't include
  U+200E/U+200F (LRM/RLM) per the 2026-06 review (H4) — verifying
  this is still the case.
- **D10.** The `phrase_patterns` parameter schema says `type: array`
  with no `null` allowed, so `phrase_patterns=None` is rejected
  instead of being treated as "no patterns". Common API pattern.

---

## Implementation Order

1. **B1** — `server.py:824` — 1-line fix
2. **B2** — `tools.py:4096` — variable rename + sanity check
3. **B3** — `patch.py:555` — remove the false-positive rename block
4. **B4** — `evaluator.py:1391` — extract helper, call from both APIs
5. **B5** — `units.py:171` (and `__floordiv__`, `__mod__`) — fix the
   unit assignment for dimensionless-self case
6. **B6** — `units.py:1564` — add `_derived_category` helper, update
   `get_unit_category` and conversion table builder

After each fix, the corresponding test in
`tests/test_production_review_2026_07_b.py` should turn green.

## Verification

After fixes:
- All 16 new tests pass.
- `python -m pytest tests/ -q` — full suite still passes (1761 + 16
  new = 1777 tests, 32 skipped).
- `python build_single.py` — single-file build still works.
- `python eggcalc.py --json "5+3"` — CLI smoke test.
