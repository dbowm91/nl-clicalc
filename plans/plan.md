# nl-clicalc Consolidated Implementation Plan

## Status: COMPLETED

All items from waves 1-7 have been implemented. Deferred items remain for future consideration.

---

## Deferred Items

These items require design decisions or are low priority.

| Item | Description | Reason |
|------|-------------|--------|
| D1 | Add reverse lookup function for confusables | Requires design decision |
| D2 | Fix or remove unreachable `unicode_normalization_only` | Requires investigation |
| D3 | Add `include_codepoints` to `measure_text()` or remove from docs | Design decision |
| D4 | Add `normalize_text` parameter to `inspect_text()` | May overlap with existing |
| D5 | Performance review for confusables_count | Defer until profiling needed |
| D6 | Reorganize documentation structure | Low priority, structural |
| D7 | Add docstrings to ConfusableInfo fields | Low priority |
| D8 | Clarify `normalize()` vs `normalize_expression()` distinction | Low priority |
| D9 | Add input size limits for `check_brackets()` and `validate_json()` | Low priority |
| D10 | Update CLI entry description | Low priority |
| D11 | Clarify normalize.py dependencies | Low priority |
| D12 | Add `__all__` export list for diff.py | Low priority |

---

## Implementation Notes

### Wave 1: Critical Bugs - FIXED
- Item 1: `split_at_operators` multi-word number combining fixed by adding `_finish_number_group()` and `_combine_consecutive_numbers()` in normalize.py
- Item 2: `combine_number_parts` logic fixed (was already working correctly per verification)

### Wave 2-7: All items verified complete

---

## Verification Commands

```bash
# Run all tests
python3 -m pytest tests/

# Verify critical fixes
python3 -c "from nl_calc import run, NORMALIZE, PATTERNS; print(run('five plus three hundred twenty two', NORMALIZE, PATTERNS))"
python3 -c "from nl_calc.normalize import combine_number_parts; print(combine_number_parts([20, 2]))"
python3 -c "from nl_calc.exact.validate import CheckBracketsResult; print('Has __slots__:', hasattr(CheckBracketsResult, '__slots__'))"

# Verify feature additions
python3 -c "from nl_calc import evaluate; print(evaluate('fact(5)'))"
python3 -c "from nl_calc import evaluate; print(evaluate('me'))"

# Verify MCP fix
python3 -c "from nl_calc.mcp.tools import math_eval; print(math_eval('5+3'))"
```

All 346 tests pass.