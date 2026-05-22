# diff.py Review - Improvement Plan

## Verified Claims

| Claim | Status |
|-------|--------|
| `levenshtein_distance` returns int | ✓ Verified |
| `first_diff` returns `FirstDiff \| None` | ✓ Verified |
| `common_prefix_suffix` returns dict-like | ✓ Verified |
| `diff_spans` uses difflib.SequenceMatcher | ✓ Verified |
| Levenshtein uses O(mn) time | ✓ Verified (dynamic programming) |
| Levenshtein uses O(min(m,n)) space | ✓ Verified (two-row optimization) |
| `diff_spans` has max_diffs=50 default | ✓ Verified |
| Data structures have correct fields | ✓ Verified |

## Discrepancies

1. **Data Structure Types (Major)**
   - Doc: `@dataclass class FirstDiff(NamedTuple)` and `@dataclass class DiffSpan(NamedTuple)`
   - Actual: TypedDict classes
   - Impact: Type annotations in doc are incorrect. The codebase uses TypedDict throughout per Python 3.14+ patterns.

2. **Missing Function**
   - `longest_common_subsequence` is implemented (lines 164-202) but not documented
   - This is a functional algorithm that should be documented

3. **Docstring Examples Missing**
   - `common_prefix_suffix` example `testing`/`ing` case not explained in doc
   - Overlap prevention logic should be documented

## Bugs Found

1. **None Critical** - All core algorithms appear correct per test verification

## Improvements with Priority

### High Priority

1. **Document `longest_common_subsequence`**
   - Add to diff.md with recurrence relation and examples
   - Function exists and works but is undocumented

2. **Fix Data Structure Documentation**
   - Change `@dataclass class Xxx(NamedTuple)` to `class Xxx(TypedDict)` in diff.md
   - Note: This is documented correctly in AGENTS.md ("code uses `class Xxx(TypedDict)`")

### Medium Priority

3. **Add Overlap Prevention Explanation to `common_prefix_suffix`**
   - The doc examples show overlap behavior but don't explain why `testing`/`ing` returns 0/0
   - Add note: "Both cannot overlap - if strings share prefix equal to their entire length, suffix is zero"

4. **Add LCS Recurrence to diff.md**
   - Include the dynamic programming recurrence for `longest_common_subsequence`

### Low Priority

5. **Docstring for `diff_spans` mentions "merge consecutive operations"**
   - Actual code does NOT merge - it just collects up to max_diffs
   - If merging is intended, it should be implemented; otherwise remove from doc

6. **Consider Adding `longest_common_subsequence` to Module Index**
   - Currently only lists 4 functions, but 5 exist