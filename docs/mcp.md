# MCP Server

nl-clicalc includes an MCP (Model Context Protocol) server that exposes text analysis and math evaluation tools to AI agents. This enables AI agents to perform deterministic text inspection and calculations via a standardized protocol.

## What is MCP?

The Model Context Protocol is a JSON-RPC 2.0 based protocol for exposing tools to AI agents. The calc MCP server provides:

- **39 deterministic tools** for AI agent workflows
- **Deterministic results** - same input always produces same output
- **No external dependencies** - pure Python standard library
- **stdio-based communication** - operates over stdin/stdout

## Running the Server

Start the MCP server with the `--mcp` flag:

```bash
calc --mcp
```

The server reads JSON-RPC requests from stdin and writes responses to stdout. It runs until EOF is received.

## Protocol Basics

The server uses JSON-RPC 2.0 over stdio:

```bash
# List available tools
{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}

# Call a tool
{"jsonrpc": "2.0", "id": 2, "method": "tools/call",
 "params": {"name": "math_eval", "arguments": {"expression": "5 + 3"}}}
```

## Available Tools

### math_eval

Evaluate mathematical expressions with full natural language and unit support.

**Arguments:**
- `expression` (string): The math expression to evaluate

**Tier:** 1
**Tags:** `math`, `evaluation`, `units`

**Example:**
```json
{"name": "math_eval", "arguments": {"expression": "five plus three"}}
// Returns: {"ok": true, "result": {"result": "8", "type": "int"}}
```

**Supported expressions:**
- Arithmetic: `5 + 3`, `2 ** 10`, `100 % 7`
- Natural language: `five plus three`, `twenty times five`
- Units: `30m + 100ft`, `5km in miles`
- Constants: `pi`, `avogadro`, `speed of light`
- Functions: `sqrt(144)`, `sin(pi/2)`, `factorial(5)`

---

### text_measure

Return comprehensive text metrics.

**Arguments:**
- `text` (string): The text to measure

**Tier:** 1
**Tags:** `text`, `metrics`, `unicode`

**Returns:**
- `bytes_utf8`: Raw UTF-8 byte count
- `codepoints`: Number of Unicode codepoints
- `chars_no_whitespace`: Characters excluding whitespace
- `ascii`: Count of ASCII characters
- `non_ascii`: Count of non-ASCII characters
- `words`: Word count
- `lines`: Line count (including empty)
- `nonempty_lines`: Lines with content
- `blank_lines`: Empty lines
- `newline_style`: LF, CRLF, CR, mixed, or none
- `ends_with_newline`: Boolean
- `letters`, `digits`, `punctuation`, `symbols`, `spaces`, `control_chars`
- `is_nfc`, `is_nfd`, `is_nfkc`, `is_nfkd`: Normalization state

**Example:**
```json
{"name": "text_measure", "arguments": {"text": "Hello, 世界!\n"}}
// Returns: {"ok": true, "result": {"bytes_utf8": 17, "codepoints": 13, "words": 2, ...}}
```

---

### text_equal

Compare two strings under various normalization modes with detailed evidence.

**Arguments:**
- `a` (string): First string
- `b` (string): Second string
- `normalization` (string, optional): "raw", "NFC", "NFD", "NFKC", "NFKD"
- `casefold` (boolean, optional): Case-insensitive comparison
- `trim` (boolean, optional): Trim whitespace

**Tier:** 1
**Tags:** `text`, `comparison`, `unicode`, `normalization`

**Returns:**
- `equal`: Boolean result
- `mode`: Comparison mode used
- `raw_equal`: Byte-for-byte equality
- `nfc_equal`, `nfd_equal`, `nfkc_equal`, `nfkd_equal`: Per-normalization equality
- `casefold_equal`: After casefolding
- `byte_equal`: After trimming
- `lengths`: Codepoint lengths of both strings
- `first_difference`: Details of first differing character (if any)
- `classification`: "identical", "normalized_equivalent", "casefold_equivalent", "trimmed_equivalent", "confusable_characters", "completely_different"

**Example:**
```json
{"name": "text_equal", "arguments": {"a": "café", "b": "cafe\u0301", "normalization": "NFC"}}
// Returns: {"ok": true, "result": {"equal": true, "mode": "NFC", ...}}
```

---

### text_diff_explain

Explain differences between two strings with detailed codepoint information.

**Arguments:**
- `a` (string): First string
- `b` (string): Second string
- `max_diffs` (integer, optional): Maximum diff spans to return (default 20)
- `include_codepoints` (boolean, optional): Include codepoint details (default true)
- `include_context` (boolean, optional): Include context notes (default true)

**Tier:** 2
**Tags:** `text`, `diff`, `unicode`, `comparison`

**Returns:**
- `equal`: Boolean
- `classification`: Why they differ (confusable_characters, insertion, deletion, etc.)
- `summary`: Human-readable summary
- `spans`: Array of DiffSpan with:
  - `kind`: "equal", "insert", "delete", "replace"
  - `a_text`, `b_text`: The text spans
  - `a_codepoints`, `b_codepoints`: Codepoint details
  - `note`: Explanation (e.g., "CYRILLIC SMALL LETTER A looks like LATIN SMALL LETTER A")
- `security_findings`: Array of security warnings
- `agent_instruction`: Instructions for AI agent handling

**Example:**
```json
{"name": "text_diff_explain", "arguments": {"a": "pаypal", "b": "paypal"}}
// Returns diff with security finding about Cyrillic confusable
```

---

### text_inspect

