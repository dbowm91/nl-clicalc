# Production Readiness Review Plan

## Summary

Comprehensive review of eggcalc for production use, focusing on correctness, MCP server validation, and edge cases. Found **4 high-severity**, **7 medium-severity**, and **8 low-severity** issues across the codebase.

---

## HIGH SEVERITY (Fix Immediately)

### H1. `prompt_input_inspect` regex runs in main process (no subprocess isolation)
**File:** `eggcalc/mcp/tools.py` (~line 4346-4360)
**Issue:** User-supplied `phrase_patterns` regex is executed in the MCP server's main thread via `re.search()`. Unlike `validate_regex` and `dotenv_validate` which isolate regex execution in subprocesses with timeouts, `prompt_input_inspect` has no such protection. A pathological regex pattern could hang the entire MCP server.
**Fix:** Move regex execution in `prompt_input_inspect` to a subprocess worker with timeout, matching the pattern used by `validate_regex` and `dotenv_validate`. Alternatively, run `_regex_safety_check` on each pattern before execution and enforce a per-pattern timeout.

### H2. O(N²) in `check_brackets()` via `_get_line_column()`
**File:** `eggcalc/exact/validate.py` (~lines 126-144, 188-216)
**Issue:** `_get_line_column()` iterates from index 0 to target on every call. In `check_brackets()`, it's called up to 3 times per unmatched bracket. For a 100KB string where every character is an unmatched bracket, this yields ~30 billion character comparisons. The `MAX_INPUT_LENGTH = 100_000` bound makes this exploitable.
**Fix:** Replace `_get_line_column()` with a single-pass approach: precompute line/column mapping once, or use `bisect` on a precomputed list of newline positions.

### H3. `unicode_policy_check()` has no input length limit
**File:** `eggcalc/exact/unicode_policy.py` (~lines 96-189)
**Issue:** Unlike `inspect_prompt.py` which enforces `MAX_TEXT_LENGTH = 100_000`, `unicode_policy_check()` accepts arbitrarily large strings. Each policy check does 5+ full passes over the string. A 10MB string would cause significant CPU and memory pressure.
**Fix:** Add `MAX_INPUT_LENGTH = 100_000` check at the top of `unicode_policy_check()`, consistent with other validation functions.

### H4. Bidi character set inconsistency between modules
**File:** `eggcalc/exact/unicode_policy.py` (~lines 80-83) vs `eggcalc/exact/inspect_prompt.py` (~lines 173-185)
**Issue:** `_BIDI_CHARS` in `unicode_policy.py` is missing U+200E (LRM) and U+200F (RLM), which ARE present in `inspect_prompt.py`'s `bidi_names`. An attacker embedding U+200F would be flagged by `prompt_input_inspect` but pass `unicode_policy_check()` for bidi controls. This creates a bypass between detection modules.
**Fix:** Add U+200E and U+200F to `_BIDI_CHARS` in `unicode_policy.py`, or create a shared constant in `primitives.py` used by both modules.

---

## MEDIUM SEVERITY (Fix Before Release)

### M1. `_INSTRUCTION_RE` caching is broken (dead code)
**File:** `eggcalc/exact/inspect_prompt.py` (~lines 122, 157-162)
**Issue:** `_get_instruction_re()` declares `global _INSTRUCTION_RE` but never assigns to it. The regex is rebuilt on every call when `phrase_patterns=None`. This is a performance bug — the regex is recompiled on every `prompt_input_inspect` call.
**Fix:** Add `_INSTRUCTION_RE = result` before the return statement.

### M2. `MAX_FINDINGS` truncation drops high-severity findings
**File:** `eggcalc/exact/inspect_prompt.py` (~lines 487-490)
**Issue:** Findings are appended in check order. `unicode_hidden` checks first and can produce one finding per invisible character. A text with 1,000+ invisible characters fills `MAX_FINDINGS` before later checks (including `INSTRUCTION_PHRASE`) run. High-severity findings are silently dropped.
**Fix:** Sort findings by severity before truncating, or reserve slots for each check category.

