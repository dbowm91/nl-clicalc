SPEC
````markdown
# nl-clicalc MCP Exact Tools Spec

## Goal

Extend `nl-clicalc` from a calculator/unit-conversion tool into a deterministic exact-reasoning utility for agents.

The system should provide low-level primitives for exact text, Unicode, structure, and measurement tasks, then expose higher-level synthesis functions through an MCP server.

Primary use case: prevent LLM agents from wasting tokens/compute on tasks that should be solved by deterministic code.

---

## Architectural Model

Use three layers:

```text
nl_clicalc/
  exact/
    primitives.py     # smallest deterministic operations
    unicode_tools.py  # Unicode/codepoint/confusable helpers
    measure.py        # text metrics
    diff.py           # low-level diff/span logic
    validate.py       # JSON/TOML/bracket/regex checks

  synthesis/
    explain_diff.py   # calls primitives + classifies result
    inspect_text.py   # combines measure + unicode findings
    sanity.py         # common agent checks

  mcp/
    server.py         # MCP adapter only
    schemas.py        # tool input/output schemas
````

Core rule:

> Primitives must be simple, deterministic, independently testable, and should not call LLMs or perform semantic interpretation.

---

## Design Principles

1. **Deterministic over clever**

   * Prefer exact byte/codepoint/span answers.
   * Do not infer user intent unless in the synthesis layer.

2. **Structured first**

   * Return dictionaries/JSON-compatible objects.
   * Human-readable text is secondary.

3. **Evidence with every verdict**

   * Never return only `true` or `false`.
   * Include position, codepoint, normalized form, or metric evidence.

4. **No mutable global state**

   * MCP calls should be stateless.
   * Existing calculator memory/variables should not be enabled by default in MCP mode.

5. **Safe by default**

   * No arbitrary eval.
   * No filesystem access unless explicitly added later.
   * Bounded input sizes.

6. **Small primitive, composed synthesis**

   * `count_codepoints()` should not know about security.
   * `inspect_text()` may combine Unicode categories, invisibles, mixed-script detection, and normalization state.

---

## Initial MCP Tool Set

### Tier 1 tools

Implement first:

```text
calculate
measure_text
text_equal
explain_diff
inspect_text
count_chars
```

### Tier 2 tools

Implement after Tier 1 is stable:

```text
check_brackets
validate_json
regex_test
list_compare
normalize_text
```

### Tier 3 tools

Optional later:

```text
semver_compare
url_inspect
path_compare
duration_parse
date_math
```

---

# Layer 1: Primitives

## Primitive: `utf8_bytes`

```python
def utf8_bytes(s: str) -> bytes:
    ...
```

Return raw UTF-8 bytes.

Used by:

* byte equality
* byte length
* byte-level diff

---

## Primitive: `codepoints`

```python
def codepoints(s: str) -> list[dict]:
    ...
```

Return:

```json
[
  {
    "index": 0,
    "char": "A",
    "codepoint": "U+0041",
    "name": "LATIN CAPITAL LETTER A",
    "category": "Lu"
  }
]
```

Use `unicodedata.name(char, "<unknown>")`.

---

## Primitive: `normalize_unicode`

```python
def normalize_unicode(s: str, form: str) -> str:
    ...
```

Allowed forms:

```text
NFC
NFD
NFKC
NFKD
```

Reject unknown forms.

---

## Primitive: `casefold_text`

```python
def casefold_text(s: str) -> str:
    ...
```

Use Python `str.casefold()`.

---

## Primitive: `raw_equal`

```python
def raw_equal(a: str, b: str) -> bool:
    return a == b
```

---

## Primitive: `normalized_equal`

```python
def normalized_equal(a: str, b: str, form: str = "NFC") -> bool:
    ...
```

---

## Primitive: `measure_basic`

```python
def measure_basic(s: str) -> dict:
    ...