Complete text inspection for hidden characters, confusables, and Unicode risks.

**Arguments:**
- `text` (string): The text to inspect
- `include_codepoints` (boolean, optional): Include codepoint details (default true)
- `include_confusables` (boolean, optional): Check for confusables (default true)

**Tier:** 1
**Tags:** `text`, `unicode`, `security`, `inspection`

**Returns:**
- `safe_repr`: Display-safe representation (invisibles shown as markers)
- `metrics`: Full text metrics (same as text_measure)
- `normalization`: Normalization state
- `invisibles`: Array of InvisibleCharInfo with index, char, codepoint, name, category, display
- `scripts`: Script analysis for each character
- `confusables`: Array of ConfusableInfo with confusable character details
- `warnings`: Human-readable warnings

**Example:**
```json
{"name": "text_inspect", "arguments": {"text": "user\u200Bname"}}
// Returns inspection showing zero-width space at index 4
```

**Security warnings include:**
- "Text contains invisible character ZERO WIDTH SPACE at index N"
- "Character at index N is confusable (SCRIPT vs SCRIPT)"
- "Text contains bidirectional control characters"

---

### text_count

Count character occurrences or return frequency table.

**Arguments:**
- `text` (string): The text to analyze
- `target` (string, optional): Specific character to count (if omitted, returns frequency table)
- `normalization` (string, optional): Normalization to apply before counting

**Tier:** 1
**Tags:** `text`, `count`, `frequency`

**Returns:**
- `target`: Character being counted (or null for frequency table)
- `normalization`: Normalization mode used
- `count`: Number of occurrences (when target specified)
- `positions`: Array of codepoint indices where target appears
- `text_length_codepoints`: Total codepoint count
- Frequency table when no target specified: `{"h": 1, "e": 1, "l": 2, ...}`

**Example:**
```json
{"name": "text_count", "arguments": {"text": "hello world", "target": "l"}}
// Returns: {"ok": true, "result": {"count": 3, "positions": [2, 3, 9], ...}}
```

---

### text_truncate

Truncate a string to a specified number of grapheme clusters (user-perceived characters).

**Arguments:**
- `text` (string): Input string to truncate
- `max_graphemes` (integer): Maximum number of grapheme clusters to return

**Tier:** 1
**Tags:** `text`, `truncation`, `unicode`

**Returns:**
- `text`: Result string (truncated if truncation occurred)
- `original_graphemes`: Original grapheme count
- `truncated_graphemes`: Grapheme count in result
- `truncated`: Boolean indicating if text was truncated

**Example:**
```json
{"name": "text_truncate", "arguments": {"text": "Hello, world!", "max_graphemes": 5}}
// Returns: {"ok": true, "result": {"text": "Hello", "original_graphemes": 13, "truncated_graphemes": 5, "truncated": true}}
```

---

### text_window

Get a window around a position in text with context lines. Shows the line at the given position with surrounding context, position metrics, and character details.

**Arguments:**
- `text` (string): Input string to analyze
- `position` (object): Position specification with kind and value
  - `kind` (string): "byte_offset", "codepoint_index", "grapheme_index", or "line_column"
  - `value` (integer): Value for byte_offset, codepoint_index, or grapheme_index
  - `line` (integer): Line number for line_column kind
  - `column` (integer): Column number for line_column kind
- `context_lines` (integer, optional): Number of context lines before and after (default: 2)
- `include_visible_repr` (boolean, optional): Include visible representation of the line (default: true)

**Tier:** 1
**Tags:** `text`, `position`, `context`, `unicode`, `window`

**Returns:**
- `position`: Object with byte_offset, codepoint_index, grapheme_index, line, column
- `line_text`: Text of the line at the position
- `line_visible_repr`: Visible representation (with invisible chars marked)
- `before`: Array of {line, text} before the position
- `after`: Array of {line, text} after the position
- `newline_style`: LF, CRLF, CR, mixed, or none
- `at_codepoint`: Object with char, codepoint, name, category
- `warnings`: Any warnings (e.g., position in middle of multibyte)

**Example:**
```json
{"name": "text_window", "arguments": {"text": "line1\nline2\nline3", "position": {"kind": "line_column", "line": 2, "column": 3}, "context_lines": 1}}
// Returns: {"ok": true, "result": {"position": {"byte_offset": 8, "codepoint_index": 8, "grapheme_index": 7, "line": 2, "column": 3}, "line_text": "line2", ...}}
```

---

### validate_brackets

Check bracket balance and return details on unmatched brackets.

**Arguments:**
- `text` (string): Text containing brackets to validate
- `pairs` (object, optional): Bracket pair mapping (default: `() [] {} <>`)

**Tier:** 1
**Tags:** `validation`, `brackets`, `structure`

**Returns:**
- `balanced`: Boolean
- `unmatched_openers`: Array of BracketError (char, index, line, column)
- `unmatched_closers`: Array of BracketError

**Example:**
```json
{"name": "validate_brackets", "arguments": {"text": "(a + b) * [c - d]"}}
// Returns: {"ok": true, "result": {"balanced": true, "unmatched_openers": [], "unmatched_closers": []}}

{"name": "validate_brackets", "arguments": {"text": "(a + b]"}}
// Returns: {"ok": true, "result": {"balanced": false, "unmatched_openers": [...], "unmatched_closers": [...]}}
```

---

### validate_json

Validate JSON and report detailed parse errors.

**Arguments:**
- `text` (string): JSON string to validate

**Tier:** 1
**Tags:** `validation`, `json`, `structured-data`

