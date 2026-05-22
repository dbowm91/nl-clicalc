# nl-clicalc Consolidated Implementation Plan

## Status: Completed

All actionable items from the plan have been verified and completed (or deferred appropriately).

## Summary

The following items were verified as already completed at plan review:

**Wave 1 (Critical Bugs)**: All 4 items verified working:
- 1.1 Temperature conversion in UnitValue.convert_to()
- 1.2 kilonewton alias correctly maps to kN
- 1.3 _cbrt() supports complex numbers
- 1.4 Hyperbolic functions (sinh, cosh, tanh, asinh, acosh, atanh) are complex-aware

**Wave 2 (CLI/REPL)**: All 3 items verified working:
- 2.1 --verbose flag shows expression
- 2.2 REPL shows expressions by default
- 2.3 -e flag behavior correct

**Wave 3 (Documentation)**: 4 items were already correct (3.3, 3.4, 3.6, 3.7); 3 items fixed (3.1, 3.2, 3.5)

**Wave 4 (Security)**: 4 items verified working (4.2, 4.3, 4.4, 4.5); 4.1 noted as intentional design decision per UTS #55

**Wave 5 (Code Quality)**: 8 items verified working (5.1, 5.2, 5.3, 5.4, 5.6, 5.7, 5.8, 5.10); 5.9 partially implemented

**Wave 6 (Feature Completeness)**: 3 items verified working (6.3, 6.4, 6.5); 6.1, 6.6, 6.7, 6.9 fixed; 6.2 and 6.8 deferred

## Deferred Items (Low Priority - Future Enhancement)

The following items were intentionally deferred as they require significant work for marginal benefit:

| Item | Description | Reason Deferred |
|------|-------------|-----------------|
| 4.1 | Include Cf in control_chars | Intentional per UTS #55 - format chars are silently ignored |
| 5.9 | Full TypedDict __slots__ | Only validate.py and measure.py needed; other files have few instances |
| 6.2 | Grapheme counting | Requires complex Unicode grapheme cluster implementation |
| 6.8 | max_word_length feature | `average_word_length` available; max is rarely needed |

## Wave 7 & 8 Items (Low Priority - Future Enhancement)

Items in Wave 7 and 8 remain as potential future enhancements:
- Statistical functions (mean, median, std, variance)
- Complex number support (beyond what's already there)
- Remaining physical constants
- Unicode normalization beyond NFC
- Casefold comparison improvements
- Mixed script detection enhancements
- Compound unit parsing
- Cancel notification support for MCP
- Bidirectional confusable detection
- Levenshtein vs difflib refactor
- And other low-priority improvements listed in original plan

## Verification

```bash
# All 346 tests pass
python3 -m pytest tests/

# Temperature conversion
python3 -c "from nl_calc.units import UnitValue; u = UnitValue(32, 'F'); print(u.convert_to('C'))"

# kilonewton alias
python3 -c "from nl_calc.units import get_conversion_factor; print(get_conversion_factor('kN', 'N'))"

# Complex cbrt
python3 -c "from nl_calc.evaluator import evaluate; print(evaluate('cbrt(-8)'))"

# Complex hyperbolic
python3 -c "from nl_calc.evaluator import evaluate; print(evaluate('sinh(1+2j)'))"
```

(Original plan with full item details preserved in git history prior to 2026-05-22)