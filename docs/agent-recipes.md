# Agent Recipes

Suggested workflows for common tasks using MCP tools.

## String Comparison

### Check whether two strings are truly identical

Use `text_equal` for a thorough comparison including Unicode normalization options.

```json
{"name": "text_equal", "arguments": {"a": "café", "b": "cafe\u0301"}}
```

If `equal` is `false`, use `text_diff_explain` to understand why:

```json
{"name": "text_diff_explain", "arguments": {"a": "pаypal", "b": "paypal"}}
```

This reveals confusable characters (Cyrillic 'а' vs Latin 'a').

---

## Unicode Safety

### Detect hidden Unicode before storing user-provided names

Use `text_inspect` to check for invisible characters, confusables, and mixed scripts.

```json
{"name": "text_inspect", "arguments": {"text": "user\u200Bname"}}
```

Returns warnings for:
- Zero-width space (U+200B)
- Zero-width joiner (U+200D)
- Word joiner (U+2060)
- Bidirectional control characters (LRE, RLE, LRO, RLO, PDF, LRM, RLM, ALM)
- Confusable characters that look like Latin letters
- Mixed scripts that may indicate spoofing

---

## JSON Handling

### Validate generated JSON

Use `validate_json` to check if JSON is well-formed.

```json
{"name": "validate_json", "arguments": {"text": "{\"name\": \"test\", \"value\": 42}"}}
```

Returns `valid: true` and `top_level_keys` on success.

### Extract specific paths from JSON

Use `json_extract` with RFC 6901 JSON Pointer to navigate to specific values.

```json
{"name": "json_extract", "arguments": {"text": "{\"config\": {\"debug\": true}}", "pointer": "/config/debug"}}
```

Pointer syntax:
- `/foo/bar` - Navigate to key
- `/arr/0` - Navigate to array index
- `/~1/f~0` - Escape `~1`→`/`, `~0`→`~`

### Compare two generated JSON configs

Use `json_compare` to check semantic equivalence (ignoring key order).

```json
{"name": "json_compare", "arguments": {"a": "{\"x\": 1, \"y\": 2}", "b": "{\"y\": 2, \"x\": 1}"}}
```

Options:
- `ignore_object_order`: Sort keys before comparison (default true)
- `ignore_array_order`: Sort arrays if comparable (default false)
- `numeric_string_equivalence`: Treat "1" and 1 as equal (default false)

---

## TOML Validation

### Validate Cargo.toml or pyproject.toml

Use `validate_toml` for TOML configuration files.

```json
{"name": "validate_toml", "arguments": {"text": "[package]\nname = \"mycrate\"\nversion = \"0.1.0\""}}
```

Returns structured error info on failure:
- `error`: Error message
- `line`, `column`: Error location
- `type`: Error type (e.g., "syntax")

---

## Text Position Conversion

### Convert editor offsets for LSP integration

Use `text_position` to convert between byte offsets, codepoint indices, and line/column.

```json
{"name": "text_position", "arguments": {"text": "let x = 1;\nconst y = 2;", "byte_offset": 12}}
```

Returns:
- `line`, `column`: Position in the text
- `codepoint_index`: Python string index
- `utf16_offset`: For LSP/editor integration
- `char`, `codepoint`, `name`: Character at position

Multiple locator modes supported:
- `byte_offset`: UTF-8 byte offset
- `codepoint_index`: Python string index
- `line` + `column`: Line/column position
- `utf16_offset`: UTF-16 code units

---

## Text Escaping

### Safely quote text for shell/JSON/regex

Use `escape_text` to properly encode text for various formats.

```json
{"name": "escape_text", "arguments": {"text": "hello\nworld", "mode": "json_string"}}
```

Available modes:
- `json_string` - JSON string literal
- `python_string` - Python string literal
- `rust_string` - Rust string literal
- `posix_shell_single` - POSIX shell single quotes
- `regex_literal` - Regex metacharacter escaping
- `markdown_inline_code` - Inline code span
- `markdown_code_block` - Code block
- `html_text` - HTML text content
- `url_component` - URL percent-encoding