**Returns:**
- `valid`: Boolean
- `error`: Error message (if invalid)
- `line`, `column`, `position`: Error location (if invalid)
- `type`: Error type (e.g., "syntax", "structure")
- `top_level_keys`: Array of top-level object/array keys (if valid)

**Example:**
```json
{"name": "validate_json", "arguments": {"text": "{\"name\": \"test\"}"}}
// Returns: {"ok": true, "result": {"valid": true, "top_level_keys": ["name"]}}

{"name": "validate_json", "arguments": {"text": "{\"name\":}"}}
// Returns: {"ok": true, "result": {"valid": false, "error": "Expecting property name...", "line": 1, "column": 9}}
```

---

### validate_regex

Test regex patterns against sample strings.

**Arguments:**
- `pattern` (string): Regex pattern
- `samples` (array of strings): Strings to test against
- `flags` (array of strings, optional): Flag names (IGNORECASE, MULTILINE, etc.)

**Tier:** 1
**Tags:** `validation`, `regex`, `pattern`

**Returns:**
- `valid_pattern`: Boolean
- `results`: Array of RegexMatch for each sample:
  - `sample`: The input string
  - `matches`: Boolean (any match)
  - `fullmatch`: Boolean (entire string matches)
  - `span`: Tuple of (start, end) positions
  - `groups`: Array of capture groups
  - `groupdict`: Dict of named capture groups

**Example:**
```json
{"name": "validate_regex", "arguments": {"pattern": "(\\d+)-(\\d+)", "samples": ["123-4567", "hello"]}}
// Returns: {"ok": true, "result": {
  "valid_pattern": true,
  "results": [
    {"sample": "123-4567", "matches": true, "groups": ["123", "4567"], ...},
    {"sample": "hello", "matches": false, ...}
  ]
}}
```

---

### list_compare

Compare two lists with various comparison options.

**Arguments:**
- `a` (array): First list
- `b` (array): Second list
- `ignore_order` (boolean, optional): Compare as sets (default true)
- `casefold` (boolean, optional): Case-insensitive string comparison (default false)
- `normalization` (string, optional): Unicode normalization for strings (default "NFC")

**Tier:** 2
**Tags:** `comparison`, `lists`, `sets`

**Returns:**
- `equal`: Boolean indicating if lists are equal under given mode
- `missing_in_b`: Items in `a` not found in `b`
- `missing_in_a`: Items in `b` not found in `a`
- `duplicates_in_a`: Items appearing more than once in `a`
- `duplicates_in_b`: Items appearing more than once in `b`
- `near_matches`: Items that differ slightly (Levenshtein distance < 3)

**Example:**
```json
{"name": "list_compare", "arguments": {"a": ["apple", "banana"], "b": ["APPLE", "cherry"], "ignore_order": true}}
// Returns: {"ok": true, "result": {
  "equal": false,
  "missing_in_b": ["banana"],
  "missing_in_a": ["cherry"],
  "duplicates_in_a": [],
  "duplicates_in_b": [],
  ...
}}
```

---

### validate_toml

Validate TOML configuration files (Cargo.toml, pyproject.toml, etc.) and report parse errors with line/column positions.

**Arguments:**
- `text` (string): TOML document string to validate
- `detail` (string, optional): "summary" | "normal" | "full" (default "normal")

**Tier:** 2
**Tags:** `validation`, `structured-data`, `toml`, `config`, `rust`, `python`

**Returns:**
- `valid`: Boolean
- `error`: Error message (if invalid)
- `line`, `column`: Error location (if invalid)
- `position`: Character position (if available)
- `type`: Error type (e.g., "syntax")
- `top_level_keys`: Array of top-level keys (if valid)
- `tables`: Array of table names (if valid)
- `summary`: Human-readable summary

**Example:**
```json
{"name": "validate_toml", "arguments": {"text": "[package]\nname = \"demo\"\nversion = \"0.1.0\""}}
// Returns: {"ok": true, "result": {"valid": true, "top_level_keys": ["package"], "tables": ["package"], "summary": "Valid TOML with 1 top-level key and 1 table"}}

{"name": "validate_toml", "arguments": {"text": "[package]\nname = \"demo\"\nversion"}}
// Returns: {"ok": true, "result": {"valid": false, "error": "Expected '=' after a key in a key/value pair", "line": 3, "column": 8}}
```

**Limits:** Input limited to 100,000 characters. Parse failures return `valid: false` in result, not server errors.

---

### json_extract

Extract a value from JSON using RFC 6901 JSON Pointer (e.g., `/foo/bar/0`). Navigate nested objects and arrays.

**Arguments:**
- `text` (string): JSON document string
- `pointer` (string, optional): RFC 6901 JSON Pointer path (default empty = whole document)
- `detail` (string, optional): "summary" | "normal" | "full" (default "normal")
- `max_output_chars` (integer, optional): Maximum output characters (default 4000)

**Tier:** 2
**Tags:** `json`, `structured-data`, `extraction`, `config`, `pointer`

**Returns:**
- `valid_json`: Boolean
- `found`: Boolean
- `pointer`: The pointer that was used
- `value_type`: Type of extracted value (string, number, object, array, boolean, null)
- `value`: The extracted value (truncated if necessary)
- `preview`: String preview of the value
- `child_keys`: Array of keys (for objects)
- `array_length`: Length (for arrays)
- `truncated`: Boolean
- `summary`: Human-readable summary

