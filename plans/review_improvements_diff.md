# diff Module Review — Improvement Plan

**Reviewed:** architecture/diff.md against nl_calc/exact/diff.py
**Date:** 2026-05-28

## Verified Claims (with line references)

### `__all__` list is defined ✓
- **Code**: `nl_calc/exact/diff.py:15-25`
- Exports: `FirstDiff`, `CommonPrefixSuffix`, `DiffSpan`, `MAX_LEVENSHTEIN_LEN`, `first_diff`, `common_prefix_suffix`, `levenshtein_distance`, `longest_common_subsequence`, `diff_spans`

### `first_diff(a, b)` returns FirstDiff with position of first difference ✓
- **Code**: `nl_calc/exact/diff.py:56-89`
- Returns `FirstDiff | None` with fields: `a_index`, `b_index`, `a_char`, `b_char`, `a_codepoint`, `b_codepoint`
- Returns `None` when strings are identical
- Codepoint format `U+XXXX` is correct

### `common_prefix_suffix(a, b)` returns CommonPrefixSuffix ✓
- **Code**: `nl_calc/exact/diff.py:92-128`
- Returns `CommonPrefixSuffix` TypedDict with `common_prefix_len` and `common_suffix_len`
- Correctly avoids overlapping prefix/suffix

### `levenshtein_distance(a, b)` returns edit distance (int) ✓
- **Code**: `nl_calc/exact/diff.py:131-174`
- Uses O(mn) time with O(min(m,n)) space optimization via two-row technique
- Raises `ValueError` for strings exceeding `MAX_LEVENSHTEIN_LEN` (10000)
- Recurrence matches documented formula

### `diff_spans(a, b)` returns list of DiffSpan segments that differ ✓
- **Code**: `nl_calc/exact/diff.py:214-246`
- Uses `difflib.SequenceMatcher` (line 227)
- Returns `[start, end)` half-open intervals
- `max_diffs` truncation works correctly (lines 243-244)
- Skips 'equal' operations as documented

### `longest_common_subsequence(a, b)` returns LCS string via dynamic programming ✓
- **Code**: `nl_calc/exact/diff.py:177-211`
- Uses full DP table (`dp[m+1][n+1]`) for both fill and backtrack
- Backtracking tie-breaking correctly uses `dp[i-1][j] > dp[i][j-1]`
- All test cases pass with correct LCS length

---

## Discrepancies Between Documentation and Code

### [HIGH] `FirstDiff` TypedDict fields are incomplete in documentation
- **Documentation says** (lines 88-92):
  ```python
  class FirstDiff(TypedDict):
      position: int
      a_char: str
      b_char: str
  ```
- **Code actually has** (`diff.py:28-35`):
  ```python
  class FirstDiff(TypedDict):
      a_index: int
      b_index: int
      a_char: str
      b_char: str
      a_codepoint: str
      b_codepoint: str
  ```
- **Impact**: Documentation shows 3 fields, code has 6. Also field names differ (`position` vs `a_index`/`b_index`). The data structures section (lines 115-121) correctly lists the 6 fields with `a_index`, `b_index`, `a_codepoint`, `b_codepoint`, suggesting the initial declaration at 88-92 is outdated.

### [HIGH] `common_prefix_suffix` examples are wrong
- **Documentation says** (lines 53-59):
  ```python
  >>> common_prefix_suffix("hello", "hell")
  {'common_prefix_len': 3, 'common_suffix_len': 0}
  >>> common_prefix_suffix("hello", "yo")
  {'common_prefix_len': 0, 'common_suffix_len': 0}
  >>> common_prefix_suffix("testing", "ing")
  {'common_prefix_len': 0, 'common_suffix_len': 0}
  ```
- **Code actually returns**:
  ```
  {'common_prefix_len': 4, 'common_suffix_len': 0}
  {'common_prefix_len': 0, 'common_suffix_len': 1}
  {'common_prefix_len': 0, 'common_suffix_len': 3}
  ```
- **Impact**: All three examples are incorrect. Code is correct; documentation examples are wrong.