---

## Text Identity Verification

### Verify large generated text without loading it again

Use `text_hash` to compute cryptographic hashes for identity checking.

```json
{"name": "text_hash", "arguments": {"text": "large content here...", "algorithms": ["sha256"]}}
```

Returns `hashes` object with hex digests for each algorithm.

Available algorithms: `sha256`, `sha1`, `md5`, `crc32`

Note: `md5` includes a warning that it's non-cryptographic.

---

## Text Transformation

### Normalize text for comparison or storage

Use `text_transform` to apply deterministic transformations.

```json
{"name": "text_transform", "arguments": {"text": "hello  ", "operations": ["trim_trailing_whitespace"]}}
```

Available operations:
- `normalize_nfc` / `normalize_nfd` / `normalize_nfkc` / `normalize_nfkd` - Unicode normalization
- `casefold` - Case-insensitive comparison preparation
- `trim` - Remove leading/trailing whitespace
- `trim_trailing_whitespace` - Remove trailing only
- `normalize_newlines_lf` - Convert to LF
- `ensure_final_newline` / `strip_final_newline` - Newline management
- `remove_zero_width` - Strip zero-width characters
- `remove_bidi_controls` - Strip bidirectional marks
- `visible_repr` - Show invisibles as escape sequences

---

## Path Analysis

### Analyze paths without filesystem access

Use `path_analyze` for lexical path analysis.

```json
{"name": "path_analyze", "arguments": {"path": "../src/lib.rs"}}
```

Returns:
- `name`, `stem`, `suffix`: Path components
- `hidden`: Boolean (starts with `.`)
- `has_traversal`: Boolean (contains `..`)
- `normalized_lexical`: Cleaned path
- `warnings`: Issues detected

---

## Identifier Validation

### Check naming conventions across languages

Use `identifier_analyze` to validate and classify identifiers.

```json
{"name": "identifier_analyze", "arguments": {"text": "my_function_name", "languages": ["python", "rust"]}}
```

Returns:
- `classification`: snake_case, camelCase, PascalCase, kebab-case, SCREAMING_SNAKE_CASE, mixed, invalid
- `python_valid`, `rust_valid`: Language-specific validity
- `transforms`: Suggested alternative formats

---

## Schema Validation

### Validate JSON against a simple schema

Use `validate_schema_light` for lightweight schema validation.

```json
{"name": "validate_schema_light", "arguments": {"text": "{\"name\": \"test\", \"version\": \"1.0.0\"}", "schema": {"type": "object", "required": ["name", "version"], "properties": {"name": {"type": "string"}, "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"}}}}
```

Supports:
- `type`: object, array, string, number, integer, boolean, null
- `required`: Required property names
- `properties`: Property definitions
- `additional_properties`: Boolean to disallow extra properties
- `enum`: Allowed string values
- `min_length`, `max_length`: String length constraints
- `pattern`: Regex pattern for strings

---

## Quick Reference

| Task | Tool | Key Arguments |
|------|------|---------------|
| Compare strings | `text_equal` | `a`, `b`, `normalization` |
| Explain diff | `text_diff_explain` | `a`, `b`, `max_diffs` |
| Inspect hidden chars | `text_inspect` | `text` |
| Validate JSON | `validate_json` | `text` |
| Extract JSON path | `json_extract` | `text`, `pointer` |
| Compare JSON | `json_compare` | `a`, `b` |
| Validate TOML | `validate_toml` | `text` |
| Convert offsets | `text_position` | `text`, one of: `byte_offset`, `codepoint_index`, `line`+`column`, `utf16_offset` |
| Escape text | `escape_text` | `text`, `mode` |
| Compute hash | `text_hash` | `text`, `algorithms` |
| Transform text | `text_transform` | `text`, `operations` |
| Analyze path | `path_analyze` | `path` |
| Classify name | `identifier_analyze` | `text` |
| Validate schema | `validate_schema_light` | `text`, `schema` |