**Example:**
```json
{"name": "json_extract", "arguments": {"text": "{\"dependencies\": {\"tokio\": {\"version\": \"1.36\"}}}", "pointer": "/dependencies/tokio"}}
// Returns: {"ok": true, "result": {"valid_json": true, "found": true, "value_type": "object", "child_keys": ["version"], ...}}
```

**Pointer Syntax:**
- `/foo/bar` - Navigate to `foo` then `bar`
- `/arr/0` - Navigate to index 0 of array
- `/~1/f~0` - Escape `~1` → `/`, `~0` → `~` (RFC 6901)

**Limits:** Output truncated at `max_output_chars`. Parse failures return `valid_json: false`, not server errors.

---

### json_canonicalize

Canonicalize JSON with deterministic formatting, key ordering, duplicate key detection, and stable hashes.

**Arguments:**
- `text` (string): Input JSON string to canonicalize
- `sort_keys` (boolean, optional): Sort object keys alphabetically (default true)
- `indent` (integer, optional): Indentation spaces (None for minified)
- `ensure_ascii` (boolean, optional): Use ASCII escaping for non-ASCII characters (default false)
- `detect_duplicate_keys` (boolean, optional): Report duplicate keys in the input (default true)
- `trailing_newline` (boolean, optional): Add a trailing newline to the canonical form (default false)

**Tier:** 1
**Tags:** `json`, `canonical`, `hash`, `deterministic`, `format`

**Returns:**
- `valid`: Boolean
- `canonical`: Canonical JSON string
- `minified`: Minified JSON string (compact, no whitespace)
- `sha256`: SHA-256 hash of the canonical form
- `duplicate_keys`: Array of keys that appear more than once (top-level only)
- `top_level_type`: "object", "array", or primitive type name
- `top_level_keys`: Array of top-level object keys (if object)
- `error`: Error message if invalid
- `line`, `column`: Error location if invalid

**Example:**
```json
{"name": "json_canonicalize", "arguments": {"text": "{\"b\": 2, \"a\": 1}", "sort_keys": true}}
// Returns: {"ok": true, "result": {"valid": true, "canonical": "{\"a\": 1, \"b\": 2}\n", "minified": "{\"a\":1,\"b\":2}", "sha256": "...", "duplicate_keys": [], "top_level_type": "object", "top_level_keys": ["b", "a"]}}
```

---

### json_query

Extract a value from JSON using RFC 6901 JSON Pointer. Navigate nested objects and arrays.

**Arguments:**
- `text` (string): JSON document string
- `pointer` (string, optional): RFC 6901 JSON Pointer path (e.g., "/foo/bar/0"). Empty string means the whole document.

**Tier:** 1
**Tags:** `json`, `pointer`, `extraction`, `query`, `rfc6901`

**Returns:**
- `found`: Boolean
- `pointer`: The pointer that was used
- `value`: The value at the pointer (if found)
- `type`: Type of the value: "object", "array", "string", "number", "boolean", "null"
- `missing_at`: The path where lookup failed (if not found)
- `reason`: "key_not_found", "index_out_of_range", "invalid_pointer_syntax", "invalid_json"
- `error`: Error message if invalid JSON

**Example:**
```json
{"name": "json_query", "arguments": {"text": "{\"foo\": \"bar\"}", "pointer": "/foo"}}
// Returns: {"ok": true, "result": {"found": true, "pointer": "/foo", "value": "bar", "type": "string", ...}}
```

---

### json_compare

Compare two JSON documents semantically, ignoring formatting and key order.

**Arguments:**
- `a` (string): First JSON document
- `b` (string): Second JSON document
- `ignore_object_order` (boolean, optional): Sort object keys for comparison (default true)
- `ignore_array_order` (boolean, optional): Sort arrays if all items are serializable (default false)
- `numeric_string_equivalence` (boolean, optional): Treat numeric strings as numbers (default false)
- `casefold_keys` (boolean, optional): Casefold object keys before comparison (default false)
- `treat_missing_null_as_equal` (boolean, optional): Treat missing and null as equal (default false)
- `max_diffs` (integer, optional): Maximum number of differences to report (default 50)
- `detail` (string, optional): "summary" | "normal" | "full" (default "normal")

**Tier:** 2
**Tags:** `json`, `structured-data`, `comparison`, `config`

**Returns:**
- `valid_json_a`: Boolean
- `valid_json_b`: Boolean
- `equal`: Boolean
- `same_type`: Boolean (both valid JSON)
- `diff_count`: Number of differences found
- `diffs`: Array of diff objects:
  - `path`: JSON Pointer path to difference
  - `kind`: "type_changed", "value_changed", "key_missing_in_a", "key_missing_in_b", "array_length_changed", "array_item_changed"
  - `a_type`, `b_type`: Types of values at path
  - `a_preview`, `b_preview`: String previews of values
- `truncated`: Boolean
- `summary`: Human-readable summary

**Example:**
```json
{"name": "json_compare", "arguments": {"a": "{\"x\": 1, \"y\": 2}", "b": "{\"y\": 2, \"x\": 1}"}}
// Returns: {"ok": true, "result": {"valid_json_a": true, "valid_json_b": true, "equal": true, "diff_count": 0, ...}}
```

**Limits:** Diff output limited to `max_diffs` entries. Parse failures return `valid_json_a: false` or `valid_json_b: false`, not server errors.

---

### text_position

Convert between byte offsets, codepoint indices, line/column positions, and UTF-16 offsets. Useful for LSP/editor integrations.