### M3. `regex_replace_preview()` missing per-sample length check
**File:** `eggcalc/exact/validate.py` (~lines 907-987)
**Issue:** `regex_test()` checks `len(sample) > MAX_SAMPLE_LENGTH` but `regex_replace_preview()` does not. A 10MB string in a single sample bypasses the guard.
**Fix:** Add `MAX_SAMPLE_LENGTH` check for each sample in `regex_replace_preview()`.

### M4. `validate_schema_light()` has no input size limit
**File:** `eggcalc/exact/validate.py` (~lines 2208-2398)
**Issue:** Walks entire data structure with no total size check. A valid schema with a 10-million-element array iterates through all elements even with zero violations.
**Fix:** Add `MAX_DATA_ELEMENTS` or `MAX_WALK_STEPS` limit to bound total iteration.

### M5. `validate_toml_text` catches `Exception` too broadly
**File:** `eggcalc/exact/validate.py` (~lines 336-351)
**Issue:** Catches `Exception` which masks programming errors (e.g., `RecursionError`, `MemoryError`). Unexpected exceptions are reported as normal parse errors.
**Fix:** Catch specific TOML-related exceptions (`tomllib.TOMLDecodeError`, `ValueError`, `KeyError`) and let others propagate.

### M6. `flags` list items in `validate_regex` not type-checked
**File:** `eggcalc/mcp/tools.py` (~lines 1237-1387, 1539-1686)
**Issue:** `flags` parameter is `list[str] | None` but handler never validates items are strings. Non-string items produce confusing errors in subprocess worker.
**Fix:** Add `all(isinstance(f, str) for f in flags)` check before passing to worker.

### M7. Duplicate bidi findings in `inspect_prompt.py`
**File:** `eggcalc/exact/inspect_prompt.py` (~lines 468-471)
**Issue:** When both `unicode_hidden` and `bidi` checks are active, bidi characters (U+202A-U+202E) are reported by both checks, inflating risk scores.
**Fix:** Deduplicate findings by (position, character) before returning, or exclude bidi chars from `unicode_hidden` when `bidi=True`.

---

## LOW SEVERITY (Track for Future)

### L1. `_canonicalize_source_file_identity` O(N²) trailing newline stripping
**File:** `eggcalc/exact/validate.py` (~lines 649-654)
**Issue:** `while current.endswith("\n\n")` removes one char at a time via string slicing. O(N²) for 50K trailing newlines.
**Fix:** Use `current.rstrip("\n")` or `current[:current.rstrip("\n").__len__()]`.

### L2. Normalization instability check has high false-positive rate
**File:** `eggcalc/exact/unicode_policy.py` (~lines 246-255)
**Issue:** Fires on any text containing precomposed characters with combining equivalents (e.g., common accented characters like é).
**Fix:** Document as intentional heuristic, or narrow the check to only fire when NFC≠NFD AND the text contains confusable-adjacent characters.

### L3. `json_key` policy missing variation selector detection
**File:** `eggcalc/exact/unicode_policy.py` (~lines 399-440)
**Issue:** Variation selectors (U+FE00-U+FE0F) are in `_INVISIBLE_CHARS` in primitives.py but not detected by `json_key` policy.
**Fix:** Add variation selector check to `_check_json_key()`.

### L4. Windows reserved name check is path-naive
**File:** `eggcalc/exact/unicode_policy.py` (~lines 310-317)
**Issue:** `stem = normalized.split(".")[0].upper()` doesn't handle path-qualified filenames like `dir/CON.txt`.
**Fix:** Extract basename before checking, or document as filename-only (not path) policy.

### L5. `_cancelled_requests` uses O(N) linear scan
**File:** `eggcalc/mcp/server.py` (~lines 598-603)
**Issue:** Rebuilds deque by filtering on every cancellation check. A `set` would give O(1) lookups.
**Fix:** Use a `set` with `MAX_CANCELLED_REQUESTS` bound, or accept the O(N) since N≤10,000.