### [MEDIUM] `diff_spans` documentation shows `equal` spans that don't appear in output
- **Documentation says** (lines 105-109):
  ```python
  >>> list(diff_spans("hello", "hallo"))
  [DiffSpan(kind='equal', a_span=[0, 2], b_span=[0, 2], a_text='he', b_text='he'),
   DiffSpan(kind='replace', a_span=[2, 3], b_span=[2, 3], a_text='l', b_text='a'),
   DiffSpan(kind='equal', a_span=[3, 5], b_span=[3, 5], a_text='lo', b_text='lo')]
  ```
- **Code actually returns** (line 232: `if tag == "equal": continue`):
  ```python
  [{'kind': 'replace', 'a_span': [1, 2], 'b_span': [1, 2], 'a_text': 'e', 'b_text': 'a'}]
  ```
- **Impact**: Example shows `equal` spans filtered out in code. Actual output only includes `replace`, `insert`, `delete` kinds.

### [LOW] `diff_spans` documentation at line 126 claims `equal` is a valid kind
- **Documentation says** (line 126): `kind`: Type of diff ("equal", "insert", "delete", "replace")
- **Code only returns**: `"replace"`, `"insert"`, `"delete"` (skips `"equal"`)
- **Impact**: Minor inconsistency - doc lists `equal` as possible kind but function never returns it

---

## Potential Bugs

### No bugs found
The implementation is correct. All functions behave as documented:
- `levenshtein_distance`: Correct O(mn) time with space optimization
- `first_diff`: Correct handling of identical strings and length mismatches
- `common_prefix_suffix`: Correct non-overlapping prefix/suffix logic
- `diff_spans`: Correct SequenceMatcher usage with max_diffs truncation
- `longest_common_subsequence`: Correct DP table and backtracking (verified with multiple test cases)

---

## Improvement Suggestions

### HIGH Priority

1. **Fix `FirstDiff` TypedDict declaration in documentation**
   - Location: `architecture/diff.md:88-92`
   - Change from:
     ```python
     class FirstDiff(TypedDict):
         position: int
         a_char: str
         b_char: str
     ```
   - To:
     ```python
     class FirstDiff(TypedDict):
         a_index: int
         b_index: int
         a_char: str
         b_char: str
         a_codepoint: str
         b_codepoint: str
     ```

2. **Fix `common_prefix_suffix` examples in documentation**
   - Location: `architecture/diff.md:53-59`
   - Change `"hello", "hell"` result from `{'common_prefix_len': 3, 'common_suffix_len': 0}` to `{'common_prefix_len': 4, 'common_suffix_len': 0}`
   - Change `"hello", "yo"` result from `{'common_prefix_len': 0, 'common_suffix_len': 0}` to `{'common_prefix_len': 0, 'common_suffix_len': 1}`
   - Change `"testing", "ing"` result from `{'common_prefix_len': 0, 'common_suffix_len': 0}` to `{'common_prefix_len': 0, 'common_suffix_len': 3}`

3. **Fix `diff_spans` example in documentation**
   - Location: `architecture/diff.md:105-109`
   - Either update example to match actual output (no `equal` spans), or clarify that `equal` spans are filtered out

### MEDIUM Priority

4. **Update `kind` documentation for DiffSpan**
   - Location: `architecture/diff.md:126`
   - Remove `"equal"` from list of possible kinds since function never returns it

### LOW Priority

5. **Add test cases for `common_prefix_suffix`** specifically covering:
   - `"hello", "hell"` (prefix overlap with suffix)
   - `"testing", "ing"` (suffix only)

---

## Summary

The `nl_calc/exact/diff.py` implementation is **correct and bug-free**. All five core functions work as expected:
- `levenshtein_distance`: O(mn) time, O(min(m,n)) space ✓
- `first_diff`: Returns FirstDiff or None ✓
- `common_prefix_suffix`: Returns CommonPrefixSuffix with non-overlapping prefix/suffix ✓
- `diff_spans`: Returns DiffSpan list without `equal` spans ✓
- `longest_common_subsequence`: Correct DP with proper backtracking ✓

The **documentation has significant errors**:
1. `FirstDiff` TypedDict declaration shows wrong fields (3 instead of 6)
2. Three `common_prefix_suffix` examples are all wrong
3. `diff_spans` example shows `equal` spans that code filters out

**Recommended action**: Update `architecture/diff.md` to fix the discrepancies listed above.
