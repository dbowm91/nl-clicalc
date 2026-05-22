# Review: `nl_calc/exact/diff.py` vs `architecture/diff.md`

## Summary

The `diff.py` module provides string diffing primitives: Levenshtein distance, first difference detection, common prefix/suffix finding, and diff span generation. These are low-level utilities used by `synthesis.py` for text comparison and validation.

## Verified Claims

| Claim in `diff.md` | Implementation | Status |
|---|---|---|
| `levenshtein_distance` uses DP with O(mn) time | Uses two-row DP optimization at `diff.py:133-151` | ✅ Matches |
| `levenshtein_distance` O(min(m,n)) space | Uses `prev_row`/`curr_row` swap pattern | ✅ Matches |
| `first_diff` returns `FirstDiff` with indices, chars, context | Returns TypedDict with `a_index`, `b_index`, `a_char`, `b_char`, `a_context`, `b_context` | ⚠️ **Partial mismatch** (see Issues) |
| `first_diff` returns `None` if identical | `diff.py:75` returns `None` | ✅ Matches |
| `common_prefix_suffix` returns dict with `common_prefix_len` and `common_suffix_len` | Returns `CommonPrefixSuffix` TypedDict | ✅ Matches |
| `diff_spans` returns `DiffSpan` with `kind`, `a_span`, `b_span`, `a_text`, `b_text` | Returns `DiffSpan` TypedDict at `diff.py:174-180` | ✅ Matches |
| `diff_spans` uses Levenshtein to compute optimal edit script | Uses `difflib.SequenceMatcher` instead | ⚠️ **Different algorithm** (see Issues) |
| `levenshtein_distance` examples (`kitten→sitting=3`, `hello→hello=0`) | Tests at `test_exact.py:325-333` verify correct | ✅ Matches |

## Issues Found

### 1. **`first_diff` context fields missing**
- **Doc** (`diff.md:34-36`): Claims `FirstDiff` has `a_context` and `b_context` (5 chars before/after)
- **Actual** (`diff.py:14-21`): Has `a_codepoint` and `b_codepoint` instead
- **Impact**: Documentation is misleading; consumers expecting `a_context`/`b_context` will get `KeyError`

### 2. **`diff_spans` uses difflib, not Levenshtein**
- **Doc** (`diff.md:76`): States "Uses Levenshtein distance to compute optimal edit script"
- **Actual** (`diff.py:166`): Uses `difflib.SequenceMatcher.get_opcodes()`
- **Impact**: Algorithm behavior differs; `difflib.SequenceMatcher` uses a different (heuristic) algorithm for computing opcodes, not true Levenshtein backtracking
- **Note**: This is not necessarily wrong—`difflib.SequenceMatcher` is a reasonable choice—but the documentation is inaccurate

### 3. **`FirstDiff` is TypedDict, not NamedTuple**
- **Doc** (`diff.md:30`): Shows `@dataclass class FirstDiff(NamedTuple):`
- **Actual** (`diff.py:14`): `class FirstDiff(TypedDict):`
- **Impact**: Minor—documentation uses wrong type syntax, but functionality is similar

### 4. **`common_prefix_suffix` doc example incorrect**
- **Doc** (`diff.md:55-56`): Shows `common_prefix_suffix("hello", "hell")` → prefix=3, suffix=0
- **Doc** (`diff.md:56-57`): Shows `common_prefix_suffix("testing", "ing")` → prefix=0, suffix=2
- **Actual**: The second example is wrong. `"testing"` and `"ing"` have no common suffix—they share the suffix `"ing"` only if you consider `"testing"` ending in `"ing"`, but the function works backwards and finds no overlap due to the prefix/suffix non-overlap constraint at line 98-99
- **Test** (`test_exact.py:313-316`): Verifies identical strings return prefix=5, suffix=0 (suffix can't overlap prefix)

### 5. **`diff_spans` excludes "equal" spans correctly**
- **Doc** (`diff.md:79-83`): Example shows equal spans merged into single span
- **Actual** (`diff.py:170-171`): Skips `tag == "equal"` correctly
- **Status**: ✅ Correct

### 6. **`diff_spans` returns empty list for identical strings**
- **Doc** (`diff.md`): No explicit claim
- **Actual** (`diff.py:169-171`): If all spans are "equal", none are added, so empty list returned
- **Test** (`test_exact.py:348-350`): `diff_spans("hello", "hello")` → empty list
- **Status**: ✅ Correct

## Improvement Recommendations

### Priority 1: Fix `first_diff` context documentation

**File**: `architecture/diff.md:34-36`

The doc claims `a_context` and `b_context` fields, but the implementation has `a_codepoint` and `b_codepoint`. Either:
- Update doc to match implementation (change `a_context`/`b_context` to `a_codepoint`/`b_codepoint`), OR
- Update implementation to include context strings if that's the intended design

### Priority 2: Fix `diff_spans` algorithm documentation

**File**: `architecture/diff.md:76`

Change:
```
**Algorithm**: Uses Levenshtein distance to compute optimal edit script, then converts to diff spans.
```

To:
```
**Algorithm**: Uses difflib.SequenceMatcher to compute opcodes, then converts to diff spans.
```

### Priority 3: Update `FirstDiff` type in documentation

**File**: `architecture/diff.md:30`

Change `@dataclass class FirstDiff(NamedTuple):` to `class FirstDiff(TypedDict):`

### Priority 4: Fix `common_prefix_suffix` example

**File**: `architecture/diff.md:56-57`

The example `common_prefix_suffix("testing", "ing")` → suffix=2 is incorrect. Current example `("hello", "hell")` → prefix=3, suffix=0 is correct. Either:
- Remove the `"testing", "ing"` example, OR
- Use a correct example like `common_prefix_suffix("testing", "ing")` → prefix=0, suffix=0`

### Priority 5: Consider using Levenshtein-based diff_spans

**File**: `nl_calc/exact/diff.py:154-185`

If true Levenshtein-based LCS diff is desired:
- Currently uses `difflib.SequenceMatcher` which is a heuristic approach
- A proper Levenshtein backtrack would reconstruct actual edit operations
- This would be a larger change; only needed if the current difflib behavior is insufficient