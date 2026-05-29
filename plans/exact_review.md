# Exact/ Architecture Review

**Document:** `architecture/exact.md`
**Code:** `eggcalc/exact/`
**Date:** 2026-05-29

---

## Summary

The architecture document `architecture/exact.md` is significantly outdated. The codebase has expanded substantially beyond the 14 modules documented, now containing 22 modules. Multiple functions, TypedDict definitions, and entire modules are not documented. There are also some minor discrepancies between documented return types and actual implementations.

---

## Critical Discrepancies

### CD1: Module Structure Outdated

**Location:** `architecture/exact.md:7-23` vs actual `eggcalc/exact/` directory

**Issue:** The documented module structure lists 14 modules, but the actual directory contains 22 modules.

| Documented | Actually Exists |
|-----------|-----------------|
| primitives.py | primitives.py |
| unicode_tools.py | unicode_tools.py |
| confusables.py | confusables.py |
| measure.py | measure.py |
| diff.py | diff.py |
| validate.py | validate.py |
| synthesis.py | synthesis.py |
| glob.py | glob.py |
| transform.py | transform.py |
| identifier.py | identifier.py |
| identifier_inspect.py | identifier_inspect.py |
| path_tools.py | path_tools.py |
| position.py | position.py |
| | cargo.py (MISSING) |
| | config.py (MISSING) |
| | inspect_prompt.py (MISSING) |
| | markdown.py (MISSING) |
| | patch.py (MISSING) |
| | shell.py (MISSING) |
| | unicode_policy.py (MISSING) |
| | version.py (MISSING) |

**Severity:** High - Documentation does not reflect actual codebase structure

---

### CD2: `__init__.py` Exports Incomplete

**Location:** `architecture/exact.md:25-72` vs `eggcalc/exact/__init__.py`

**Issue:** The documented public API re-exports are missing many items that exist in the actual `__init__.py`:

Missing module re-exports:
- `config` - dotenv/ini validation (`dotenv_validate`, `ini_validate`)
- `patch` - patch apply/summary (`patch_apply_check`, `patch_summary`)
- `inspect_prompt` - prompt inspection (`prompt_input_inspect`)
- `markdown` - markdown structure (`markdown_structure`, `code_fence_extract`)
- `shell` - shell tools (`shell_split`, `shell_quote_join`, `argv_compare`)
- `unicode_policy` - unicode policy (`unicode_policy_check`, `canonicalize_text`)
- `cargo` - cargo inspection (`cargo_toml_inspect`)
- `version` - version comparison (`parse_version`, `check_version_constraint`)

**Severity:** High - Users relying on documented exports will not find these tools

---

### CD3: Missing TypedDict Definitions

**Location:** `architecture/exact.md` vs actual implementations

**Issue:** Many TypedDict definitions exist in code but are not documented:

From `validate.py`:
- `BracketError` (line 21-27) - NOT documented
- `RegexFlags` (line 67-73) - NOT documented
- `RegexMatchPreview` (line 59-65) - NOT documented
- `TomlShapeResult` (line 352-359) - NOT documented
- `VersionCompareResult` (line 361-367) - NOT documented
- `RegexSafetyFinding` (line 1902-1907) - NOT documented
- `RegexFindIterMatch` (line 1751-1759) - NOT documented
- `SchemaViolation` (line 1287-1293) - NOT documented
- `JsonCanonicalizeResult` (line 2260-2272) - NOT documented
- `JsonQueryResult` (line 2274-2285) - NOT documented

From `synthesis.py`:
- `NormalizationState` (line 66-72) - NOT documented
- `UnicodeRisks` (line 74-80) - NOT documented
- `DiffInfo` (line 127-139) - NOT documented
- `InspectTextNormalized` (line 153-159) - NOT documented
- `NormalizationFinding` (line 161-164) - NOT documented
- `ListCompareOrderedResult` (line 195-201) - NOT documented
- `ListCompareSetResult` (line 202-207) - NOT documented
- `ListCompareMultisetResult` (line 208-214) - NOT documented
- `ListCompareNearMatch` (line 215-221) - NOT documented
- `TextWindowPosition` (line 1086-1093) - NOT documented

**Severity:** High - Missing type definitions cause confusion for users

---

## Discrepancies

### D1: `list_compare` Return Type

**Location:** `architecture/exact.md:366` vs `synthesis.py:985-1083`

**Issue:** The documentation states `list_compare(a, b)` returns `dict`. The actual implementation returns `ListCompareResult` (TypedDict).

**Severity:** Low - TypedDict is more correct; documentation should be updated

---

### D2: `visible_repr` Display Order

**Location:** `architecture/exact.md:457` vs `primitives.py:261-276`

**Issue:** The architecture doc correctly states "Variation selector checks must come BEFORE combining mark checks." The implementation at primitives.py:273-276 shows variation selectors (0xfe00-0xfe0f) are checked at line 273, and combining marks at line 275. This is **correct** and documented correctly.

**Severity:** None - This is a verification that the doc is correct

---

### D3: `utf8_bytes` Returns `bytes`

**Location:** `architecture/exact.md:456` vs `primitives.py:75-84`