**Arguments:**
- `text` (string): Input string
- `byte_offset` (integer, optional): UTF-8 byte offset (0-based)
- `codepoint_index` (integer, optional): Python string index (Unicode scalar index)
- `line` (integer, optional): 1-based line number (with line_base)
- `column` (integer, optional): 1-based column number (with column_base)
- `utf16_offset` (integer, optional): UTF-16 code unit offset for LSP-style positions
- `line_base` (integer, optional): Base for line numbers (1 for 1-based, 0 for 0-based, default 1)
- `column_base` (integer, optional): Base for column numbers (1 for 1-based, 0 for 0-based, default 1)
- `detail` (string, optional): "summary" | "normal" | "full" (default "normal")

**Tier:** 2
**Tags:** `text`, `position`, `offset`, `unicode`, `lsp`

**Returns:**
- `valid`: Boolean
- `byte_offset`: UTF-8 byte offset
- `codepoint_index`: Unicode scalar index
- `utf16_offset`: UTF-16 code unit offset
- `line`: Line number (1-based)
- `column`: Column number (1-based)
- `line_base`, `column_base`: Bases used
- `char`: Character at position
- `codepoint`: Unicode codepoint (e.g., "U+0078")
- `name`: Unicode name of character
- `line_text_preview`: Content of the line
- `summary`: Human-readable summary
- `error`: Error message (if invalid)
- `warnings`: Array of warnings (e.g., for CRLF handling)

**Example:**
```json
{"name": "text_position", "arguments": {"text": "let x = 1;\nconst y = 2;", "byte_offset": 12}}
// Returns: {"ok": true, "result": {"valid": true, "byte_offset": 12, "codepoint_index": 10, "line": 2, "column": 4, ...}}
```

**Limits:** Exactly one locator mode must be provided. Input limited to 100,000 characters.

---

### text_transform

Apply deterministic text transformations: Unicode normalization, casefold, trim, newline normalization, zero-width removal, bidi control stripping, and visible representation.

**Arguments:**
- `text` (string): Input string to transform
- `operations` (array of strings): Operations to apply
- `detail` (string, optional): "summary" | "normal" | "full" (default "normal")

**Tier:** 2
**Tags:** `text`, `unicode`, `transform`, `normalization`, `sanitation`

**Available Operations:**
- `normalize_nfc` / `normalize_nfd` / `normalize_nfkc` / `normalize_nfkd`: Unicode normalization
- `casefold`: Case-insensitive comparison preparation
- `trim`: Remove leading/trailing whitespace
- `trim_trailing_whitespace`: Remove trailing whitespace only
- `normalize_newlines_lf`: Convert all newlines to LF
- `ensure_final_newline`: Ensure text ends with newline
- `strip_final_newline`: Remove final newline
- `remove_zero_width`: Remove zero-width characters (U+200B, U+FEFF, etc.)
- `remove_bidi_controls`: Remove bidirectional control characters
- `visible_repr`: Show invisibles as escape sequences

**Returns:**
- `changed`: Boolean indicating if text was modified
- `text`: Transformed text
- `operations_applied`: Array of operations that were applied
- `removed`: Array of removed character info (if any invisibles removed)
- `warnings`: Array of warnings
- `summary`: Human-readable summary

**Example:**
```json
{"name": "text_transform", "arguments": {"text": "hello  ", "operations": ["trim_trailing_whitespace"]}}
// Returns: {"ok": true, "result": {"changed": true, "text": "hello", "operations_applied": ["trim_trailing_whitespace"], ...}}
```

**Limits:** Input limited to 100,000 characters.

---

### escape_text

Escape text for various output formats. Safely quote text for shell, JSON, regex, and other contexts.

**Arguments:**
- `text` (string): Input string to escape
- `mode` (string): Escape mode
- `detail` (string, optional): "summary" | "normal" | "full" (default "normal")

**Tier:** 2
**Tags:** `text`, `escape`, `encoding`, `shell`, `json`, `regex`

**Available Modes:**
- `json_string`: JSON string literal (escapes quotes, backslashes, newlines)
- `python_string`: Python string literal
- `rust_string`: Rust string literal
- `posix_shell_single`: POSIX shell single-quoted string
- `regex_literal`: Regular expression literal
- `markdown_inline_code`: Markdown inline code
- `markdown_code_block`: Markdown code block
- `html_text`: HTML text content
- `url_component`: URL component (percent-encoding)

**Returns:**
- `mode`: The escape mode used
- `escaped`: The escaped text
- `changed`: Boolean indicating if text was modified
- `summary`: Human-readable summary

**Example:**
```json
{"name": "escape_text", "arguments": {"text": "hello\nworld", "mode": "json_string"}}
// Returns: {"ok": true, "result": {"mode": "json_string", "escaped": "\"hello\\nworld\"", "changed": true, "summary": "Escaped text as JSON string literal"}}
```

**Limits:** Input limited to 100,000 characters.

---

### unescape_text

Unescape text from various formats.

**Arguments:**
- `text` (string): Input string to unescape
- `mode` (string): Unescape mode
- `detail` (string, optional): "summary" | "normal" | "full" (default "normal")

**Tier:** 2
**Tags:** `text`, `escape`, `encoding`, `shell`, `json`, `regex`

**Available Modes:**
- `json_string`: JSON string literal
- `python_string`: Python string literal (via ast.literal_eval)
- `unicode_escape`: Unicode escape sequences (\uXXXX, \UXXXXXXXX)
- `url_component`: URL component (decode percent-encoding)