```

Return:

```json
{
  "bytes_utf8": 0,
  "codepoints": 0,
  "graphemes_estimate": null,
  "chars_no_whitespace": 0,
  "ascii": 0,
  "non_ascii": 0
}
```

Note: without external dependencies, exact grapheme cluster counting is hard. Either:

* return `null`, or
* label clearly as `graphemes_estimate`.

Do not pretend codepoints are graphemes.

---

## Primitive: `count_char`

```python
def count_char(s: str, target: str) -> dict:
    ...
```

Return:

```json
{
  "target": "r",
  "count": 3,
  "positions": [2, 3, 8]
}
```

Positions are Python string/codepoint indexes.

---

## Primitive: `find_invisibles`

```python
def find_invisibles(s: str) -> list[dict]:
    ...
```

Detect:

* zero-width space
* zero-width joiner
* zero-width non-joiner
* BOM
* word joiner
* soft hyphen
* variation selectors
* bidi controls
* control chars except `\n`, `\t`, `\r` unless requested

Return:

```json
[
  {
    "index": 4,
    "char": "\u200b",
    "codepoint": "U+200B",
    "name": "ZERO WIDTH SPACE",
    "category": "Cf",
    "display": "⟦ZWSP⟧"
  }
]
```

---

## Primitive: `visible_repr`

```python
def visible_repr(s: str) -> str:
    ...
```

Map invisible or ambiguous chars to display-safe markers.

Suggested mappings:

```text
SPACE                  -> ␠
TAB                    -> ␉
NEWLINE                -> ␊
CARRIAGE RETURN        -> ␍
NO-BREAK SPACE         -> ⟦NBSP⟧
ZERO WIDTH SPACE       -> ⟦ZWSP⟧
ZERO WIDTH JOINER      -> ⟦ZWJ⟧
ZERO WIDTH NON-JOINER  -> ⟦ZWNJ⟧
BOM                    -> ⟦BOM⟧
SOFT HYPHEN            -> ⟦SHY⟧
RLO/LRO/etc.           -> ⟦BIDI:NAME⟧
COMBINING MARK         -> ◌ + mark
```

---

## Primitive: `line_metrics`

```python
def line_metrics(s: str) -> dict:
    ...
```

Return:

```json
{
  "lines": 0,
  "nonempty_lines": 0,
  "blank_lines": 0,
  "max_line_length_codepoints": 0,
  "trailing_whitespace_lines": [],
  "newline_style": "LF|CRLF|CR|mixed|none",
  "ends_with_newline": true
}
```

Line numbers should be 1-based.

---

## Primitive: `word_metrics`

```python
def word_metrics(s: str) -> dict:
    ...
```

Return:

```json
{
  "words": 0,
  "unique_words_casefolded": 0,
  "sentences_estimate": 0,
  "paragraphs": 0,
  "average_word_length": 0.0
}
```

Keep sentence count labeled as estimate.

---

## Primitive: `first_diff`

```python
def first_diff(a: str, b: str) -> dict | None:
    ...
```

Return:

```json
{
  "a_index": 3,
  "b_index": 3,
  "a_char": "e",
  "b_char": "é",
  "a_codepoint": "U+0065",
  "b_codepoint": "U+00E9"
}
```

Return `None` if equal.

---

## Primitive: `common_prefix_suffix`

```python
def common_prefix_suffix(a: str, b: str) -> dict:
    ...
```

Return:

```json
{
  "common_prefix_len": 3,
  "common_suffix_len": 5
}
```

Avoid overlapping prefix/suffix.

---

## Primitive: `levenshtein_distance`

```python
def levenshtein_distance(a: str, b: str, max_len: int = 10000) -> int:
    ...
```

Bound input size. Use dynamic programming with memory optimization.

Optional:

* `damerau_levenshtein_distance`

---

## Primitive: `diff_spans`

```python
def diff_spans(a: str, b: str) -> list[dict]:
    ...
```

Use `difflib.SequenceMatcher` initially.

Return spans:

```json
[
  {
    "kind": "replace|insert|delete",
    "a_span": [3, 5],
    "b_span": [3, 4],
    "a_text": "é",
    "b_text": "é"
  }
]
```

---

## Primitive: `unicode_script`

```python
def unicode_script(char: str) -> str:
    ...
