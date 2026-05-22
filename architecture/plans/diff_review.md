# diff.py Architecture Review

## Verified Claims

1. **Purpose**: String diffing algorithms - MATCHES (lines 1-6)
2. **`levenshtein_distance(a: str, b: str) -> int`**: Exists (line 108), calculates edit distance - MATCHES
3. **`first_diff(a: str, b: str) -> FirstDiff | None`**: Exists (line 42), finds first difference - MATCHES
4. **`common_prefix_suffix(a: str, b: str) -> dict`**: Exists (line 78), finds common prefix/suffix - MATCHES
5. **`diff_spans(a: str, b: str, max_diffs: int = 50) -> list[DiffSpan]`**: Exists (line 154), generates diff spans - MATCHES
6. **Algorithm (Levenshtein)**: Uses dynamic programming with O(mn) time and O(min(m,n)) space optimization - MATCHES (lines 133-150)
7. **Algorithm (diff_spans)**: Uses difflib.SequenceMatcher - MATCHES (line 166)
8. **MAX_LEVENSHTEIN_LEN = 10000**: Exists (line 39) but not documented
9. **FirstDiff structure**: a_index, b_index, a_char, b_char, a_codepoint, b_codepoint - MATCHES (lines 14-21)
10. **DiffSpan structure**: kind, a_span, b_span, a_text, b_text - MATCHES (lines 30-36)

## Discrepancies

1. **Data structure types**:
   - Doc uses `@dataclass class FirstDiff(NamedTuple)` but code uses `class FirstDiff(TypedDict)`
   - Doc uses `@dataclass class DiffSpan(NamedTuple)` but code uses `class DiffSpan(TypedDict)`
   - Functionally similar but different type implementations

2. **Algorithm description mismatch**:
   - Doc (lines 126-131) says "Compute Levenshtein distance matrix, Backtrack to find optimal edit operations"
   - Code actually uses difflib.SequenceMatcher directly, not manual Levenshtein backtracking
   - This is not a bug - SequenceMatcher implements the same logic internally

3. **MAX_LEVENSHTEIN_LEN not documented**: The constant exists (line 39) but arch doc doesn't mention it

## Bugs Found

No bugs. Code is correct and matches documented behavior.

## Improvements

1. **Low Priority**: Update architecture doc to use TypedDict instead of NamedTuple for data structures (or vice versa for consistency)
2. **Low Priority**: Fix algorithm description to reflect that code uses SequenceMatcher directly rather than manual Levenshtein backtracking
3. **Low Priority**: Document MAX_LEVENSHTEIN_LEN constant

## Priority

- **Low**: Documentation improvements only
- **No code changes needed**