**Issue:** The architecture doc correctly states "returns actual UTF-8 encoded bytes" - implementation confirms this.

**Severity:** None - Verified correct

---

### D4: `_get_script_heuristic` Caching

**Location:** `architecture/exact.md:458` vs `unicode_tools.py:82`

**Issue:** The architecture doc states `_get_script_heuristic()` has `@functools.lru_cache` decorator. The implementation at unicode_tools.py:82 confirms it has `@functools.lru_cache(maxsize=128)`.

**Severity:** None - Verified correct

---

### D5: Cf Characters Excluded from `control_chars`

**Location:** `architecture/exact.md:459` vs `measure.py:244-248`

**Issue:** The architecture doc states "Cf (format) characters excluded from control_chars" and measure.py:245-246 confirms: `if cat == "Cf": pass  # Cf excluded from control_chars count per UTS #55`

**Severity:** None - Verified correct

---

## Missing Documentation

### M1: Entire Modules Not Documented

The following modules exist in `eggcalc/exact/` but are completely absent from `architecture/exact.md`:

| Module | Purpose | Functions |
|--------|---------|-----------|
| `config.py` | .env and INI validation | `dotenv_validate`, `ini_validate` |
| `patch.py` | Unified diff parsing and application | `patch_apply_check`, `patch_summary` |
| `inspect_prompt.py` | Hidden char/ANSI/instruction detection | `prompt_input_inspect` |
| `markdown.py` | Markdown structure analysis | `markdown_structure`, `code_fence_extract` |
| `shell.py` | Shell command parsing | `shell_split`, `shell_quote_join`, `argv_compare` |
| `unicode_policy.py` | Named Unicode safety policies | `unicode_policy_check`, `canonicalize_text` |
| `cargo.py` | Cargo.toml inspection | `cargo_toml_inspect` |
| `version.py` | Semver/PEP440 parsing | `parse_version`, `check_version_constraint` |

**Severity:** High

---

### M2: Undocumented Functions in validate.py

| Function | Location | Purpose |
|----------|----------|---------|
| `regex_replace_preview()` | validate.py:802-874 | Preview regex replacements |
| `json_canonicalize()` | validate.py:2287-2402 | Canonicalize JSON with duplicate key detection |
| `json_query()` | validate.py:2415-2516 | RFC 6901 JSON Pointer query |
| `toml_shape()` | validate.py:369-419 | Analyze TOML structure |
| `version_compare()` | validate.py:422-561 | Compare version strings (semver/loose) |

**Severity:** Medium

---

### M3: Undocumented Functions in synthesis.py

| Function | Location | Purpose |
|----------|----------|---------|
| `text_window()` | synthesis.py:1107-1299 | Get window around position |
| `text_replace_check()` | synthesis.py:1324-1508 | Check replacement before editing |
| `line_range_extract()` | synthesis.py:1533-1672 | Extract exact line ranges |
| `line_range_compare()` | synthesis.py:1688-1788 | Compare line ranges |

**Severity:** Medium

---

## Verified Correct Items

The following items were verified as correctly documented and implemented:

- `CodepointInfo` as NamedTuple with fields: index, char, codepoint, name, category ✓
- `MeasureBasic` as TypedDict with correct fields ✓
- `InvisibleCharInfo` as TypedDict with correct fields ✓
- `utf8_bytes()` returns actual `bytes` object ✓
- `normalize_unicode()` with NFC/NFD/NFKC/NFKD forms, raises ValueError on invalid form ✓
- `normalized_equal()` with default form="NFC" ✓
- `visible_repr()` display order: space chars → invisible dict → VS → combining marks → BIDI ✓
- Variation selectors (U+FE00-U+FE0F) handled separately from `_INVISIBLE_CHARS` ✓
- `_INVISIBLE_CHARS` has 22 entries as documented ✓
- `diff.py` TypedDicts: `FirstDiff`, `CommonPrefixSuffix`, `DiffSpan` all correctly defined ✓
- `measure.py` TypedDicts: `LineMetrics`, `WordMetrics`, `CharCategoryMetrics` all correctly defined ✓
- `longest_common_subsequence()` implemented with dynamic programming ✓

---

## Recommendations

1. **Update Module Structure section** to reflect all 22 modules
2. **Add missing module documentation** for: config, patch, inspect_prompt, markdown, shell, unicode_policy, cargo, version
3. **Update public API exports** in `__init__.py` section to include all re-exports
4. **Add missing TypedDict definitions** to appropriate module sections
5. **Document undocumented functions** in validate.py, synthesis.py, and other modules
6. **Fix `list_compare` return type** - should be `ListCompareResult` not `dict`

---

## Risk Assessment

| Category | Risk Level | Notes |
|----------|------------|-------|
| Security | Low | Deterministic primitives, no external calls |
| Correctness | Low | Minor discrepancies, mostly documentation gaps |
| Usability | High | Many tools undocumented, module structure outdated |
| Completeness | High | 8 modules completely missing from docs |

**Overall:** The codebase is more complete than the documentation suggests. No critical bugs found - the issue is primarily documentation completeness.
