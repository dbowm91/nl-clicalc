# unicode_tools Module Review — Improvement Plan

**Reviewed:** architecture/unicode_tools.md against nl_calc/exact/unicode_tools.py
**Date:** 2026-05-28

## Verified Claims (with line references)
- `unicode_script(char: str) -> str` — VERIFIED at code line 119
- `unicode_scripts(s: str) -> list[str]` — VERIFIED at code line 138
- `detect_mixed_scripts(s: str) -> dict` — VERIFIED at code line 150
- `detect_confusables(s: str) -> list[ConfusableInfo]` — VERIFIED at code line 187
- `confusables_count(s: str) -> int` — VERIFIED at code line 233
- `_get_script_heuristic()` is cached with `@functools.lru_cache` — VERIFIED at code line 72
- `ScriptInfo` TypedDict fields — VERIFIED at code line 21-26
- `ConfusableInfo` TypedDict fields — VERIFIED at code line 29-42

## Discrepancies Between Documentation and Code

### HIGH Priority

1. **`reverse_confusables` function completely missing from documentation**
   - Documentation says: Nothing (not mentioned anywhere)
   - Code actually does: `reverse_confusables(char: str) -> list[str]` defined at code lines 268-292, exported in `__init__.py:52` and `__all__:108`
   - Impact: Public API function is undocumented, users have no knowledge of this capability

2. **`detect_mixed_scripts` documentation omits "Other" script exclusion**
   - Documentation says: `'positions': list[ScriptInfo]  # Positions of non-Common/Inherited chars` (docs line 75)
   - Code actually does: Excludes "Other" in addition to "Common" and "Inherited" (code lines 170, 181)
   - Impact: Documentation incorrectly describes behavior; users may misinterpret results

3. **Index section missing `reverse_confusables`**
   - Documentation says: Index lists only 5 functions (docs lines 217-224)
   - Code actually does: 6 public functions exist (including `reverse_confusables`)
   - Impact: Documentation index is incomplete

### MEDIUM Priority

4. **`detect_mixed_scripts` return type underspecified**
   - Documentation says: Returns `dict` with `mixed_scripts`, `scripts`, `positions` keys (docs lines 73-76)
   - Code actually does: Returns a `dict` with proper TypedDict structure but docs don't specify the type annotations match the actual TypedDict definitions
   - Impact: Minor - type documentation is implied through examples

5. **`ConfusableInfo.confusable_with` can contain multiple characters**
   - Documentation mentions: "multi-character substitutions" (docs line 133) in the database section but doesn't clarify that `confusable_with` field can contain multiple codepoints joined
   - Code actually does: `"".join(chr(int(cp[2:], 16)) for cp in sub_str.split())` joins potentially multiple chars (code line 210)
   - Impact: Users may not realize `confusable_with` can be a multi-character string

## Potential Bugs

- [LOW] **No bugs identified** — Code is well-structured with proper error handling, cache usage, input validation, and edge case coverage

## Improvement Suggestions

### HIGH Priority

1. **Document `reverse_confusables` function** — Add complete documentation including:
   - Function signature and description
   - Example usage showing the "O" / "0" confusable case
   - Return type and behavior
   - Position in docs: after `confusables_count` in the Functions section

2. **Update `detect_mixed_scripts` docs to mention "Other" exclusion** — Change docs line 75 from:
   ```
   'positions': list[ScriptInfo]  # Positions of non-Common/Inherited chars
   ```
   to:
   ```
   'positions': list[ScriptInfo]  # Positions of non-Common/Inherited/Other chars
   ```

3. **Update Index section** — Add `reverse_confusables()` to the index list (after `confusables_count`)

### MEDIUM Priority

4. **Clarify multi-character confusable_with** — Add note that `confusable_with` in `ConfusableInfo` may contain multiple characters when the confusables table maps to multi-codepoint sequences

5. **Add `unicode_scripts` to the Supported Scripts table or clarify it returns per-character scripts** — Currently the table shows script info but `unicode_scripts` returns a list matching each character position

### LOW Priority

6. **Add example for `detect_mixed_scripts` showing "Other" exclusion** — Example with digits or punctuation to demonstrate they're excluded from the `scripts` list

## Summary

The unicode_tools module documentation is mostly accurate but has one critical omission: `reverse_confusables()` is a fully implemented and exported public function that is completely absent from the architecture document. Additionally, `detect_mixed_scripts()` exclusion of "Other" script is mentioned in code comments but missing from documentation. Both should be corrected to ensure documentation completeness and accuracy. No bugs were identified in the implementation.