### L6. Code duplication in subprocess cleanup patterns
**File:** `eggcalc/mcp/tools.py` (3 locations)
**Issue:** `terminate() -> join(2) -> kill() -> join(1) -> register as orphan` is repeated in `validate_regex`, `regex_finditer`, and `dotenv_validate`.
**Fix:** Extract into a shared `_cleanup_child_process(proc, timeout)` helper.

### L7. `_sanitize_error` path regex may over-redact
**File:** `eggcalc/mcp/tools.py` (~lines 353-380)
**Issue:** Pattern `(?:/[\w.-]+){2,}\.\w+` matches legitimate path-like substrings in error messages.
**Fix:** Acceptable for error messages; no fix needed unless user-visible text is affected.

### L8. `_mcp_defaults_configured` benign race condition
**File:** `eggcalc/mcp/server.py` (~lines 799-806)
**Issue:** Flag checked and set without lock. Currently single-threaded `main()` so no actual race, but `handle_request()` is public.
**Fix:** Use `threading.Lock` or accept idempotent double-call.

---

## Test Coverage Gaps to Address

| Priority | Gap | Action |
|----------|-----|--------|
| **High** | MCP mode doesn't verify state-mutating functions disabled | Add tests for `setvar`/`store`/`random` rejection in MCP mode |
| **High** | Rate limiting only tests constant value, not enforcement | Add test sending >MAX_REQUESTS_PER_SECOND |
| **High** | `convert()` and `temp()` functions untested via `evaluate()` | Add positive-path tests |
| **High** | `phase`, `polar`, `rect` complex functions untested | Add test cases |
| **Medium** | UnitValue arithmetic operators untested | Add tests for `__neg__`, `__pos__`, `__abs__`, `__round__`, `__complex__`, `__int__`, `__float__` |
| **Medium** | 36 evaluator function aliases untested | Add tests for `ln`, `fact`, `is_prime`, `std`, `var`, etc. |
| **Medium** | Tokenization lacks Unicode/scientific notation tests | Add test cases |
| **Medium** | No concurrent evaluation safety test | Add thread-safety test |

---

## Implementation Order

1. **Phase 1 — Security Critical (H1-H4):**
   - H1: Subprocess isolation for `prompt_input_inspect` regex
   - H2: Fix O(N²) in `check_brackets()`
   - H3: Add input length limit to `unicode_policy_check()`
   - H4: Unify bidi character sets

2. **Phase 2 — Correctness (M1-M7):**
   - M1: Fix `_INSTRUCTION_RE` caching
   - M2: Severity-aware finding truncation
   - M3: Per-sample length check in `regex_replace_preview`
   - M4: Input size limit for `validate_schema_light`
   - M5: Narrow exception handling in `validate_toml_text`
   - M6: Type-check `flags` list items
   - M7: Deduplicate bidi findings

3. **Phase 3 — Test Coverage:**
   - Add MCP mode security tests
   - Add rate limiting enforcement test
   - Add `convert()`/`temp()` positive tests
   - Add complex function tests
   - Add UnitValue operator tests
   - Add function alias tests

4. **Phase 4 — Low Severity (L1-L8):** ✅ COMPLETE
   - Fix O(N²) trailing newline stripping
   - Document normalization instability heuristic
   - Add variation selector check to `json_key`
   - Fix Windows reserved name check for paths
   - Replace _cancelled_requests deque with set
   - Extract subprocess cleanup into shared helper
   - Refine _sanitize_error path regex
   - Add thread lock for _mcp_defaults_configured

---

## Verification

After each phase:
1. Run `python3 -m pytest tests/ -x --tb=short` — all existing tests must pass
2. Run `python3 -m pytest tests/test_security_fuzz.py -x` — security tests must pass
3. Run `python3 -m pytest tests/test_mcp_server.py -x` — MCP tests must pass
4. Manual verification of fixed edge cases
