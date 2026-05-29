# measure.py Architecture Review

## Document: architecture/measure.md

## Verified Claims
| Claim | Status | Evidence |
|-------|--------|----------|
| LineMetrics TypedDict fields | VERIFIED | measure.py:15-23 |
| WordMetrics TypedDict fields | VERIFIED | measure.py:26-32 |
| CharCategoryMetrics TypedDict fields | VERIFIED | measure.py:35-43 |
| line_metrics() function signature | VERIFIED | measure.py:66-125 |
| word_metrics() function signature | VERIFIED | measure.py:128-197 |
| char_category_metrics() function signature | VERIFIED | measure.py:200-262 |
| average_word_length rounded to 2 decimal places | VERIFIED | measure.py:196 |
| newline_style detection algorithm | VERIFIED | measure.py:46-63 |
| control_chars excludes Cf per UTS #55 | VERIFIED | measure.py:245-248 |
| "none" returned when no newlines present | VERIFIED | measure.py:62-63 |
| char_category_metrics example output | VERIFIED | measure.py:80-83 (verified trace) |
| word_metrics example for "hello world hello" | VERIFIED | measure.py:47-50 (verified trace) |

## Discrepancies
| Claim | Status | Issue |
|-------|--------|-------|
| line_metrics("hello\nworld\n") returns lines=3 | INCORRECT | Document claims lines=3, implementation returns lines=2. Python's splitlines() on "hello\nworld\n" returns ["hello", "world"] (2 elements). The trailing empty string after final \n is NOT included. |
| Word definition: "Sequences of non-whitespace characters" | INCOMPLETE | Document describes words as any whitespace-separated token, but implementation filters to only tokens containing at least one alphabetic character (measure.py:154). Token "123" would NOT be counted as a word. |

## Bugs Identified
| Bug | Location | Severity | Description |
|-----|----------|----------|-------------|
| None | - | - | No bugs found; implementation is consistent with its documented behavior (except for example discrepancies). |

## Improvements Surface
| Area | Priority | Description |
|------|----------|-------------|
| Documentation | Medium | The line_metrics example at lines 25-28 of architecture/measure.md shows `lines=3` for input "hello\nworld\n". This is incorrect; the correct value is `lines=2`. The example should be changed to match the actual behavior, or a different example should be used that more clearly illustrates the line counting behavior. |
| Documentation | Low | The word definition at line 44 states "Sequences of non-whitespace characters" but the implementation only counts tokens containing at least one alphabetic character. Consider clarifying the definition to: "Sequences of non-whitespace characters that contain at least one letter." Or if the intent was to count all tokens, the implementation should be changed to remove the `any(c.isalpha() for c in t)` filter. |

## Notes
- All three TypedDict definitions match exactly between documentation and code.
- All three function signatures match exactly.
- The newline style detection algorithm (measure.py:46-63) correctly implements the documented behavior at architecture/measure.md:98-103.
- The char_category_metrics classification logic (letters L*, digits N*, punctuation P*, symbols S*, spaces Z*, control C* excluding Cf, combining marks M*) matches the documentation exactly.
- The word_metrics sentence estimation uses regex pattern r"[.!?]+(?:\s|$)|[.!?]+(?=[A-Z])" which is not documented but appears functional.
- The word_metrics paragraph detection (blank-line separated) is not documented in architecture/measure.md but is implemented at measure.py:175-189.
- Both the example output discrepancies appear to be documentation errors rather than implementation errors.
