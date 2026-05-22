# nl-clicalc Consolidated Implementation Plan

## Status: ALL COMPLETED - Wave 7 Deferred Items Only

All waves 1-6 have been implemented and verified. Only Wave 7 (Future Items) remain deferred.

---

## Wave 7: Future Items (Low Priority - Deferred)

These are nice-to-have items that are not critical for the current implementation.

### 7.1 Rust Reimplementation Items (Future)
Future Rust reimplementation may include:
- Statistical functions (mean, median, std, variance)
- Complex number support
- Remaining physical constants
- Unicode normalization
- Casefold comparison
- Mixed script detection
- Compound unit parsing
- Port remaining test suites
- Interactive REPL and extended CLI options

### 7.2 Add Cancel Notification Support
**File:** `nl_calc/mcp/`

**Problem:** `notifications/cancel` and `notifications/progress` not handled.

**Fix:** Add cancel notification support for long-running operations.

### 7.3 Consider Adding confusable_codepoint Field
**File:** `nl_calc/exact/confusables.py`

**Problem:** Consumers may need both character and codepoint representations.

**Fix:** Consider adding `confusable_codepoint` field to ConfusableInfo TypedDict.

### 7.4 Consider Bidirectional Confusable Detection
**File:** `nl_calc/exact/confusables.py`

**Problem:** Currently only catches confusable characters, not Latin characters being used deceptively.

**Fix:** Consider adding bidirectional confusable detection.

### 7.5 Levenshtein vs difflib
**File:** `nl_calc/exact/diff.py`

**Problem:** Current difflib behavior may be insufficient for some use cases.

**Fix:** Optionally refactor to use true Levenshtein-based LCS diff.

### 7.6 Performance Timing Numbers
**File:** `nl_calc/__init__.py` or docs

**Problem:** Unverified performance timing numbers in documentation.

**Fix:** Remove or qualify since they cannot be verified.

---

## Verification Commands

After implementing changes, verify with these commands:

```bash
# Run all tests
python3 -m pytest tests/

# Verify unit conversion fix (1.1)
python3 -c "from nl_calc.units import get_conversion_factor; print(get_conversion_factor('kN', 'N'))"  # Should be 1000.0

# Verify temperature fix (1.2)
python3 -c "from nl_calc.units import convert_temperature; print(convert_temperature(32, 'F', 'C'))"  # Should be 0.0

# Verify newline detection (1.3)
python3 -c "from nl_calc.exact.measure import line_metrics; print(line_metrics('a\r\nb').newline_style)"  # Should be CRLF

# Verify MCP flag exists (1.5)
python3 -m nl_calc --help | grep mcp

# Check for lru_cache on _get_script_heuristic (3.3)
python3 -c "from nl_calc.exact.unicode_tools import _get_script_heuristic; import functools; print(hasattr(_get_script_heuristic, 'cache_info'))"

# Verify mps in UNIT_CATEGORIES (3.4)
python3 -c "from nl_calc.units import get_unit_category; print(get_unit_category('mps'))"  # Should be 'speed'
```

(End of file - 72 lines)