**Returns:**
- `mode`: The unescape mode used
- `unescaped`: The unescaped text
- `changed`: Boolean indicating if text was modified
- `error`: Error message (if unescape failed)
- `summary`: Human-readable summary

**Example:**
```json
{"name": "unescape_text", "arguments": {"text": "\"hello\\nworld\"", "mode": "json_string"}}
// Returns: {"ok": true, "result": {"mode": "json_string", "unescaped": "hello\nworld", "changed": true, ...}}
```

**Limits:** Input limited to 100,000 characters.

---

### text_hash

Compute cryptographic hashes of text for identity checking. Verify large generated text without loading it again.

**Arguments:**
- `text` (string): Input string to hash
- `algorithms` (array of strings, optional): Hash algorithms (sha256, sha1, md5, crc32) (default ["sha256"])
- `encoding` (string, optional): Text encoding for byte conversion (default "utf-8")
- `detail` (string, optional): "summary" | "normal" | "full" (default "normal")

**Tier:** 2
**Tags:** `text`, `hash`, `identity`, `security`

**Returns:**
- `encoding`: The encoding used
- `bytes`: Number of UTF-8 bytes
- `codepoints`: Number of Unicode codepoints
- `hashes`: Object mapping algorithm names to hex digests
- `warnings`: Array of warnings (e.g., for md5)
- `summary`: Human-readable summary

**Example:**
```json
{"name": "text_hash", "arguments": {"text": "hello world", "algorithms": ["sha256", "md5"]}}
// Returns: {"ok": true, "result": {"encoding": "utf-8", "bytes": 11, "codepoints": 11, "hashes": {"sha256": "...", "md5": "..."}, ...}}
```

**Limits:** Input limited to 100,000 characters.

---

### path_analyze

Analyze path components, extensions, hidden status, and traversal without filesystem access. Lexical analysis only.

**Arguments:**
- `path` (string): Path string to analyze
- `style` (string, optional): "auto" | "posix" | "windows" (default "auto")
- `detail` (string, optional): "summary" | "normal" | "full" (default "normal")

**Tier:** 2
**Tags:** `text`, `path`, `filesystem`, `lexical`

**Returns:**
- `input`: Original input path
- `style`: Detected or specified style (posix/windows)
- `absolute`: Boolean indicating if path is absolute
- `has_traversal`: Boolean indicating if path contains `..` segments
- `components`: Array of path components
- `parent`: Parent directory
- `name`: Filename
- `stem`: Filename without extension
- `suffix`: File extension (single)
- `suffixes`: All extensions (for `.tar.gz`)
- `hidden`: Boolean indicating if file/dir starts with `.`
- `normalized_lexical`: Lexically normalized path
- `warnings`: Array of warnings (e.g., traversal, unicode issues)
- `summary`: Human-readable summary

**Example:**
```json
{"name": "path_analyze", "arguments": {"path": "../src/lib.rs"}}
// Returns: {"ok": true, "result": {"input": "../src/lib.rs", "style": "posix", "absolute": false, "has_traversal": true, "name": "lib.rs", "stem": "lib", "suffix": ".rs", ...}}
```

**Limits:** Input limited to 100,000 characters. No filesystem access.

---

### identifier_analyze

Classify and validate identifier naming conventions across languages. Help avoid naming drift.

**Arguments:**
- `text` (string): Identifier to analyze
- `languages` (array of strings, optional): Languages to check (python, rust, javascript, env) (default all)
- `detail` (string, optional): "summary" | "normal" | "full" (default "normal")

**Tier:** 3
**Tags:** `text`, `identifier`, `naming`, `validation`, `language`

**Returns:**
- `text`: Original identifier
- `classification`: Primary classification (snake_case, camelCase, PascalCase, kebab-case, SCREAMING_SNAKE_CASE, mixed, invalid)
- `python_valid`: Boolean for Python identifier
- `python_keyword`: Boolean if Python keyword
- `rust_valid`: Boolean for Rust identifier
- `rust_keyword`: Boolean if Rust keyword
- `javascript_valid`: Boolean for JavaScript identifier
- `env_valid`: Boolean for environment variable name
- `transforms`: Suggested transformations:
  - `snake_case`, `kebab_case`, `pascal_case`, `screaming_snake_case`
- `warnings`: Array of warnings
- `summary`: Human-readable summary

**Example:**
```json
{"name": "identifier_analyze", "arguments": {"text": "my_function_name"}}
// Returns: {"ok": true, "result": {"text": "my_function_name", "classification": "snake_case", "python_valid": true, "python_keyword": false, "env_valid": true, ...}}
```

**Limits:** Input limited to 100,000 characters.

---

### validate_schema_light

Validate JSON against a simple schema format with type, required, enum, pattern, and nested constraints. Does NOT implement full JSON Schema.

**Arguments:**
- `text` (string): JSON document string to validate
- `schema` (object): Schema to validate against
- `detail` (string, optional): "summary" | "normal" | "full" (default "normal")

**Tier:** 3
**Tags:** `validation`, `json`, `schema`, `structured-data`

**Supported Schema Features:**
- `type`: "object", "array", "string", "number", "integer", "boolean", "null"
- `required`: Array of required property names
- `properties`: Object with property definitions
- `additional_properties`: Boolean to disallow extra properties
- `enum`: Array of allowed string values
- `min_length`, `max_length`: String length constraints
- `min_items`, `max_items`: Array length constraints
- `items`: Schema for array items
- `pattern`: Regex pattern for strings

**Returns:**
- `valid`: Boolean
- `errors`: Array of validation errors:
  - `path`: JSON Pointer path to violation
  - `message`: Human-readable error message
  - `type`: Error type
