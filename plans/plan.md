# eggcalc Implementation Plan

## Status: COMPLETED (2026-05-29)

All 35 original items and all 8 deferred items have been verified as implemented.
See git history for detailed implementation.

---

## Design Decisions (Not Implemented)

| Item | Description | Reason |
|------|-------------|--------|
| D3 | `load_user_config_extended` | Not exported - thread-safety concerns with custom number/operator words |

---

## Notes for Future Agents

1. **Before fixing bugs:** Always read the actual code first. This plan was verified but some bugs may have been fixed after verification.

2. **For unit tests:** When adding tests for bug fixes, use:
   - `run()` for NL inputs like "five plus three"
   - `evaluate()` for pure math like "5 + 3"
   - CLI for integration tests

3. **For documentation fixes:** Always verify against the actual code before updating docs.

4. **Build compatibility:** All code changes must work when assembled by `build_single.py` into eggcalc.py

5. **Test count:** 1231 tests pass (as of 2026-05-29)

6. **Implementation verification:** All deferred items have been verified working:
   - D1: Return type consistency (evaluator.py:1177-1179)
   - D2: Type stubs (normalize.py, evaluator.py, units.py)
   - D4/D5: Confusables metadata and reproducibility (scripts/generate_confusables.py, data/confusables.txt)
   - D6: Benchmark infrastructure (benchmarks/ with benchmark_evaluate_cached now exported)
   - D7: TypedDict documentation (architecture/synthesis.md)
   - D8: CONTRIBUTING.md path references (all corrected to eggcalc/)

(End of file)