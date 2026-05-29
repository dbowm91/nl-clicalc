# Deferred Items Implementation Plan

## Status: COMPLETED (2026-05-29)

All implementable deferred items have been completed as of today.

---

## Summary of Implementation

| Item | Status | Implementation |
|------|--------|----------------|
| D1 | **DONE** | `evaluator.py:1181-1184` - Binary ops return plain types for dimensionless results |
| D2 | Deferred | Type stubs - 25+ improvements possible, 3-5 hours. Can be done incrementally. |
| D3 | Deferred | `load_user_config_extended` - Thread-safety concerns, not worth complexity |
| D4 | **DONE** | `scripts/generate_confusables.py` - Metadata added to header |
| D5 | **DONE** | `data/confusables.txt` cache + version-pinned URL support |
| D6 | **DONE** | `benchmarks/` module with timing utilities |
| D7 | **DONE** | `architecture/synthesis.md` - Added missing TypedDicts |
| D8 | **DONE** | `CONTRIBUTING.md` - Fixed path references |

---

## Verification

All 631 tests pass. Run:
```bash
python3 -m pytest tests/ -x -q
```

Benchmarks can be run with:
```bash
PYTHONPATH=. python3 benchmarks/run.py
```

(End of file)