- `summary`: Human-readable summary

**Example:**
```json
{"name": "validate_schema_light", "arguments": {"text": "{\"name\": \"test\", \"version\": \"1.0.0\"}", "schema": {"type": "object", "required": ["name", "version"], "properties": {"name": {"type": "string"}, "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"}}}}
// Returns: {"ok": true, "result": {"valid": true, "errors": [], "summary": "Valid against schema"}}
```

**Limits:** Input limited to 100,000 characters.

---

## Error Responses

When a tool call fails, the response includes an error envelope:

```json
{"ok": false, "error_type": "invalid_arguments", "error": "Invalid normalization form", "hints": ["Use NFC or NFD"]}
```

**Error types:**
- `invalid_arguments`: Input validation failed (wrong type, out of range, etc.)
- `input_too_large`: Input exceeds size limits
- `unsupported_option`: Unknown or unsupported option value
- `parse_error`: Could not parse input (invalid JSON, regex, etc.)
- `evaluation_error`: Math expression evaluation failed
- `timeout`: Operation timed out
- `internal_error`: Unexpected error in the tool

---

## Input Limits

The MCP server enforces these limits to prevent DoS:
- `MAX_TEXT_LENGTH`: 100,000 characters per text argument
- `MAX_LIST_ITEMS`: 10,000 items per list argument
- `MAX_REGEX_SAMPLES`: 100 samples per regex test
- `MAX_EXPRESSION_LENGTH`: 10,000 characters for math expressions

---

## Tool Tiers

Tools are categorized into three tiers:

**Tier 1:** Core tools, always available, low-context overhead.
- `math_eval`, `text_measure`, `text_equal`, `text_inspect`, `text_count`, `text_truncate`, `validate_brackets`, `validate_json`, `validate_regex`

**Tier 2:** Useful coding-agent tools, deterministic, moderate context.
- `json_compare`, `json_extract`, `validate_toml`, `text_position`, `text_transform`, `escape_text`, `unescape_text`, `text_hash`, `path_analyze`, `list_compare`

**Tier 3:** Specialized tools, more context, opt-in for context-constrained agents.
- `identifier_analyze`, `validate_schema_light`

---

## AI Agent Integration Example

Here's how an AI agent would use the MCP server:

```python
import subprocess
import json

class CalcMCPClient:
    def __init__(self):
        self.process = subprocess.Popen(
            ["calc", "--mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self._next_id = 1

    def _send_request(self, method, params=None):
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id,
            "method": method,
            "params": params or {}
        }
        self._next_id += 1

        self.process.stdin.write(json.dumps(request).encode())
        self.process.stdin.write(b"\n")
        self.process.stdin.flush()

        response = json.loads(self.process.stdout.readline())
        return response.get("result")

    def list_tools(self):
        return self._send_request("tools/list")

    def call_tool(self, name, arguments):
        return self._send_request("tools/call", {"name": name, "arguments": arguments})

    def math_eval(self, expression):
        return self.call_tool("math_eval", {"expression": expression})

    def text_inspect(self, text):
        return self.call_tool("text_inspect", {"text": text})

# Usage
client = CalcMCPClient()
result = client.math_eval("5 + 3")  # {"ok": true, "result": {"result": "8", "type": "int"}}
inspection = client.text_inspect("p\u0430ypal")  # Confusable detection
```

---

### glob_match

Match a glob pattern against a path with explicit semantics.

**Arguments:**
- `pattern` (string): Glob pattern (e.g., "src/**/*.rs")
- `path` (string): Path to match
- `platform` (string, optional): "posix" or "windows"
- `case_sensitive` (boolean, optional): Default true

**Tier:** 1
**Tags:** `text`, `glob`, `pattern`, `path`, `wildcard`

**Glob Semantics:**
- `*` matches any characters within one path segment (not crossing `/`)
- `**` matches zero or more full path segments
- `?` matches exactly one character within a segment

**Example:**
```json
{"name": "glob_match", "arguments": {"pattern": "src/**/*.rs", "path": "src/main.rs"}}
// Returns: {"ok": true, "result": {"matches": true, "normalized_pattern": "src/**/*.rs", ...}}
```

---

### text_fingerprint

Compute a deterministic SHA-256 fingerprint of text with canonicalization options.

**Arguments:**
- `text` (string): Input string to fingerprint
- `unicode` (string, optional): "raw", "NFC", "NFD", "NFKC", "NFKD"
- `newline` (string, optional): "raw" or "LF"
- `trim_final_newline` (boolean, optional): Remove trailing newline
- `casefold` (boolean, optional): Apply casefolding before hashing

**Tier:** 1
**Tags:** `text`, `hash`, `fingerprint`, `sha256`, `identity`, `canonicalization`

**Example:**
```json
{"name": "text_fingerprint", "arguments": {"text": "hello\n", "trim_final_newline": true, "unicode": "NFC"}}
// Returns: {"ok": true, "result": {"sha256": "...", "bytes_utf8": 5, "codepoints": 5, ...}}
```

---

### identifier_inspect

Inspect identifiers for validity and collisions. Detects confusables, mixed scripts, normalization issues, and casefold collisions.

**Arguments:**
- `identifiers` (array): List of identifier strings to inspect
- `language` (string, optional): "generic", "python", "rust", "javascript", "typescript", "json_key"
- `normalization` (string, optional): "NFC", "NFD", etc.
- `casefold` (boolean, optional): Check for casefold collisions
- `check_confusables` (boolean, optional): Default true

