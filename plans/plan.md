# nl-clicalc Implementation Plan

## Status: COMPLETED (2026-05-29)

All 35 items from the original plan have been verified and implemented.
All 8 deferred items (D1, D4, D5, D6, D7, D8) have been implemented.
See git history for the detailed implementation.

---

## Deferred Items (Design Review Needed)

These items were deferred during the implementation for design review:

| Item | Description | Reason |
|------|-------------|--------|
| D2 | Type stubs | Could add more specific type annotations |
| D3 | `load_user_config_extended` | Not exported by design |

---

## Implementation Notes (2026-05-29)

### Deferred items now implemented:

**D1: Return type consistency** - `evaluator.py:1181-1184`
- Binary operations now return plain types (int/float) for dimensionless results
- `evaluate("5 + 3")` returns `int 8` instead of `UnitValue(8, None)`

**D4/D5: Confusables metadata and reproducibility** - `scripts/generate_confusables.py`
- Added `get_confusables_url()` for version-pinned downloads
- Added local cache at `data/confusables.txt` for reproducible builds
- `confusables.py` header now includes Source-Version, Source-Date, Generated, Entry-Count

**D6: Benchmark infrastructure** - `benchmarks/`
- `benchmark_evaluate()`, `benchmark_evaluate_raw()`, `benchmark_normalize()`, `benchmark_evaluate_cached()`
- Baseline timings in `results.py` with verification utilities

**D7: TypedDict documentation** - `architecture/synthesis.md`
- Added `NormalizationState`, `UnicodeRisks`, `InspectTextNormalized`, `NormalizationFinding`

**D8: CONTRIBUTING.md** - Fixed path references from `clicalc/` to `nl-clicalc/`

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