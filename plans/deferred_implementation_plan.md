# Deferred Items Implementation Plan

## Status: IN PROGRESS (2026-05-29)

Implementation plan for the 8 deferred items from `plans/plan.md`.

---

## Item D1: Return Type Consistency

### Problem
Binary operations always return `UnitValue` even for dimensionless results:
```python
evaluate("5 + 3")  # Returns UnitValue(8, None), not int 8
evaluate("42")     # Returns int 42
```

### Root Cause
`evaluator.py:1182` unconditionally wraps results in `UnitValue`:
```python
return UnitValue(result, result_unit)  # Always wraps
```

### Implementation
Add conditional return at `evaluator.py:1182`:
```python
# Before
return UnitValue(result, result_unit)

# After
if result_unit is None:
    return result
return UnitValue(result, result_unit)
```

### Risk Mitigation
- All 631 tests use defensive patterns like `isinstance(result, UnitValue) or result == 8`
- Tests will pass - the defensive patterns accommodate both behaviors

### Files Affected
- `nl_calc/evaluator.py` (line 1182)

---

## Item D4: Confusables Regeneration Metadata

### Problem
Generated `confusables.py` has no metadata about source version or generation date.

### Implementation
Modify `scripts/generate_confusables.py` to add metadata:
1. Parse version from downloaded `confusables.txt` header
2. Add generation timestamp
3. Add entry count
4. Update docstring header in generated file

### Changes to `generate_python_file()`:
```python
def generate_python_file(
    confusables: dict[str, str],
    output_path: Path,
    source_version: str | None = None,
    source_date: str | None = None,
) -> None:
    # Add metadata to docstring
    metadata = []
    if source_version:
        metadata.append(f"Source-Version: {source_version}")
    if source_date:
        metadata.append(f"Source-Date: {source_date}")
    metadata.append(f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
    metadata.append(f"Entry-Count: {len(confusables)}")
```

### Files Affected
- `scripts/generate_confusables.py`

---

## Item D5: Confusables Reproducibility Test

### Problem
Live Unicode server updates cause regeneration to produce different output over time.

### Implementation
1. Add version-pinned URL support to `generate_confusables.py`
2. Create `data/confusables.txt` local cache for reproducible builds
3. Add a test that verifies regeneration produces identical output

### Changes to `generate_confusables.py`:
```python
def get_confusables_url(version: str | None = None) -> str:
    """Get URL for confusables.txt, optionally version-pinned."""
    if version:
        return f"https://www.unicode.org/Public/security/{version}/confusables.txt"
    return DEFAULT_URL  # .../latest/

def fetch_confusables_txt(use_cache: bool = False) -> tuple[str, str | None]:
    """Fetch confusables.txt with optional local cache."""
    if use_cache:
        cache_path = Path(__file__).parent.parent / "data" / "confusables.txt"
        if cache_path.exists():
            return cache_path.read_text(encoding="utf-8"), None
    # ... HTTP fetch ...
```

### New Test File: `tests/test_confusables_reproducibility.py`
```python
def test_regeneration_produces_identical_output():
    """Verify that regeneration produces identical output."""
    # Hash current file
    # Re-run generation
    # Compare hash
    # Assert identical
```

### Files Affected
- `scripts/generate_confusables.py` (modified)
- `tests/test_confusables_reproducibility.py` (new)
- `data/confusables.txt` (cached version, added to .gitignore)

---

## Item D6: Performance Benchmarking Infrastructure

### Problem
No benchmark suite exists to verify documented performance timings.

### Implementation
Create `benchmarks/` directory with:

#### `benchmarks/__init__.py`
Empty, makes directory a package.

#### `benchmarks/run.py`
```python
"""Benchmark runner for nl-clicalc."""
import timeit
import statistics

# Core benchmarks
def benchmark_evaluate(n: int = 1000) -> dict:
    """Benchmark evaluate() for pre-normalized expressions."""

def benchmark_evaluate_raw(n: int = 1000) -> dict:
    """Benchmark evaluate_raw() for NL expressions."""

def benchmark_normalize(n: int = 1000) -> dict:
    """Benchmark normalization alone."""
```

#### `benchmarks/results.py`
```python
"""Baseline performance results."""
BASELINE = {
    "evaluate_simple": {"mean": 10e-6, "unit": "seconds"},
    # ... documented timings from README
}
```

### Files Affected
- `benchmarks/__init__.py` (new)
- `benchmarks/run.py` (new)
- `benchmarks/results.py` (new)

---

## Item D7: TypedDict Documentation for Synthesis

### Problem
8 TypedDicts in `synthesis.py` are missing from `architecture/synthesis.md`.

### Missing TypedDicts:
1. `NormalizationState`
2. `UnicodeRisks`
3. `InspectTextNormalized`
4. `NormalizationFinding`
5. `ListCompareOrderedResult`
6. `ListCompareSetResult`
7. `ListCompareMultisetResult`
8. `TextWindowPosition`

### Implementation
Add sections to `architecture/synthesis.md`:
- Standalone definitions for embedded types
- Document sub-types used in list_compare and text_window

### Estimated: ~80-100 lines of documentation

### Files Affected
- `architecture/synthesis.md`

---

## Item D8: Documentation Fixes (Not Full Reorganization)

### Problem
- CHANGELOG conflict between root and docs/changelog.md
- CONTRIBUTING.md references wrong directory (`clicalc/` vs `nl-clicalc/`)

### Implementation
1. Remove `docs/changelog.md` (duplicate content)
2. Update `CONTRIBUTING.md` path reference

### Files Affected
- `docs/changelog.md` (delete)
- `CONTRIBUTING.md` (edit path reference)

---

## Items Deliberately Not Implementing

| Item | Reason |
|------|--------|
| D2 | Type stubs - 25+ improvements needed, 3-5 hours effort. Can be done incrementally. |
| D3 | `load_user_config_extended` - thread-safety concerns, edge case feature, not worth complexity |

---

## Implementation Order

1. **D1** (HIGH priority, low effort, significant API improvement)
2. **D4** (Medium priority, low effort)
3. **D5** (Medium priority, medium effort, depends on D4)
4. **D6** (Medium priority, medium effort)
5. **D7** (Low priority, medium effort)
6. **D8** (Low priority, low effort)

---

## Verification

After each item:
```bash
python3 -m pytest tests/ -x -q
```

All 631 tests must continue to pass.

(End of file)