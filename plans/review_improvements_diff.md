# diff.py Module Review - Improvement Plan

## Verified Claims

### levenshtein_distance (lines 118-161)
- **Correct**: Uses O(mn) time with O(min(m,n)) space optimization via two rows
- Dynamic programming recurrence matches doc: `dp[i][j] = min(prev_row[j] + 1, curr_row[j-1] + 1, prev_row[j-1] + (0 if match else 1))`
- Correctly raises ValueError for strings exceeding MAX_LEVENSHTEIN_LEN (10000)

### first_diff (lines 43-76)
- **Correct**: Returns FirstDiff TypedDict with a_index, b_index, a_char, b_char, a_codepoint, b_codepoint
- Correctly returns None when strings are identical
- Codepoint format `U+XXXX` is correct

### diff_spans (lines 205-237)
- **Correct**: Uses difflib.SequenceMatcher (lines 218-232)
- Returns [start, end) half-open intervals as documented
- max_diffs truncation works correctly (lines 234-235)
- Skips 'equal' operations as documented

---

## Discrepancies: Documentation vs Code

### 1. TypedDict vs "Named tuple" (HIGH priority)
**Doc**: Lines 98, 108, 117 describe `FirstDiff`, `DiffSpan`, `CommonPrefixSuffix` as "Named tuple"
**Code**: All three are `TypedDict` classes (lines 15-37)

**Fix needed**: Update architecture/diff.md lines 98-119 to say "TypedDict" instead of "Named tuple"

### 2. common_prefix_suffix Example Error (HIGH priority)
**Doc**: Line 57 shows `common_prefix_suffix("hello", "hell")` → `{'common_prefix_len': 3, 'common_suffix_len': 0}`
**Code**: Implementation returns `{'common_prefix_len': 3, 'common_suffix_len': 1}`

Trace for "hello" vs "hell":
- prefix_len = 3 (h,e,l match, then 'o' != end of "hell")
- min_len = 4, suffix check allows suffix_len < 4-3 = 1
- a[4]='o' == b[3]='o' → suffix_len = 1

**Fix needed**: Update doc example at line 54-55 to show `{'common_prefix_len': 3, 'common_suffix_len': 1}`

### 3. common_prefix_suffix "testing"/"ing" Example (MEDIUM priority)
**Doc**: Line 59 shows `common_prefix_suffix("testing", "ing")` → `{'common_prefix_len': 0, 'common_suffix_len': 0}`
**Code**: Returns `{'common_prefix_len': 0, 'common_suffix_len': 3}`

Trace:
- prefix_len = 0 (no common prefix)
- min_len = 3, suffix check allows suffix_len < 3-0 = 3
- a[6]='g' == b[2]='g', suffix_len=1
- a[5]='n' == b[1]='n', suffix_len=2
- a[4]='i' == b[0]='i', suffix_len=3
- Loop ends, returns suffix_len=3

**Fix needed**: Update doc example at lines 58-59 to show `{'common_prefix_len': 0, 'common_suffix_len': 3}`

### 4. diff_spans merging claim (LOW priority)
**Doc**: Line 139 states "Merges consecutive operations of the same type"
**Code**: No merging logic exists in diff_spans()

**Fix needed**: Remove merging claim from doc or add merging logic to code

---

## Potential Bugs

### 1. longest_common_subsequence Backtracking Logic (HIGH priority)
**Location**: diff.py:197-199

```python
elif prev_row[j - 1] > prev_row[j]:
    i -= 1
else:
    j -= 1
```

**Problem**: `prev_row[j]` is from the current iteration's row after inner loop, not the actual previous row (dp[i-1][j]). This breaks tie-breaking when dp[i-1][j-1] == dp[i-1][j].

**Example where bug manifests**: "ab" vs "ba"
- DP table builds correctly
- Backtracking with bug: trace at (2,2), a[1]='b' != b[0]='a', prev_row[0]=1 == prev_row[1]=1 → moves left (j--)
- Result "b" instead of correct LCS "a" or "b"

**Fix**: Use full DP table instead of two-row optimization for correct backtracking. Change lines 178-187 to:

```python
m, n = len(a), len(b)
dp = [[0] * (n + 1) for _ in range(m + 1)]
for i in range(1, m + 1):
    for j in range(1, n + 1):
        if a[i - 1] == b[j - 1]:
            dp[i][j] = dp[i - 1][j - 1] + 1
        else:
            dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

lcs_len = dp[m][n]
result = []
i, j = m, n
while i > 0 and j > 0:
    if a[i - 1] == b[j - 1]:
        result.append(a[i - 1])
        i -= 1
        j -= 1
    elif dp[i - 1][j] > dp[i][j - 1]:
        i -= 1
    else:
        j -= 1
```

**Priority**: HIGH - Produces incorrect results for certain input pairs

---

## Improvement Suggestions

### Priority HIGH

1. **Fix longest_common_subsequence backtracking bug**
   - Use full O(mn) DP table instead of two-row optimization
   - Fix backtrack tie-breaking to use `dp[i-1][j] > dp[i][j-1]` instead of `prev_row[j-1] > prev_row[j]`

2. **Update architecture/diff.md documentation**
   - Change "Named tuple" to "TypedDict" for FirstDiff, DiffSpan, CommonPrefixSuffix
   - Fix common_prefix_suffix examples
   - Remove false merging claim

### Priority MEDIUM

3. **Add LCS test case** for "ab" vs "ba" expecting length 1 (any valid LCS)

4. **Consider adding type annotations** to function signatures (currently missing return type hints)

### Priority LOW

5. **Add docstring example for first_diff** showing length mismatch case

6. **Consider adding `__all__`** export list for cleaner imports

---

## Summary

The diff.py module is generally well-implemented with correct Levenshtein distance, first_diff, and diff_spans functions. However, **longest_common_subsequence has a critical bug** in its backtracking logic that can produce incorrect results due to the two-row space optimization breaking the tie-breaking invariant.

The documentation has several discrepancies with the code, primarily around class types (TypedDict vs Named tuple) and incorrect examples for common_prefix_suffix.