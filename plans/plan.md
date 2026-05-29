# nl-clicalc Implementation Plan

## Status: COMPLETED (2026-05-29)

All 35 items from the original plan have been verified and implemented.
See git history for the detailed implementation.

---

## Deferred Items (Design Review Needed)

These items were deferred during the implementation for design review:

| Item | Description | Reason |
|------|-------------|--------|
| D1 | Return type consistency | Binary operations return `UnitValue` even without units |
| D2 | Type stubs | Could add more specific type annotations |
| D3 | `load_user_config_extended` | Not exported by design |
| D4 | Confusables regeneration metadata | Could add date/version comment |
| D5 | Confusables reproducibility test | Could verify regeneration produces identical output |
| D6 | Performance benchmarking | Documented timings not verified |
| D7 | Complete TypedDict documentation for synthesis | All return types need docs |
| D8 | Reorganize documentation | Low priority, current structure functional |

---

## Notes for Future Agents

1. **Before fixing bugs:** Always read the actual code first. This plan was verified but some bugs may have been fixed after verification.

2. **For unit tests:** When adding tests for bug fixes, use:
   - `run()` for NL inputs like "five plus three"
   - `evaluate()` for pure math like "5 + 3"
   - CLI for integration tests

3. **For documentation fixes:** Always verify against the actual code before updating docs.

4. **Build compatibility:** All code changes must work when assembled by build_single.py into nl_calc.py

5. **Test count:** As of 2026-05-29, 631 tests pass.

(End of file)