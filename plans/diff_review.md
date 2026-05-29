# Diff Architecture Review

**Document:** `architecture/diff.md`
**Code:** `eggcalc/exact/diff.py`
**Date:** 2026-05-29

---

## Summary

The architecture document has multiple discrepancies ranging from incorrect docstring examples to undocumented parameters and types. The implementation is largely correct, but the documentation contains several errors that could mislead users.

---

## Discrepancies

### D1: `common_prefix_suffix` Docstring Examples Incorrect

**Location:** `architecture/diff.md:55-57` vs `diff.py:104-111`

**Issue:** Two of three docstring examples are incorrect:

1. `common_prefix_suffix("prefix_middle_suffix", "xxx_middle_yyy")`
   - Documented result: `{'common_prefix_len': 0, 'common_suffix_len': 0}`
   - Actual result: `{'common_prefix_len': 0, 'common_suffix_len': 13}`
   - Both strings share suffix "_middle_suffix" of length 13

2. `common_prefix_suffix("testing", "ing")`
   - Documented result: `{'common_prefix_len': 0, 'common_suffix_len': 0}`
   - Actual result: `{'common_prefix_len': 0, 'common_suffix_len': 3}`
   - No common prefix exists, but "ing" is a valid suffix of "testing"

3. `common_prefix_suffix("hello world", "hello there")`
   - Documented result: `{'common_prefix_len': 6, 'common_suffix_len': 0}` ✓ (correct)

**Severity:** Medium (docstring examples contradict actual behavior, though the implementation is correct)

---

### D2: `common_prefix_suffix` Return Type Mismatch

**Location:** `architecture/diff.md:48` vs `diff.py:37-40`

**Issue:** The architecture document shows:
```python
>>> common_prefix_suffix("hello", "yo")
{'common_prefix_len': 0, 'common_suffix_len': 1}
```

The function signature section states it returns `dict`, but the implementation returns `CommonPrefixSuffix` TypedDict. While the TypedDict fields match the dict display format, the documented return type is imprecise.

**Severity:** Low (output format is correct, but type annotation is more specific than documented)

---

### D3: Undocumented `max_len` Parameter and Constant

**Location:** `architecture/diff.md:9-22` vs `diff.py:52,130-147`

**Issue:** The `levenshtein_distance` function has an undocumented `max_len` parameter:

```python
def levenshtein_distance(a: str, b: str, max_len: int = MAX_LEVENSHTEIN_LEN) -> int:
```

The architecture document shows:
```python
>>> levenshtein_distance("kitten", "sitting")
3
```

But makes no mention of:
- The `MAX_LEVENSHTEIN_LEN = 10000` constant
- The `max_len` parameter with default value 10000
- The `ValueError` raised when input exceeds max length

**Severity:** Medium (important boundary condition undocumented)

---

## Verified Correct Items

The following items were verified as correctly documented and implemented:

