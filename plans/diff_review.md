# diff.py Architecture Review

## Verified Claims

- **levenshtein_distance function exists and works correctly**: kitten/sitting = 3, hello/hello = 0
- **first_diff function exists and works correctly**: Returns correct indices and codepoints, None when identical
- **common_prefix_suffix avoids overlapping prefix/suffix**: Implementation correctly prevents overlap
- **diff_spans uses difflib.SequenceMatcher**: Uses get_opcodes() as documented
- **Data structures exist**: FirstDiff, CommonPrefixSuffix, DiffSpan all present

## Discrepancies

| Item | Documentation | Actual Code | Verdict |
|------|---------------|-------------|---------|
| `common_prefix_suffix("hello", "hell")` | prefix=3 | prefix=4 | **Doc wrong** - code is correct |
| `common_prefix_suffix("testing", "ing")` | prefix=0, suffix=0 | prefix=0, suffix=3 | **Doc wrong** - code is correct |
| `diff_spans("hello", "hallo")` example | replace at index 2 | replace at index 1 | **Doc wrong** - code is correct |
| `FirstDiff` type | `NamedTuple` | `TypedDict` | Implementation correct, doc misleading |
| `DiffSpan` type | `NamedTuple` | `TypedDict` | Implementation correct, doc misleading |
| `CommonPrefixSuffix` returned as dict | Says "Named tuple (returned as dict)" | Returns `CommonPrefixSuffix` TypedDict | Misleading phrasing |

## Bugs Found

### Bug 1: Levenshtein distance not actually used in diff_spans (Medium)
**Location**: `diff.py:154-185`

The architecture doc claims diff_spans "Computes Levenshtein distance matrix" and "Backtrack to find optimal edit operations". The actual implementation uses `difflib.SequenceMatcher.get_opcodes()` which is a different algorithm (heuristic-based Myers diff).

**Impact**: Documentation promises Levenshtein but delivers SequenceMatcher. For most use cases this is fine, but users expecting true optimal edit distance will be confused.

### Bug 2: diff_spans documentation shows incorrect example output (Low)
**Location**: `architecture/diff.md:79-83`

The example shows:
```python
>>> list(diff_spans("hello", "hallo"))
[DiffSpan(kind='equal', ...), DiffSpan(kind='replace', a_span=[2, 3], ...), ...]
```

Actual output: `replace` at `[1, 2]` not `[2, 3]`. "hello"[1] = 'e', not 'l'.

**Impact**: Documentation example is simply wrong and will confuse users.

## Improvements

### Improvement 1: Add LCS (Longest Common Subsequence) function (Medium)
**Rationale**: The architecture index mentions `longest_common_subsequence` but it doesn't exist in the code. This is a standard string similarity metric useful for many applications.

### Improvement 2: Document max_len parameter for levenshtein_distance (Low)
**Rationale**: The function has `MAX_LEVENSHTEIN_LEN = 10000` limit but this isn't mentioned in the architecture doc. Users passing very long strings will get confusing ValueError.

### Improvement 3: Document max_diffs parameter for diff_spans (Low)
**Rationale**: The `max_diffs=50` default limits output but this isn't documented. Users processing large diffs may miss content.

### Improvement 4: Add docstring example for common_prefix_suffix showing overlap prevention (Low)
**Rationale**: The overlap prevention logic is subtle. A good example: `common_prefix_suffix("abc", "bc")` should return prefix=0, suffix=0 (not prefix=2, suffix=2 which would overlap).

### Improvement 5: diff_spans could optionally include equal spans (Low)
**Rationale**: The architecture doc shows equal spans in examples, but code skips them. Making this configurable would provide more flexibility.

## Priority Summary

| Item | Severity | Type |
|------|----------|------|
| Levenshtein not used in diff_spans | Medium | Discrepancy |
| common_prefix_suffix doc examples wrong | Medium | Documentation bug |
| diff_spans doc example wrong | Low | Documentation bug |
| FirstDiff/DiffSpan documented as NamedTuple | Low | Documentation bug |
| Missing longest_common_subsequence | Medium | Missing feature |
| max_len not documented | Low | Documentation gap |
| max_diffs not documented | Low | Documentation gap |

## Recommendations

1. **Fix architecture documentation**: The common_prefix_suffix examples are clearly wrong and should be corrected to match actual output.

2. **Clarify diff_spans algorithm**: Either implement true Levenshtein-based diff (complex) or update doc to say "Uses SequenceMatcher to compute optimal edit script" instead of claiming matrix computation and backtracking.

3. **Consider adding longest_common_subsequence**: This would make the module more complete relative to the architecture doc.

4. **Update type annotations**: The doc mentions NamedTuple for FirstDiff/DiffSpan but code uses TypedDict. Both are valid, but doc should reflect reality.