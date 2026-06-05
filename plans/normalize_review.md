# normalize Architecture Review

## Document: normalize.md

## Verified Claims
| Claim | Status | Evidence |
|-------|--------|----------|
| `run` exported | VERIFIED | normalize.py:43 |
| `normalize` exported | VERIFIED | normalize.py:44 |
| `normalize_expression` exported | VERIFIED | normalize.py:45 |
| `main` exported | VERIFIED | normalize.py:46 |
| `print_help` exported | VERIFIED | normalize.py:47 |
| `NORMALIZE` exported | VERIFIED | normalize.py:48 |
| `PATTERNS` exported | VERIFIED | normalize.py:49 |
| `MAX_INPUT_LENGTH` = 10000 | VERIFIED | normalize.py:54 |
| `MAX_NESTING_DEPTH` = 100 | VERIFIED | normalize.py:55 |
| `evaluate` re-exported from evaluator | VERIFIED | normalize.py:25 |
| `EvaluationError` re-exported from evaluator | VERIFIED | normalize.py:25 |
| `UnitValue` re-exported from units | VERIFIED | normalize.py:37 |
| `normalize()` signature | VERIFIED | normalize.py:911 |
| `normalize_expression()` signature | VERIFIED | normalize.py:1128 |
| `run()` signature | VERIFIED | normalize.py:1176 |
| `check_if_number()` returns dict with bool/converted/type | VERIFIED | normalize.py:400-484 |
| `_build_config()` returns tuple[dict, dict] | VERIFIED | normalize.py:315-387 |
| OPERATOR_CONVERSIONS["+"] = ["plus", "positive"] | VERIFIED | normalize.py:114 |
| OPERATOR_CONVERSIONS["-"] = ["minus", "negative"] | VERIFIED | normalize.py:115 |
| OPERATOR_CONVERSIONS["*"] includes "times", "multiplied by", "of" | VERIFIED | normalize.py:116 |
| OPERATOR_CONVERSIONS["/"] includes "divided by", "over", "per", "divide" | VERIFIED | normalize.py:117 |
| OPERATOR_CONVERSIONS["IN"] = ["in", "into"] | VERIFIED | normalize.py:129 |
| OPERATOR_CONVERSIONS["TO"] = ["to", "as"] | VERIFIED | normalize.py:130 |
| STRIPPED_PHRASES includes "what's", "what is", "a ", "?", "calculate", "compute", "convert", "tell me", "give me", "the " | VERIFIED | normalize.py:276-288 |
| PATTERNS["space"] for multiple whitespace | VERIFIED | normalize.py:370 |
| PATTERNS["point"] for decimal point | VERIFIED | normalize.py:371 |
| PATTERNS["negative"] for negative sign | VERIFIED | normalize.py:372 |
| PATTERNS["thousands_separator"] for comma | VERIFIED | normalize.py:373 |
| PATTERNS["inline_negative"] for hyphenated words | VERIFIED | normalize.py:374 |
| PATTERNS["parenthesis"] for ( ) | VERIFIED | normalize.py:375 |
| PATTERNS["operators"] for valid operator symbols | VERIFIED | normalize.py:376 |
| PATTERNS["stripped_chars"] for phrases to remove | VERIFIED | normalize.py:378 |
| PATTERNS["int"] for integer pattern | VERIFIED | normalize.py:379 |
| PATTERNS["float"] for float pattern | VERIFIED | normalize.py:380 |
| Words sorted by length descending in config | VERIFIED | normalize.py:334-336, 354 |
| Security: No eval() usage - uses AST parsing | VERIFIED | normalize.py uses evaluate() which uses AST |
| Security: Input length limits enforced | VERIFIED | normalize.py:1148-1149 |
| Security: Nesting depth limits enforced | VERIFIED | normalize.py:947-948 |
| Security: Invalid tokens raise ValueError | VERIFIED | normalize.py:501 |