```

Initial implementation can be heuristic:

* Latin
* Cyrillic
* Greek
* Han
* Hiragana
* Katakana
* Arabic
* Hebrew
* Devanagari
* Common
* Inherited
* Other

Python stdlib does not expose Unicode Script directly. Use codepoint ranges initially.

---

## Primitive: `detect_mixed_scripts`

```python
def detect_mixed_scripts(s: str) -> dict:
    ...
```

Return:

```json
{
  "mixed_scripts": true,
  "scripts": ["Latin", "Cyrillic"],
  "positions": [
    {
      "index": 0,
      "char": "А",
      "script": "Cyrillic",
      "codepoint": "U+0410"
    }
  ]
}
```

Ignore `Common` and `Inherited` for mixed-script verdict.

---

## Primitive: `detect_confusables`

```python
def detect_confusables(s: str) -> list[dict]:
    ...
```

Initial minimal table is acceptable.

Start with common Latin/Cyrillic/Greek homoglyphs:

```text
Latin A  vs Cyrillic А U+0410
Latin a  vs Cyrillic а U+0430
Latin e  vs Cyrillic е U+0435
Latin o  vs Cyrillic о U+043E
Latin p  vs Cyrillic р U+0440
Latin c  vs Cyrillic с U+0441
Latin x  vs Cyrillic х U+0445
Latin y  vs Cyrillic у U+0443
Latin B  vs Greek Β / Cyrillic В
Latin H  vs Cyrillic Н
Latin K  vs Cyrillic К
Latin M  vs Cyrillic М
Latin O  vs Cyrillic О / Greek Ο
Latin P  vs Cyrillic Р / Greek Ρ
Latin T  vs Cyrillic Т
```

Return:

```json
[
  {
    "index": 0,
    "char": "А",
    "codepoint": "U+0410",
    "name": "CYRILLIC CAPITAL LETTER A",
    "confusable_with": "A",
    "confusable_name": "LATIN CAPITAL LETTER A"
  }
]
```

Later option: import Unicode Consortium confusables data at build time.

---

## Primitive: `check_brackets`

```python
def check_brackets(s: str, pairs: dict[str, str] | None = None) -> dict:
    ...
```

Default pairs:

```text
() [] {} <>
```

Should track:

* unmatched openers
* unmatched closers
* positions
* line/column
* context

Return:

```json
{
  "balanced": false,
  "unmatched_openers": [
    {
      "char": "{",
      "index": 10,
      "line": 1,
      "column": 11
    }
  ],
  "unmatched_closers": []
}
```

Do not try to fully parse programming languages. This is structural sanity only.

---

## Primitive: `validate_json`

```python
def validate_json(s: str) -> dict:
    ...
```

Return:

```json
{
  "valid": false,
  "error": "Expecting ',' delimiter",
  "line": 3,
  "column": 12,
  "position": 44
}
```

If valid:

```json
{
  "valid": true,
  "type": "object",
  "top_level_keys": ["name", "version"]
}
```

---

## Primitive: `regex_test`

```python
def regex_test(pattern: str, samples: list[str], flags: list[str] | None = None) -> dict:
    ...
