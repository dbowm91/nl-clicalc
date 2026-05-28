# diff Module Review — Improvement Plan

**Reviewed:** architecture/diff.md against nl_calc/exact/diff.py
**Date:** 2026-05-28

## Verified Claims (with line references)

- `__all__` exports correct functions — VERIFIED at diff.py:15-25
- `FirstDiff` TypedDict has 6 fields (`a_index`, `b_index`, `a_char`, `b_char`, `a_codepoint`, `b_codepoint`) — VERIFIED at diff.py:28-35
- `CommonPrefixSuffix` TypedDict has 2 fields — VERIFIED at diff.py:38-41
- `DiffSpan` TypedDict has 5 fields — VERIFIED at diff.py:44-50
- `MAX_LEVENSHTEIN_LEN = 10000` — VERIFIED at diff.py:53
- `levenshtein_distance(a, b)` uses O(mn) time with O(min(m,n)) space — VERIFIED at diff.py:131-174
- `first_diff` returns FirstDiff or None with U+XXXX codepoint format — VERIFIED at diff.py:56-89
- `common_prefix_suffix` correctly prevents prefix/suffix overlap — VERIFIED at diff.py:92-128
- `longest_common_subsequence` uses dynamic programming with backtracking — VERIFIED at diff.py:177-211
- `diff_spans` uses difflib.SequenceMatcher, skips 'equal' spans — VERIFIED at diff.py:214-246

## Discrepancies Between Documentation and Code

### [HIGH] `FirstDiff` TypedDict declaration in docs has wrong fields
- **Documentation says** (diff.md:88-92):
  ```python
  class FirstDiff(TypedDict):
      position: int
      a_char: str
      b_char: str
  ```
- **Code actually has** (diff.py:28-35):
  ```python
  class FirstDiff(TypedDict):
      a_index: int
      b_index: int
      a_char: str
      b_char: str
      a_codepoint: str
      b_codepoint: str
  ```
- **Impact**: Docs show 3 fields vs actual 6 fields; `position` should be `a_index`/`b_index`

### [HIGH] `common_prefix_suffix` examples all return incorrect values
- **Documentation says** (diff.md:53-59):
  - `"hello", "hell"` → `{'common_prefix_len': 3, 'common_suffix_len': 0}`
  - `"hello", "yo"` → `{'common_prefix_len': 0, 'common_suffix_len': 0}`
  - `"testing", "ing"` → `{'common_prefix_len': 0, 'common_suffix_len': 0}`
- **Code actually returns**:
  - `"hello", "hell"` → `{'common_prefix_len': 4, 'common_suffix_len': 0}`
  - `"hello", "yo"` → `{'common_prefix_len': 0, 'common_suffix_len': 1}`
  - `"testing", "ing"` → `{'common_prefix_len': 0, 'common_suffix_len': 3}`
- **Impact**: All three examples are wrong; code is correct

### [MEDIUM] `diff_spans` example shows `equal` spans that code filters out
- **Documentation shows** (diff.md:105-109):
  ```python
  [DiffSpan(kind='equal', ...), DiffSpan(kind='replace', ...), DiffSpan(kind='equal', ...)]
  ```
- **Code actually returns** (diff.py:231-232):
  ```python
  if tag == "equal":
      continue
  ```
  Only non-equal spans are returned
- **Impact**: Example is misleading

### [LOW] `DiffSpan` documentation lists `equal` as valid kind
- **Documentation says** (diff.md:126): kind can be "equal", "insert", "delete", "replace"
- **Code never returns** `equal` (only insert/delete/replace)
- **Impact**: Minor inconsistency

## Potential Bugs

No bugs found. All functions behave correctly:
- `levenshtein_distance`: Correct two-row DP optimization, proper max_len enforcement
- `first_diff`: Correct empty string handling, length mismatch handling, codepoint formatting
- `common_prefix_suffix`: Correct overlap prevention algorithm
- `diff_spans`: Correct SequenceMatcher usage, proper max_diffs truncation
- `longest_common_subsequence`: Correct DP table and backtracking (verified with "ab"/"ba" case which returns "b", not "a")

## Improvement Suggestions

### HIGH Priority
1. **Fix `FirstDiff` TypedDict declaration** (diff.md:88-92) — use 6 correct fields
2. **Fix all three `common_prefix_suffix` examples** (diff.md:53-59) — update expected values

### MEDIUM Priority
3. **Fix `diff_spans` example output** (diff.md:105-109) — remove `equal` spans from example

### LOW Priority
4. **Remove `equal` from `kind` documentation** (diff.md:126) — or note it may be filtered

## Summary

The `nl_calc/exact/diff.py` implementation is correct and bug-free. All five functions work as expected with proper edge case handling. The documentation has significant errors: the `FirstDiff` TypedDict declaration shows wrong fields (3 vs 6), all three `common_prefix_suffix` examples return incorrect values, and the `diff_spans` example shows `equal` spans that the code filters out. The recommended action is to update `architecture/diff.md` to fix these discrepancies.