- `levenshtein_distance` algorithm with O(mn) time and O(min(m,n)) space optimization ✓
- `levenshtein_distance` recurrence relation matches implementation ✓
- `first_diff` TypedDict fields and example output ✓
- `FirstDiff` TypedDict structure matches documented format ✓
- `DiffSpan` TypedDict structure matches documented format ✓
- `common_prefix_suffix` overlap prevention logic correct (suffix can't extend into prefix region) ✓
- `longest_common_subsequence` algorithm uses dynamic programming correctly ✓
- `diff_spans` uses `difflib.SequenceMatcher` as documented ✓
- `diff_spans` skips "equal" segments as documented ✓

---

## Missing Documentation

### M1: `CommonPrefixSuffix` TypedDict Not Explicitly Documented

**Location:** `diff.py:37-40`

The architecture shows `CommonPrefixSuffix` as a TypedDict class definition but doesn't document its purpose or fields in the Data Structures section. Users must infer from usage.

**Recommendation:** Add explicit documentation:
```python
### CommonPrefixSuffix (TypedDict)

TypedDict containing:
- `common_prefix_len`: Length of common prefix
- `common_suffix_len`: Length of common suffix (non-overlapping with prefix)
```

**Severity:** Low

---

### M2: `MAX_LEVENSHTEIN_LEN` Constant Not Documented

**Location:** `diff.py:52`

The architecture document does not mention this constant, which bounds input size for security/performance reasons.

**Severity:** Low

---

### M3: `max_diffs` Truncation Behavior Not Documented

**Location:** `architecture/diff.md:70-108` vs `diff.py:213-245`

The architecture shows the `diff_spans` function but doesn't document:
- The `max_diffs` parameter with default value 50
- That spans are truncated when exceeding `max_diffs`
- That truncation happens mid-iteration, potentially cutting off related opcodes

**Severity:** Medium (important for understanding output completeness)

---

## Documentation Clarifications Needed

### C1: `diff_spans` Example Uses `list()` Unnecessarily

**Location:** `architecture/diff.md:106`

```python
>>> list(diff_spans("hello", "hallo"))
[DiffSpan(kind='replace', a_span=[1, 2], b_span=[1, 2], a_text='e', b_text='a')]
```

The function returns `list[DiffSpan]`, not a generator. Using `list()` wrapper is unnecessary and could mislead users about the return type.

**Recommendation:** Remove `list()` wrapper.

---

### C2: `common_prefix_suffix` Overlap Prevention Wording

**Location:** `architecture/diff.md:48-58`

The docstring states:
> Avoids overlapping prefix/suffix. If the entire string would be overlapped, both prefix and suffix are zero.

This wording is ambiguous. For "prefix_middle_suffix" vs "xxx_middle_yyy":
- No common prefix (prefix_len = 0)
- With prefix_len = 0, the entire string is available for suffix matching
- The suffix "_middle_suffix" (13 chars) is found

The phrase "If the entire string would be overlapped" could be interpreted as applying here, but it doesn't—the overlap check only prevents suffix from extending INTO the prefix region, not from matching when prefix is empty.

**Recommendation:** Clarify: "The suffix cannot extend into the prefix region. When there is no common prefix, the full string is available for suffix matching."

---

## Potential Bug in Implementation

### B1: `diff_spans` Truncation May Split Related OpCodes

**Location:** `diff.py:229-243`

```python
for tag, i1, i2, j1, j2 in matcher.get_opcodes():
    if tag == "equal":
        continue
    kind = tag
    spans.append(DiffSpan(...))
    if len(spans) >= max_diffs:
        break
```

When `len(spans)` reaches `max_diffs`, the loop breaks immediately. If a replace operation spans multiple positions and the truncation occurs mid-opcode, the diff is incomplete. This could produce invalid diff output.

**Note:** This is a potential issue but may be acceptable depending on use case requirements. The architecture doesn't specify whether truncation should be atomic or can split opcodes.

**Severity:** Low (edge case, may be acceptable)

---

## Recommendations

1. **Fix `common_prefix_suffix` docstring examples** - Examples 1 and 2 return incorrect values
2. **Document `MAX_LEVENSHTEIN_LEN` constant** and `max_len` parameter for `levenshtein_distance`
3. **Document `max_diffs` parameter** for `diff_spans` and truncation behavior
4. **Clarify `CommonPrefixSuffix` return type** as TypedDict, not plain dict
5. **Remove `list()` wrapper** from `diff_spans` example
6. **Clarify overlap prevention** wording in docstring

---

## Risk Assessment

| Category | Risk Level | Notes |
|----------|------------|-------|
| Security | Low | Length-bounded operations, no external calls |
| Correctness | Low | Implementation correct, doc examples wrong |
| Usability | Medium | Undocumented parameters may surprise users |
| Completeness | Low | Core functions documented, minor omissions |

No critical issues found that would prevent the module from functioning as designed.