```

Support Python `re`.

Return:

```json
{
  "valid_pattern": true,
  "results": [
    {
      "sample": "foo",
      "matches": true,
      "fullmatch": true,
      "span": [0, 3],
      "groups": [],
      "groupdict": {}
    }
  ]
}
```

---

# Layer 2: Synthesis Functions

## Synthesis: `measure_text`

Calls:

* `measure_basic`
* `line_metrics`
* `word_metrics`
* `find_invisibles`
* `detect_mixed_scripts`
* normalization checks

Input:

```json
{
  "text": "string",
  "include_codepoints": false
}
```

Output:

```json
{
  "bytes_utf8": 128,
  "codepoints": 121,
  "graphemes": null,
  "words": 57,
  "unique_words_casefolded": 42,
  "lines": 12,
  "nonempty_lines": 9,
  "blank_lines": 3,
  "max_line_length_codepoints": 88,
  "chars_no_whitespace": 104,
  "ascii": 117,
  "non_ascii": 4,
  "letters": 82,
  "digits": 6,
  "punctuation": 12,
  "symbols": 1,
  "spaces": 18,
  "control_chars": 0,
  "combining_marks": 1,
  "invisible_chars": 1,
  "newline_style": "LF",
  "ends_with_newline": true,
  "normalization": {
    "is_nfc": true,
    "is_nfd": false,
    "is_nfkc": true,
    "is_nfkd": false
  },
  "unicode_risks": {
    "contains_invisibles": true,
    "contains_bidi_controls": false,
    "mixed_scripts": false,
    "scripts": ["Latin"]
  }
}
```

---

## Synthesis: `text_equal`

Input:

```json
{
  "a": "string",
  "b": "string",
  "normalization": "raw|NFC|NFD|NFKC|NFKD",
  "casefold": false,
  "trim": false
}
```

Output:

```json
{
  "equal": false,
  "mode": {
    "normalization": "raw",
    "casefold": false,
    "trim": false
  },
  "raw_equal": false,
  "nfc_equal": true,
  "nfkc_equal": true,
  "casefold_equal": true,
  "byte_equal": false,
  "lengths": {
    "a_codepoints": 5,
    "b_codepoints": 4,
    "a_bytes_utf8": 6,
    "b_bytes_utf8": 5
  },
  "first_difference": {
    "a_index": 3,
    "b_index": 3,
    "a_visible": "e◌́",
    "b_visible": "é"
  },
  "classification": "unicode_normalization_only"
}
```

---

## Synthesis: `explain_diff`

Input:

```json
{
  "a": "string",
  "b": "string",
  "max_diffs": 20,
  "include_codepoints": true,
  "include_context": true
}
```

Output:

```json
{
  "equal": false,
  "classification": "unicode_normalization_only",
  "summary": {
    "raw_equal": false,
    "byte_equal": false,
    "nfc_equal": true,
    "nfkc_equal": true,
    "casefold_equal": true,
    "same_length_codepoints": false,
    "edit_distance": 1,
    "common_prefix_len": 3,
    "common_suffix_len": 0
  },
  "a_metrics": {
    "bytes_utf8": 6,
    "codepoints": 5
  },
  "b_metrics": {
    "bytes_utf8": 5,
    "codepoints": 4
  },
  "diffs": [
    {
      "kind": "normalization_equivalent",
      "a_span": [3, 5],
      "b_span": [3, 4],
      "a_text": "é",
      "b_text": "é",
      "a_visible": "e◌́",
      "b_visible": "é",
      "a_codepoints": [
        {
          "char": "e",
          "codepoint": "U+0065",
          "name": "LATIN SMALL LETTER E"
        },
        {
          "char": "́",
          "codepoint": "U+0301",
          "name": "COMBINING ACUTE ACCENT"
        }
      ],
      "b_codepoints": [
        {
          "char": "é",
          "codepoint": "U+00E9",
          "name": "LATIN SMALL LETTER E WITH ACUTE"
        }
      ],
      "note": "Different raw codepoints, equal after NFC normalization."
    }
  ],
  "security_findings": [],
  "agent_instruction": "Treat these strings as equivalent only if NFC normalization is acceptable. They are not byte-identical."
}
```

### Classification values

Use one of:

```text
exact_match
case_only
unicode_normalization_only
compatibility_normalization_only
whitespace_only
line_ending_only
invisible_character
confusable_character
punctuation_variant
accent_or_diacritic_difference
numeric_difference
ordinary_text_difference
length_only
prefix_suffix_difference
multiple_difference_types
```

---

## Synthesis: `inspect_text`

Input:

```json
{
  "text": "string",
  "include_codepoints": true,
  "include_confusables": true
}
```

Output:

```json
{
  "safe_repr": "user⟦ZWSP⟧name",
  "metrics": {},
  "normalization": {
    "is_nfc": true,
    "is_nfkc": true
  },
  "invisibles": [
    {
      "index": 4,
      "char": "\u200b",
      "codepoint": "U+200B",
      "name": "ZERO WIDTH SPACE",
      "display": "⟦ZWSP⟧"
    }
  ],
  "scripts": {
    "mixed_scripts": false,
    "scripts": ["Latin"]
  },
  "confusables": [],
  "warnings": [
    {
      "severity": "warning",
      "kind": "invisible_character",
      "message": "Text contains ZERO WIDTH SPACE at index 4."
    }
  ]
}
```

---

## Synthesis: `count_chars`

Input:

```json
{
  "text": "strawberry",
  "target": "r",
  "normalization": "raw|NFC|NFKC"
}
```

Output:

```json
{
  "target": "r",
  "normalization": "raw",
  "count": 3,
  "positions": [2, 3, 8],
  "text_length_codepoints": 10
}
```

If no target provided, return frequency table.

---

## Synthesis: `list_compare`

Input:

```json
{
  "a": ["src/foo.rs", "README.md"],
  "b": ["src/foo.rs", "readme.md"],
  "ignore_order": true,
  "casefold": false,
  "normalization": "NFC"
}
```

Output:

```json
{
  "same_ordered": false,
  "same_unordered": false,
  "only_in_a": ["README.md"],
  "only_in_b": ["readme.md"],
  "duplicates_a": [],
  "duplicates_b": [],
  "near_matches": [
    {
      "a": "README.md",
      "b": "readme.md",
      "classification": "case_only"
    }
  ]
}
```

---

# Layer 3: MCP Adapter

The MCP adapter should be thin.

It should:

* validate tool inputs
* call synthesis functions
* return JSON-compatible outputs
* not contain core logic
* not read/write files
* not mutate calculator globals

Recommended package layout:

```text
nl_clicalc/mcp/
  server.py
  schemas.py
  tools.py