**Tier:** 1
**Tags:** `text`, `identifier`, `collision`, `confusable`, `security`, `validation`

**Example:**
```json
{"name": "identifier_inspect", "arguments": {"identifiers": ["paypal", "pаypal"], "language": "python"}}
// Returns: {"ok": true, "result": {"identifiers": [{"raw": "paypal", "scripts": ["Latin"], ...}, ...], "collisions": [...]}}
```

---

### path_normalize

Normalize and analyze a path with explicit platform semantics.

**Arguments:**
- `path` (string): Path to normalize
- `platform` (string, optional): "posix" or "windows" (default "posix")
- `collapse_dot_segments` (boolean, optional): Remove . and .. segments (default true)
- `preserve_trailing_separator` (boolean, optional): Keep trailing slash (default false)

**Tier:** 1
**Tags:** `text`, `path`, `normalization`, `platform`

**Returns:**
- `normalized`: Normalized path string
- `is_absolute`: Boolean
- `components`: Array of path segments
- `warnings`: Array of warnings

**Example:**
```json
{"name": "path_normalize", "arguments": {"path": "src/../src/main.rs", "collapse_dot_segments": true}}
// Returns: {"ok": true, "result": {"normalized": "src/main.rs", "is_absolute": false, ...}}
```

---

### version_compare

Compare two version strings with explicit scheme.

**Arguments:**
- `a` (string): First version
- `b` (string): Second version
- `scheme` (string, optional): "semver", "pep440", or "loose" (default "semver")

**Tier:** 3
**Tags:** `text`, `version`, `semver`, `comparison`

**Returns:**
- `comparison`: -1, 0, or 1
- `valid`: Boolean
- `scheme`: The scheme used

**Example:**
```json
{"name": "version_compare", "arguments": {"a": "1.2.3", "b": "1.2.10", "scheme": "semver"}}
// Returns: {"ok": true, "result": {"comparison": -1, "valid": true, "scheme": "semver"}}
```

---

### toml_shape

Analyze the structure of a TOML document.

**Arguments:**
- `text` (string): TOML document
- `max_depth` (integer, optional): Maximum nesting depth (default 4)
- `max_tables` (integer, optional): Maximum tables to report (default 50)

**Tier:** 3
**Tags:** `text`, `toml`, `structured-data`, `shape`

**Returns:**
- `valid`: Boolean
- `top_level_keys`: Array of top-level key names
- `tables`: Array of table info (name, depth, key_count)
- `truncated`: Boolean

**Example:**
```json
{"name": "toml_shape", "arguments": {"text": "[package]\nname = \"foo\"\n[dependencies]\n"}}
// Returns: {"ok": true, "result": {"valid": true, "top_level_keys": ["package", "dependencies"], ...}}
```

---

### list_dedupe

Remove duplicates from a list with optional normalization and casefolding.

**Arguments:**
- `items` (array): List of strings to deduplicate
- `normalization` (string, optional): "NFC", "NFD", "NFKC", "NFKD", or "raw" (default "raw")
- `casefold` (boolean, optional): Case-insensitive deduplication (default false)
- `preserve_order` (boolean, optional): Keep first occurrence order (default true)

**Tier:** 3
**Tags:** `text`, `list`, `deduplication`, `normalization`

**Returns:**
- `items`: Deduplicated list
- `count_original`: Original count
- `count_dedupe`: After deduplication
- `removed`: Array of removed items (if preserve_order is false)

**Example:**
```json
{"name": "list_dedupe", "arguments": {"items": ["a", "A", "b", "a"], "casefold": true}}
// Returns: {"ok": true, "result": {"items": ["a", "b"], "count_original": 4, "count_dedupe": 2}}
```

---

### list_sort

Sort a list of strings with optional normalization and casefolding.

**Arguments:**
- `items` (array): List of strings to sort
- `normalization` (string, optional): "NFC", "NFD", "NFKC", "NFKD", or "raw" (default "raw")
- `casefold` (boolean, optional): Case-insensitive sorting (default false)
- `reverse` (boolean, optional): Descending order (default false)
- `stable` (boolean, optional): Preserve relative order of equal elements (default true)

**Tier:** 3
**Tags:** `text`, `list`, `sorting`, `normalization`

**Returns:**
- `items`: Sorted list
- `count`: Number of items

**Example:**
```json
{"name": "list_sort", "arguments": {"items": ["b", "A", "c"], "casefold": true}}
// Returns: {"ok": true, "result": {"items": ["A", "b", "c"], "count": 3}}
```

---

## Security Considerations

The MCP server is designed for AI agent use with these security properties:

1. **No arbitrary code execution** - math_eval uses AST parsing, not eval()
2. **Input limits enforced** - Prevents DoS via large inputs
3. **Deterministic results** - Same input produces same output
4. **No external network calls** - Pure computation, no side effects
5. **Text inspection tools** - Help detect Unicode-based spoofing attacks

**For untrusted input handling:**
- Use `text_inspect` to check for hidden characters and confusables before storing user text
- Use `validate_json` to safely parse user-provided JSON
- Use `validate_brackets` to check expression syntax before evaluation
- Use `escape_text` to safely embed text in JSON, shell commands, or regex patterns

---

## See Also

- [Exact Module](exact.md) - Underlying text processing functions
- [Security](security.md) - Security best practices
- [CLI](cli.md) - Command-line text tools (`calc inspect`, `calc count`, `calc regex`)
- [Agent Recipes](agent-recipes.md) - Suggested workflows for common tasks