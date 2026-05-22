# normalize.py Architecture Review

## Summary

The `normalize.py` module converts natural language math expressions (e.g., "sixteen plus five hundred twenty two") into executable mathematical expressions. It handles word-to-number conversion, operator mapping, tokenization, unit preprocessing, and unit conversion detection.

## Verified Claims

### Documented pipeline steps match implementation

| Document Step | Implementation | Status |
|--------------|----------------|--------|
| `normalize()` - word replacements | `normalize()` at line 734 | ✓ |
| `split_at_operators()` - tokenization | `split_at_operators()` at line 692 | ✓ |
| `convert_from_human_handler()` - number words | `convert_from_human_handler()` at line 618 | ✓ |
| `apply_math_functions()` - function syntax | `apply_math_functions()` at line 554 | ✓ |
| `_handle_unit_conversion_from_tokens()` - unit conversion | `_handle_unit_conversion_from_tokens()` at line 842 | ✓ |
| `_preprocess_units()` - add multiplication before units | `_preprocess_units()` at line 784 | ✓ |

### Data structures match

| Document | Implementation | Status |
|----------|----------------|--------|
| `OPERATOR_CONVERSIONS` | lines 101-119 | ✓ |
| `NUMBER_WORDS` | lines 220-261 | ✓ |

### Performance optimizations match

| Document | Implementation | Status |
|----------|----------------|--------|
| `_UNITS_BY_LENGTH` sorted list | line 46 | ✓ |
| `_UNIT_PREFIXES` set for O(1) lookup | lines 94-97 | ✓ |
| `lru_cache` on `check_if_number()` | line 388 | ✓ |
| Combined regex for single-pass replacement | lines 335-342 | ✓ |

### Constants match

| Document | Implementation | Status |
|----------|----------------|--------|
| `MAX_INPUT_LENGTH = 10000` | line 42 | ✓ |
| `MAX_NESTING_DEPTH = 100` | line 43 | ✓ |

### Dependencies imported from correct modules

| Document | Implementation | Status |
|----------|----------------|--------|
| `evaluator.py`: `EvaluationError`, `evaluate` | line 23 | ✓ |
| `units.py`: `UnitValue`, `UNIT_ALIASES`, `is_unit`, `UNIT_CATEGORIES` | line 24 | ✓ |

## Issues Found

### 1. `check_if_number()` documentation mismatch

**Document says:** "LRU cache on `check_if_number()` (1024 entries)"
**Implementation:** Line 388 shows `@lru_cache(maxsize=1024)` ✓

However, `check_if_number()` returns a **dict**, not a simple boolean. The document at line 40-41 says "Checks if a token represents a number (int, float, hex, binary, octal, complex, unit-suffixed)" but does not document the return type accurately.

### 2. Missing `FUNCTION_MAPPINGS` in architecture doc

**Document** only shows `OPERATOR_CONVERSIONS` and `NUMBER_WORDS` data structures, but `FUNCTION_MAPPINGS` (lines 123-217) is a major data structure with ~100 entries that maps function name aliases to canonical names. This is a significant omission.

### 3. Missing `CONSTANT_WORDS` in architecture doc

**Document** does not mention `CONSTANT_WORDS` (lines 279-300), which maps physical constant names (avogadro, gas constant, planck, etc.) to their symbols. This is a significant feature not documented.

### 4. Missing `STRIPPED_PHRASES` in architecture doc

**Document** does not mention `STRIPPED_PHRASES` (lines 264-276), which removes filler words like "what's", "what is", "calculate", etc.

### 5. Potential bug: `convert_from_human_handler()` behavior on valid tokens

At line 630-637, `convert_from_human_handler()` converts tokens using `word_to_number` replacement with `@` markers:

```python
for word, num_val in word_to_number.items():
    replaced = replaced.replace(word, f"@{num_val}")
```

Then at line 640, `convert_numbers()` is called. However, if a token is already a valid number (e.g., "5"), `check_if_number` returns `{"bool": True}` and the token is passed through unchanged at line 527. This seems correct but the flow could be clearer.

### 6. `_handle_unit_conversion_from_tokens()` limitation

At lines 852-896, the function only detects unit conversion patterns when the "from" unit is at the end of a token (e.g., `2meters` but not `2 meters` as separate tokens after splitting). The preprocessing inserts `*` between number and unit (e.g., `2*m`), but after splitting at operators, `2*m` would be tokenized as `['2', '*', 'm']` not matching the 3-token pattern `['2m', 'in', 'feet']`.

This means `2 meters in feet` would not work as expected since after `split_at_operators()`, the tokens would be `['2', 'meters', 'in', 'feet']`, not `['2meters', 'in', 'feet']`.

### 7. Performance claim: "Unit prefix set `_UNIT_PREFIXES` for O(1) quick rejection"

**Partial issue:** The set is built from `_COMMON_UNITS` (lines 49-91), but the actual unit matching at line 823 uses `_UNITS_BY_LENGTH` which comes from all `UNIT_ALIASES.keys()`. The prefix set only helps reject non-unit cases quickly when the remaining expression starts with something not in any common unit prefix - but actual unit matching still iterates through all `_UNITS_BY_LENGTH`.

## Improvement Recommendations

### 1. Document `FUNCTION_MAPPINGS` (lines 123-217)

Add to architecture doc:
```python
FUNCTION_MAPPINGS = {
    "square root": "sqrt",
    "sine": "sin",
    ...
}
```
This is a critical data structure for natural language function parsing.

### 2. Document `CONSTANT_WORDS` (lines 279-300)

Add to architecture doc as it's part of the word replacement system.

### 3. Document `STRIPPED_PHRASES` (lines 264-276)

Add to architecture doc as it affects normalization behavior.

### 4. Document `check_if_number()` return type accurately

The function returns `dict{"bool": bool, "converted": Any, "type": type}` not a simple boolean.

### 5. Fix unit conversion detection for space-separated units

Current issue at line 842-898: `_handle_unit_conversion_from_tokens()` needs to handle tokens like `['2', 'meters', 'in', 'feet']` in addition to `['2meters', 'in', 'feet']`.

### 6. Consider documenting `validate_for_eval()` (lines 475-490)

Not mentioned in architecture doc. It validates tokens before evaluation.

### 7. Consider documenting `combine_number_parts()` (lines 493-521)

Not mentioned in architecture doc. It handles complex number word combinations like "twenty two" → 22.

## References

- Architecture doc: `architecture/normalize.md`
- Implementation: `nl_calc/normalize.py`
- Main functions: lines 734, 692, 618, 554, 842, 784, 901
- Data structures: lines 101, 220, 123, 279, 264
- Performance optimizations: lines 46, 94, 388, 335