```

Possible implementation targets:

* Python MCP SDK if already acceptable
* stdio MCP server
* optional HTTP/SSE later

---

## MCP Tool Names

Expose:

```text
nl_calculate
nl_measure_text
nl_text_equal
nl_explain_diff
nl_inspect_text
nl_count_chars
nl_check_brackets
nl_validate_json
nl_regex_test
nl_list_compare
```

Prefixing with `nl_` avoids collisions in larger harnesses.

---

## MCP Tool Descriptions

### `nl_calculate`

> Deterministically evaluate arithmetic, unit conversions, constants, and simple scientific expressions. Use for math and unit tasks instead of asking the model to calculate.

### `nl_measure_text`

> Measure exact text properties: UTF-8 byte length, codepoint count, words, lines, whitespace, newline style, Unicode normalization state, invisibles, and mixed-script signals.

### `nl_text_equal`

> Compare two strings under raw, Unicode-normalized, casefolded, or trimmed modes and report exact equality evidence.

### `nl_explain_diff`

> Explain why two strings differ, including spans, codepoints, Unicode names, normalization equivalence, confusables, invisibles, and agent-facing classification.

### `nl_inspect_text`

> Inspect a string for hidden characters, Unicode confusables, mixed scripts, normalization state, and display-safe representation.

### `nl_count_chars`

> Count exact characters or produce a character frequency table with codepoint positions.

### `nl_check_brackets`

> Check whether delimiters are structurally balanced and report unmatched delimiters with line/column positions.

### `nl_validate_json`

> Validate JSON and report precise parse errors or top-level structure information.

### `nl_regex_test`

> Test a Python regular expression against sample strings and report match/fullmatch status, spans, groups, and errors.

### `nl_list_compare`

> Compare two lists exactly, optionally ignoring order, casefolding, or Unicode-normalizing elements. Report missing, duplicate, and near-match items.

---

# Input Limits

Set defaults:

```text
MAX_TEXT_LENGTH = 100_000
MAX_LIST_ITEMS = 10_000
MAX_REGEX_SAMPLES = 100
MAX_DIFF_LENGTH = 20_000
MAX_DIFF_SPANS = 50
```

Behavior:

* refuse or truncate with explicit warning
* never silently truncate
* expose limit errors in structured form

Example:

```json
{
  "ok": false,
  "error_type": "InputTooLarge",
  "error": "Input length 250000 exceeds MAX_TEXT_LENGTH 100000."
}
```

---

# Error Shape

All MCP tools should return a consistent envelope.

Success:

```json
{
  "ok": true,
  "result": {}
}
```

Failure:

```json
{
  "ok": false,
  "error_type": "ValidationError",
  "error": "Unsupported normalization form: XYZ",
  "hints": ["Use one of: raw, NFC, NFD, NFKC, NFKD"]
}
```

---

# Testing Requirements

## Unit tests for primitives

Required cases:

### Equality

```text
"elephant" vs "elephant" -> raw equal
"elephant" vs "eIephant" -> not equal, ordinary/confusable depending chars
"café" vs "cafe\u0301" -> raw false, NFC true
"A" vs "А" -> raw false, confusable
```

### Invisible characters

```text
"user\u200bname" -> detects ZWSP
"hello\u00a0world" -> detects NBSP
"abc\u202Edef" -> detects bidi control
```

### Counting

```text
"strawberry", "r" -> 3 at [2,3,8]
"banana", "a" -> 3
"aaaa", "aa" -> reject target length > 1 unless substring mode exists
```

### Metrics

```text
"hello\nworld\n" -> 2 lines or 3 split lines? Define behavior explicitly.
```

Recommended behavior:

* `lines` means logical lines as humans expect.
* `"hello\nworld\n"` has `lines = 2`, `ends_with_newline = true`.

### Brackets

```text
"(a[b]{c})" -> balanced
"(a]" -> mismatch
"foo(bar" -> unmatched opener
"foo)bar" -> unmatched closer
```

### JSON

```text
{"x": 1} -> valid
{"x": 1,} -> invalid with line/column
```

### Regex

```text
pattern "^[a-z]+$"
samples ["foo", "Foo", "foo123"]
```

---

# Agent Prompting Guidance

When injecting tool results into an LLM context, prefer compact textual summaries over giant JSON unless the agent framework handles tool JSON natively.

Example injected result:

```text
EXACT_DIFF_RESULT
classification: unicode_normalization_only
raw_equal: false
nfc_equal: true
byte_equal: false
edit_distance: 1

