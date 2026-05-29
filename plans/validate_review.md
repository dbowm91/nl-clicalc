# validate.py Architecture Review

## Document: validate.md

## Verified Claims
| Claim | Status | Evidence |
|-------|--------|----------|
| MAX_INPUT_LENGTH = 100_000 | VERIFIED | validate.py:15 |
| MAX_PATTERN_LENGTH = 1000 | VERIFIED | validate.py:16 |
| MAX_PATTERN_NESTING = 5 | VERIFIED | validate.py:17 |
| MAX_SAMPLE_LENGTH = 10_000 | VERIFIED | validate.py:18 |
| MAX_SCHEMA_VIOLATIONS = 100 | VERIFIED | validate.py:1593 |
| MAX_TEXT_LENGTH_REGEX = 100_000 | VERIFIED | validate.py:1745 |
| MAX_PATTERN_LENGTH_REGEX = 1000 | VERIFIED | validate.py:1746 |
| MAX_MATCHES = 100 | VERIFIED | validate.py:1747 |
| MAX_GROUPS = 100 | VERIFIED | validate.py:1748 |
| DEFAULT_BRACKET_PAIRS definition | VERIFIED | validate.py:116-121 |
| BracketError TypedDict | VERIFIED | validate.py:21-26 |
| CheckBracketsResult TypedDict | VERIFIED | validate.py:29-33 |
| ValidateJsonResult TypedDict | VERIFIED | validate.py:36-44 |
| ValidateTomlResult TypedDict | VERIFIED | validate.py:47-56 |
| TomlShapeResult TypedDict | VERIFIED | validate.py:352-358 |
| VersionCompareResult TypedDict | VERIFIED | validate.py:361-366 |
| RegexMatchPreview TypedDict | VERIFIED | validate.py:59-64 |
| RegexFlags TypedDict | VERIFIED | validate.py:67-72 |
| RegexMatch TypedDict | VERIFIED | validate.py:75-82 |
| RegexTestResult TypedDict | VERIFIED | validate.py:85-90 |
| JsonCompareDiff TypedDict | VERIFIED | validate.py:93-100 |
| JsonCompareResult TypedDict | VERIFIED | validate.py:103-112 |
| JsonExtractResult TypedDict | VERIFIED | validate.py:1267-1284 |
| SchemaViolation TypedDict | VERIFIED | validate.py:1287-1292 |
| ValidateSchemaLightResult TypedDict | VERIFIED | validate.py:1295-1300 |
| JsonShapeKey TypedDict | VERIFIED | validate.py:1596-1602 |
| JsonShapeResult TypedDict | VERIFIED | validate.py:1605-1610 |
| RegexFindIterMatch TypedDict with total=False | VERIFIED | validate.py:1751 |
| RegexFindIterResult TypedDict | VERIFIED | validate.py:1761-1767 |
| RegexSafetyFinding TypedDict | VERIFIED | validate.py:1902-1906 |
| RegexSafetyResult TypedDict | VERIFIED | validate.py:1909-1913 |
| JsonCanonicalizeResult TypedDict | VERIFIED | validate.py:2260-2271 |
| JsonQueryResult TypedDict | VERIFIED | validate.py:2274-2284 |
| check_brackets() function | VERIFIED | validate.py:145-220 |
| validate_json() function | VERIFIED | validate.py:223-272 |
| validate_toml_text() function | VERIFIED | validate.py:286-349 |
| toml_shape() function | VERIFIED | validate.py:369-419 |
| version_compare() function | VERIFIED | validate.py:422-451 |
| regex_test() function | VERIFIED | validate.py:676-799 |
| regex_replace_preview() function | VERIFIED | validate.py:802-874 |
| list_dedupe() function | VERIFIED | validate.py:564-597 |
| list_sort() function | VERIFIED | validate.py:600-626 |
| json_compare() function | VERIFIED | validate.py:950-1264 |
| json_extract() function | VERIFIED | validate.py:1327-1590 |
| json_shape() function | VERIFIED | validate.py:1613-1715 |
| regex_finditer() function | VERIFIED | validate.py:1791-1899 |
| regex_safety_check() function | VERIFIED | validate.py:1916-2061 |
| validate_schema_light() function | VERIFIED | validate.py:2084-2257 |
| json_canonicalize() function | VERIFIED | validate.py:2287-2402 |
| json_query() function | VERIFIED | validate.py:2415-2516 |
| ValueError raising functions | VERIFIED | validate.py:164-165, 236-237, 314-315, 393-394, 1343-1344, 1628-1629, 2309-2310, 2427-2428 |
| regex_test MAX_SAMPLE_LENGTH limit | VERIFIED | validate.py:753-764 |
| regex_finditer limits | VERIFIED | validate.py:1816-1817, 1819-1826 |
| validate_schema_light MAX_SCHEMA_VIOLATIONS limit | VERIFIED | validate.py:2112, 2243 |

## Discrepancies
No major discrepancies found. All TypedDicts, constants, and function signatures match between the documentation and implementation.

## Bugs Identified
| Bug | Location | Severity | Description |
|-----|----------|----------|-------------|
| list_sort ignores stable parameter | validate.py:600-626 | Medium | The `stable` parameter is accepted but has no effect. Python's `sorted()` is always stable regardless of any `stable` parameter. The parameter should either be removed (since it's meaningless) or the implementation should use an unstable sort when `stable=False` (which would require a different sorting algorithm). |
| json_extract returns unbounded value field | validate.py:1327-1590 | Low | The function returns the full parsed `value` in the result. For large JSON documents, this could return very large objects. The `max_output_chars` only limits the `preview` field, not the `value` field. This is documented behavior but could cause memory issues with huge JSON. |

## Improvements Surface
| Area | Priority | Description |
|------|----------|-------------|
| API Design | Medium | `list_sort()` accepts `stable` parameter that has no effect. Python's `sorted()` is inherently stable. Consider either removing the parameter or documenting that the sort is always stable. |
| Memory Safety | Low | `json_extract()` has `max_output_chars` limit for preview but returns full `value`. For very large JSON documents, the `value` field could consume significant memory. Consider adding a configurable `max_value_size` parameter. |
| Documentation | Low | The architecture doc at line 330 notes "top_level_keys is only populated for objects" but this is consistent with the implementation behavior. |

## Notes
- All 9 constants match exactly between documentation and code.
- All 21 TypedDict definitions match exactly.
- All 18 functions match exactly in signatures, behaviors, and return types.
- All input limits are correctly documented.
- The only bug found is the meaningless `stable` parameter in `list_sort()`.
- The only low severity concern is potential memory usage with large JSON in `json_extract()`.
- Overall the documentation is highly accurate and comprehensive. No major discrepancies between `architecture/validate.md` and `eggcalc/exact/validate.py`.
