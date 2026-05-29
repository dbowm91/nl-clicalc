# diff.py Architecture Review

## Source Files Reviewed
- `nl_calc/exact/diff.py` (246 lines)
- `architecture/diff.md` (161 lines)

## Verification Summary

### Verified Claims

| Function | Status | Notes |
|----------|--------|-------|
| `levenshtein_distance` | MATCHES | O(mn) time, O(min(m,n)) space optimization confirmed |
| `first_diff` | MATCHES | TypedDict fields and return behavior match exactly |
| `common_prefix_suffix` | PARTIAL | Logic correct, but one example in docs is wrong |
| `longest_common_subsequence` | MATCHES | Dynamic programming implementation correct |
| `diff_spans` | PARTIAL | Algorithm correct, but one example in docs is wrong |

---

## Discrepancies Found

### 1. `diff_spans` Example Documentation Error
**Severity**: Medium

**Document says** (line 108-110):
```python
>>> list(diff_spans("hello", "hallo"))
[DiffSpan(kind='replace', a_span=[2, 3], b_span=[2, 3], a_text='l', b_text='a')]
```

**Actual output**:
```python
[{'kind': 'replace', 'a_span': [1, 2], 'b_span': [1, 2], 'a_text': 'e', 'b_text': 'a'}]
```

**Issue**: The document claims the difference is at index 2 (`'l'` → `'a'`), but the actual first difference between "hello" and "hallo" is at index 1 (`'e'` → `'a'`). Characters at index 2 are both `'l'` (equal).

---

### 2. `common_prefix_suffix("hello", "yo")` Example Documentation Error
**Severity**: Medium

**Document says** (line 55-56):
```python
>>> common_prefix_suffix("hello", "yo")
{'common_prefix_len': 0, 'common_suffix_len': 0}
```

**Actual output**:
```python
{'common_prefix_len': 0, 'common_suffix_len': 1}
```

**Issue**: The document claims there is no common suffix, but `'o'` IS a common suffix of "hello" and "yo" (both end with 'o'). The overlap prevention logic correctly allows suffix_len=1 in this case since `prefix_len=0` leaves the full min_len available.

---

## Bugs Identified

### 1. `longest_common_subsequence` Lacks Length Limit (Low Severity)
**Location**: `diff.py:177-211`

**Issue**: Unlike `levenshtein_distance` which has `MAX_LEVENSHTEIN_LEN = 10000`, the LCS function has no maximum length check. The DP table is O(mn) space, which could cause memory issues on very large inputs (e.g., two 50,000-character strings = 2.5 billion cells).

**Recommendation**: Add an optional `max_len` parameter similar to `levenshtein_distance` to bound memory usage.

---

## Improvements Suggested

### 1. Add `max_len` Parameter to `longest_common_subsequence` (Medium Priority)
**Issue**: No bounds checking unlike other functions in the module.

**Suggested fix**:
```python
MAX_LCS_LEN = 10000  # or similar constant

def longest_common_subsequence(a: str, b: str, max_len: int = MAX_LCS_LEN) -> str:
    if len(a) > max_len or len(b) > max_len:
        raise ValueError(f"Input string exceeds max length {max_len}")
    # ... rest of implementation
```

### 2. Document `diff_spans` Return Type Accurately (Low Priority)
**Issue**: The docstring says "Generate a list of diff spans" but doesn't clarify it's a regular list, not a generator/iterator. Users calling `list()` on the result are doing unnecessary work.

**Suggested fix**: Update docstring to clarify it returns `list[DiffSpan]` directly.

### 3. Add Type Hint for `common_prefix_suffix` Return Type (Low Priority)
**Issue**: The docstring says `-> dict` but should use the `CommonPrefixSuffix` TypedDict for consistency with the other functions.

---

## Priority Summary

| Priority | Item | Description |
|----------|------|-------------|
| **High** | Fix `diff_spans` example | Document shows wrong index/text values |
| **High** | Fix `common_prefix_suffix` example | Document shows 0,0 but actual is 0,1 |
| **Medium** | Add `max_len` to LCS | Prevent memory exhaustion on large inputs |
| **Low** | Clarify `diff_spans` return type | State it's a list, not an iterator |
| **Low** | Add return type annotation to `common_prefix_suffix` | Use `CommonPrefixSuffix` TypedDict |

---

## Test Coverage

All existing tests pass (42 diff-related tests in `test_exact.py`). The code implementation is correct; documentation examples are the primary issue.

**Tests verified**:
- `test_first_diff_*` - 5 tests, all pass
- `test_common_prefix_suffix_*` - 4 tests, all pass
- `test_levenshtein_distance_*` - 4 tests, all pass
- `test_longest_common_subsequence_*` - 2 tests, all pass
- `test_diff_spans_*` - 5 tests, all pass
