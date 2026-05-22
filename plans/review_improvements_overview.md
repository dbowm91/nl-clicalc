# Review: architecture/overview.md Improvements

## Summary

Reviewed architecture/overview.md against the actual codebase structure. The document is generally accurate and well-organized. Found 7 discrepancies/issues ranging from minor to medium priority.

---

## Verified Claims ✓

| Claim | Status | Notes |
|-------|--------|-------|
| Core module files (normalize, evaluator, units, __main__) | ✓ | All exist at correct paths |
| exact/ module structure (7 modules + __init__) | ✓ | All files present |
| mcp/ module structure (schemas, tools, server) | ✓ | All files present |
| Key Data Structures: NUMBER_WORDS, OPERATOR_CONVERSIONS, FUNCTION_MAPPINGS, CONSTANT_WORDS | ✓ | All correctly located in normalize.py |
| Key Data Structures: UNIT_BASE, UNIT_CONVERSIONS, UNIT_ALIASES | ✓ | All correctly located in units.py |
| Key Data Structures: UnitValue | ✓ | Correctly in units.py |
| Key Data Structures: TOOL_SCHEMAS | ✓ | Correctly in mcp/schemas.py |
| Module Dependencies (dependency graph) | ✓ | All dependencies accurate |
| Build system (build_single.py, install.py) | ✓ | Both files exist |
| Function exports (evaluate, run, normalize, etc.) | ✓ | All verified via __init__.py exports |

---

## Discrepancies

### 1. confusables.py Line Count Inaccurate (LOW)

**Location:** Line 295
**Current:** "Auto-generated Unicode confusables table (~180KB, ~6500 lines)"
**Actual:** 6580 lines
**Fix:** Update "~6500 lines" to "6580 lines"

### 2. Key Data Structures Missing Memory Class (LOW)

**Location:** Key Data Structures table, line 462
**Issue:** `Memory` class is listed but `Memory` is not shown as a data structure entry
**Current:** Only `UnitValue` shown for evaluator.py
**Fix:** Add `Memory` class row:
```
| `Memory` | evaluator.py | Calculator memory registers |
```

### 3. normalize.py Dependencies Incomplete (LOW)

**Location:** Module Dependencies section, line 476
**Current:** `└── exact (inspect_text, count_chars, regex_test)`
**Issue:** Parent says normalize.py depends on exact but listing shows exact depends on normalize (wrong direction)
**Fix:** The arrow direction is correct in the text, but could clarify:
```
normalize.py
    ├── evaluator.evaluate()
    ├── units.UnitValue, UNIT_ALIASES, is_unit
    └── exact.inspect_text, exact.count_chars, exact.regex_test
```

### 4. Key Data Structures Missing normalize_unit (LOW)

**Location:** Key Data Structures table, line 458
**Issue:** `normalize_unit` is exported from units.py but not listed in the table
**Fix:** Add to units.py row or update line 58 entry:
```
| `normalize_unit` | units.py | Normalizes unit strings to canonical form |
```

### 5. CLI Entry Point Description Slightly Misleading (LOW)

**Location:** CLI Entry Point section, line 152
**Current:** "Entry point for `python -m nl_calc`. Delegates to `normalize.main()`."
**Issue:** While technically accurate (normalize.main() is called), this doesn't mention the actual processing flow through run()
**Fix:** Update to:
```
Entry point for `python -m nl_calc`. Parses arguments and delegates to `run()` for processing.
```

### 6. evaluator.py Key Exports Incomplete (MEDIUM)

**Location:** evaluator.py section, line 117
**Current Key exports:** `evaluate()`, `evaluate_raw()`, `evaluate_cached()`, `PyCalcApp`
**Issue:** Missing several important exports like `evaluate_async()`, `evaluate_with_timeout()`, `Memory`, memory functions, variable functions
**Fix:** Update to:
```
**Key exports:** `evaluate()`, `evaluate_raw()`, `evaluate_cached()`, `evaluate_async()`, `evaluate_with_timeout()`, `PyCalcApp`, `Memory`, `memory_store()`, `memory_recall()`, `memory_add()`, `memory_subtract()`, `memory_clear()`, `memory_list()`, `setvar()`, `getvar()`, `delvar()`, `listvars()`, `clearvars()`
```

### 7. missing from Key Exports (MEDIUM)

**Location:** normalize.py section, line 94
**Current Key exports:** `run()`, `normalize()`, `normalize_expression()`, `main()`
**Issue:** Missing `NORMALIZE`, `PATTERNS`, `print_help`, `MAX_INPUT_LENGTH`, `MAX_NESTING_DEPTH`
**Fix:** Update to:
```
**Key exports:** `run()`, `normalize()`, `normalize_expression()`, `main()`, `NORMALIZE`, `PATTERNS`, `print_help`, `MAX_INPUT_LENGTH`, `MAX_NESTING_DEPTH`
```

---

## Suggested Improvements

### High Priority

1. **Update evaluator.py Key Exports** (line 117)
   - Add missing function exports
   - Impacts: Users relying on docs to find API

2. **Update normalize.py Key Exports** (line 94)
   - Add missing exports like NORMALIZE, PATTERNS
   - Impacts: Users needing to use pattern constants

### Medium Priority

3. **Add normalize_unit to Key Data Structures** (line ~458)
   - Makes table comprehensive for units.py API
   - Impacts: Documentation completeness

4. **Add Memory to Key Data Structures** (line ~462)
   - Makes table comprehensive for evaluator.py API
   - Impacts: Documentation completeness

### Low Priority

5. **Fix confusables.py line count** (line 295)
   - "~6500 lines" → "6580 lines"
   - Minor accuracy improvement

6. **Clarify normalize.py dependencies** (line 476)
   - Show exact function names not just module
   - Minor clarity improvement

7. **Update CLI description** (line 152)
   - Clarify it uses `run()` not just `main()`
   - Minor accuracy improvement

---

## Verification Notes

- All file paths verified against actual filesystem
- All constants verified via grep and __init__.py exports
- confusables.py line count verified with `wc -l`
- Module dependency graph verified via import analysis
- MCP TOOL_SCHEMAS verified in schemas.py

---

## Priority Summary

| Priority | Count | Items |
|----------|-------|-------|
| High | 2 | evaluator exports, normalize exports |
| Medium | 2 | normalize_unit, Memory in data structures |
| Low | 3 | line count, dependency clarity, CLI description |