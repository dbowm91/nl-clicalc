# MCP Server

nl-clicalc includes an MCP (Model Context Protocol) server that exposes text analysis and math evaluation tools to AI agents. This enables AI agents to perform deterministic text inspection and calculations via a standardized protocol.

## What is MCP?

The Model Context Protocol is a JSON-RPC 2.0 based protocol for exposing tools to AI agents. The calc MCP server provides:

- **10 text and math tools** for AI agent workflows
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

**Example:**
```json
{"name": "math_eval", "arguments": {"expression": "five plus three"}}
// Returns: {"ok": true, "result": 8}
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
// Returns metrics including: bytes_utf8, codepoints, words, lines, etc.
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
- `max_diffs` (integer, optional): Maximum diff spans to return (default 50)

**Returns:**
- `equal`: Boolean
- `classification`: Why they differ (confusable_characters, insertion, deletion, etc.)
- `summary`: Human-readable summary
- `diffs`: Array of DiffInfo with:
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

### validate_brackets

Check bracket balance and return details on unmatched brackets.

**Arguments:**
- `text` (string): Text containing brackets to validate

**Returns:**
- `balanced`: Boolean
- `unmatched_openers`: Array of BracketError (char, index, line, column)
- `unmatched_closers`: Array of BracketError

**Default bracket pairs:** `()` `[]` `{}` `<>`

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
//   "valid_pattern": true,
//   "results": [
//     {"sample": "123-4567", "matches": true, "groups": ["123", "4567"], ...},
//     {"sample": "hello", "matches": false, ...}
//   ]
// }}
```

---

### list_compare

Compare two lists with various comparison options.

**Arguments:**
- `a` (array): First list
- `b` (array): Second list
- `ignore_order` (boolean, optional): Compare as sets (default false)
- `casefold` (boolean, optional): Case-insensitive string comparison (default false)
- `normalization` (string, optional): Unicode normalization for strings

**Returns:**
- `same_ordered`: Items in same position in both lists
- `same_unordered`: Items present in both (when ignore_order=true)
- `only_in_a`: Items only in first list
- `only_in_b`: Items only in second list
- `duplicates`: Items appearing more than once
- `near_matches`: Items that differ slightly (Levenshtein distance < 3)

**Example:**
```json
{"name": "list_compare", "arguments": {"a": ["apple", "banana"], "b": ["APPLE", "cherry"], "ignore_order": true}}
// Returns: {"ok": true, "result": {
//   "same_ordered": [],
//   "same_unordered": ["apple"],
//   "only_in_a": ["banana"],
//   "only_in_b": ["cherry"],
//   ...
// }}
```

---

## Error Responses

When a tool call fails, the response includes an error envelope:

```json
{"ok": false, "error_type": "validation_error", "error": "Invalid JSON", "hints": ["Check for trailing commas"]}
```

**Error types:**
- `validation_error`: Input validation failed
- `timeout_error`: Calculation timed out
- `parse_error`: Could not parse input
- `internal_error`: Unexpected error in the tool

---

## Input Limits

The MCP server enforces these limits to prevent DoS:
- `MAX_TEXT_LENGTH`: 100,000 characters per text argument
- `MAX_LIST_ITEMS`: 10,000 items per list argument
- `MAX_REGEX_SAMPLES`: 100 samples per regex test

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
result = client.math_eval("5 + 3")  # {"ok": true, "result": 8}
inspection = client.text_inspect("p\xe2ypal")  # Confusable detection
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

---

## See Also

- [Exact Module](exact.md) - Underlying text processing functions
- [Security](security.md) - Security best practices
- [CLI](cli.md) - Command-line text tools (`calc inspect`, `calc count`, `calc regex`)