## Discrepancies
1. **[MISMATCH]**: Module Dependencies - exact imports incomplete
   - Document states (line 259): `exact (inspect_text, count_chars, regex_test)`
   - Code actually imports (lines 26-36):
     ```
     from .exact import (
         count_chars,
         dotenv_validate,
         inspect_text,
         line_range_extract,
         markdown_structure,
         patch_apply_check,
         regex_test,
         shell_split,
         text_replace_check,
     )
     ```
   - 6 additional functions are imported but not documented: `dotenv_validate`, `line_range_extract`, `markdown_structure`, `patch_apply_check`, `shell_split`, `text_replace_check`

2. **[MISMATCH]**: OPERATOR_CONVERSIONS["**"] missing variant
   - Document states (line 61): `["^", "raised to", "to the power of"]`
   - Code actually (line 118): `["^", "raised to", "raised to the power", "to the power of"]`
   - Additional entry "raised to the power" exists in code but not documented

3. **[MISMATCH]**: CONSTANT_WORDS examples incomplete
   - Document shows 10 constant entries (lines 105-111)
   - Code contains 21 entries (lines 292-312)
   - Missing in doc: "boltzmann"/"boltzmann constant", "avogadros", "speed of light in vacuum", "c zero", "amu", "mu0", "vacuum permeability", "g", "G", "gravitational constant", "me", "mp", "mn", "re", "alpha", "rydberg", "stefan", "wien", etc.

4. **[MISMATCH]**: `valid_operations` pattern description incomplete
   - Document describes (line 217): "Valid operation/constant names"
   - Code actually includes (line 383): symbols + FUNCTION_MAPPINGS.values() + CONSTANT_WORDS.keys()
   - Document does not mention that function names are also included

5. **[MISMATCH]**: Private constants documented as public
   - Document (lines 232-234) shows:
     ```
     | _UNITS_BY_LENGTH | list | Units sorted by length for parsing |
     | _COMMON_UNITS | list | Frequently used units for fast lookup |
     | _UNIT_PREFIXES | set | O(1) lookup for unit starts |
     ```
   - These are prefixed with underscore indicating private, and none appear in `__all__` (lines 39-52)

6. **[MISMATCH]**: Private function documented
   - Document (line 221): `_build_config() -> tuple[dict, dict]` is shown but this is a private function (leading underscore) not in `__all__`

## Bugs Identified
| Bug | Location | Severity | Description |
|-----|----------|----------|-------------|
| No bugs identified | - | - | Code appears functionally correct |

## Improvements Surface
| Area | Priority | Description |
|------|----------|-------------|
| Documentation | High | Module dependencies section (line 259) is significantly incomplete - only lists 3 of 9 actual imports from `exact` module |
| Documentation | Medium | CONSTANT_WORDS section shows ~10 entries but 21 exist in code - should either show all or clarify with ellipsis |
| Documentation | Medium | OPERATOR_CONVERSIONS for "**" omits "raised to the power" variant present in code |
| Documentation | Medium | `valid_operations` pattern description doesn't mention it includes function names |
| Documentation | Low | Private functions/constants (_build_config, _UNITS_BY_LENGTH, _COMMON_UNITS, _UNIT_PREFIXES) are documented but not exported - could be removed from docs or moved to internal section |
| Code | Low | `_rebuild_config()` function (line 394) is never called in the codebase - dead code or incomplete feature? |

## Notes
- The architecture document is generally well-structured and accurate for the major claims about function signatures, constants, and the processing pipeline
- The most significant discrepancy is the incomplete documentation of imports from the `exact` module, which represents 6 missing symbols
- The NUMBER_WORDS and FUNCTION_MAPPINGS documentation uses partial examples with ellipsis appropriately, but CONSTANT_WORDS documentation is similarly incomplete without clear indication
- The document's description of the processing pipeline (lines 186-200) is accurate and helpful
- The document correctly notes that "No eval() usage — uses AST parsing" which is a key security feature
- All security-related claims (input limits, nesting depth, invalid token handling) are verified