first_difference:
- a[3:5]: "e◌́" = U+0065 LATIN SMALL LETTER E + U+0301 COMBINING ACUTE ACCENT
- b[3:4]: "é"  = U+00E9 LATIN SMALL LETTER E WITH ACUTE

agent_instruction: Treat as equivalent only if NFC normalization is acceptable. Not byte-identical.
```

---

# Recommended Implementation Order

## Phase 1

Implement primitive core:

```text
codepoints
visible_repr
measure_basic
line_metrics
find_invisibles
normalize_unicode
raw_equal
normalized_equal
count_char
first_diff
common_prefix_suffix
```

## Phase 2

Implement synthesis:

```text
measure_text
text_equal
inspect_text
explain_diff
count_chars
```

## Phase 3

Add structural tools:

```text
check_brackets
validate_json
regex_test
list_compare
```

## Phase 4

Add MCP adapter:

```text
stdio MCP server
tool schemas
consistent error envelope
manual smoke tests from Claude/Codex/codegg
```

## Phase 5

Hardening:

```text
fuzz tests
Unicode edge cases
large input limits
snapshot tests for exact JSON outputs
security review
```

---

# Non-Goals

Do not implement initially:

```text
semantic equivalence
natural-language meaning comparison
LLM-based typo correction
file scanning
filesystem mutation
network access
large document diffing
full language parsing
full Unicode grapheme segmentation unless adding dependency
complete UTS #39 confusable implementation unless imported cleanly
```

---

# Success Criteria

The MCP server is successful if an agent can reliably answer:

```text
Are these two strings exactly the same?
If not, why not?
How many times does this character occur?
Are there hidden Unicode characters?
Are there confusable lookalike characters?
How many words/chars/lines are in this text?
Is this JSON valid?
Are these brackets balanced?
Does this regex match these samples?
Are these two lists equivalent?
What is the result of this unit/math expression?
```

without doing probabilistic reasoning itself.

```
```

