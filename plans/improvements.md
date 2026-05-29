# nl-clicalc / eggsact MCP Deterministic Tools Refinement Plan

## Purpose

This plan converts the nl-clicalc MCP assessment into a concrete implementation handoff. It is intended for a smaller coding model such as MiMo v2.5 to execute in the existing `dbowm91/nl-clicalc` repository and to preserve the design direction for the future Rust `eggsact` crate used by `codegg`.

The project goal is not to turn the MCP server into a semantic coding assistant. The goal is to make it a reliable deterministic oracle for questions that LLM coding agents routinely answer incorrectly: exact string equality, Unicode normalization, invisible characters, confusables, byte/codepoint/grapheme positions, JSON structure, regex spans, path/glob behavior, list deltas, unit conversions, and stable fingerprints.

The desired end state is a stable, schema-driven MCP contract that `codegg` can call frequently without context pollution and without special-case prompt instructions.

## Current State Summary

The repository already has the correct foundation.

The MCP server exposes deterministic tools over stdio using JSON-RPC. The current tool layer is in:

- `nl_calc/mcp/server.py`
- `nl_calc/mcp/tools.py`
- `nl_calc/mcp/schemas.py`
- `docs/mcp.md`

The exact text-analysis foundation is under:

- `nl_calc/exact/primitives.py`
- `nl_calc/exact/unicode_tools.py`
- `nl_calc/exact/measure.py`
- `nl_calc/exact/diff.py`
- `nl_calc/exact/validate.py`
- `nl_calc/exact/synthesis.py`
- `nl_calc/exact/confusables.py`

The current registered MCP tools are:

- `math_eval`
- `text_measure`
- `text_equal`
- `text_diff_explain`
- `text_inspect`
- `text_count`
- `text_truncate`
- `validate_brackets`
- `validate_json`
- `validate_regex`
- `list_compare`

The docs appear to describe “10 text and math tools,” but the server registers 11. `text_truncate` is implemented and schema-listed, but documentation should promote it rather than leave it as drift.

## Non-Goals

Do not add internet/network behavior.

Do not add semantic code review, architecture reasoning, lint interpretation, dependency advisories, or package ecosystem intelligence.

Do not add tools that modify files or produce patches.

Do not add YAML unless the project intentionally accepts an external dependency or a deliberately limited parser. For this repo’s current no-external-dependencies posture, defer YAML.

Do not make tool behavior depend on the host operating system when deterministic cross-platform behavior is needed. Path tools must accept explicit `platform` arguments.

Do not bury normal validation failures as opaque MCP transport failures. Invalid JSON input to `validate_json`, an unmatched bracket result, or a regex compile failure should be normal tool results, not server crashes.

## Design Principles

Keep three layers clean.

The primitive layer should contain pure deterministic functions with no MCP concepts. These functions should be easy to unit-test and later port to Rust.

The synthesis layer should compose primitives into agent-useful operations: `text_window`, `json_shape`, `identifier_inspect`, `text_fingerprint`, and similar.

The MCP adapter layer should do only JSON schema exposure, argument validation, error/result wrapping, and protocol handling.

Prefer exact data over prose. A tool result may include a short human-readable summary, but the primary contract should be structured fields.

Prefer small focused tools over broad “smart” tools. For example, `unit_convert(value, from_unit, to_unit)` is better for agents than relying exclusively on flexible natural-language `math_eval`.

Use deterministic ordering in every list result. Sort stable outputs when natural ordering is not inherent.

Use explicit limits everywhere: input size, list length, regex samples, regex matches, output array size, max context lines, max shape depth.

## Phase 0: Contract Cleanup and Baseline Hardening

### Goal

Make the existing MCP surface internally consistent before adding new tools.

### Tasks

1. Reconcile documentation, schema, and implementation.

   Update `docs/mcp.md` so it lists all currently registered tools, including `text_truncate`.

   Verify that every documented argument default matches the actual implementation and schema.

   In particular, inspect and fix drift around `list_compare`:
   - Documentation currently describes fields such as `same_ordered`, `same_unordered`, `only_in_a`, `only_in_b`, `duplicates`, and `near_matches`.
   - Schema appears to expose fields such as `equal`, `missing_in_b`, `missing_in_a`, `duplicates_in_a`, and `duplicates_in_b`.
   - Implementation defaults `ignore_order=True`; docs should not say otherwise.

   Verify `math_eval` docs reflect the actual return envelope: stringified result and type metadata, unless you choose to change the implementation.

2. Standardize error taxonomy.

   Choose lowercase snake_case error types:
   - `invalid_arguments`
   - `input_too_large`
   - `unsupported_option`
   - `parse_error`
   - `evaluation_error`
   - `timeout`
   - `internal_error`

   Replace mixed forms such as `InputTooLarge`, `ValidationError`, `UnexpectedError`, `EvaluationError`, and `InputError` in MCP tool wrappers.

   Keep old values only if backward compatibility is explicitly required; if kept, document them as deprecated.

3. Decide and document the tool failure model.

   Recommended model:

   - Protocol errors are JSON-RPC errors:
     - malformed JSON-RPC request
     - unknown method
     - unknown tool
     - invalid `params` shape
     - internal server exception

   - Domain/tool failures are normal MCP tool results:
     - invalid JSON text passed to `validate_json`
     - invalid regex pattern passed to `validate_regex`
     - unbalanced brackets
     - unsupported normalization option
     - input too large

   This lets codegg treat deterministic tool outputs as data rather than catching protocol-level exceptions for ordinary negative answers.

4. Add a canonical success/error envelope.

   Recommended success envelope:

   ```json
   {
     "ok": true,
     "result": {},
     "meta": {
       "tool": "text_equal",
       "version": "nl-calc-mcp-1",
       "warnings": []
     }
   }
   ```

   Recommended error envelope:

   ```json
   {
     "ok": false,
     "error_type": "invalid_arguments",
     "message": "normalization must be one of raw, NFC, NFD, NFKC, NFKD",
     "hints": ["Use NFC for canonical equivalence checks"],
     "meta": {
       "tool": "text_equal",
       "version": "nl-calc-mcp-1"
     }
   }
   ```

   Avoid using `error` as the primary field if possible; use `message` for readability. If changing field names is too disruptive, preserve `error` but add `message`.

5. Add golden MCP tool-list tests.

   Create a test that calls `tools/list` and compares:
   - tool names
   - descriptions exist and are non-empty
   - input schemas exist
   - required fields match expected signatures
   - defaults are represented where appropriate

   This test should fail if a tool is registered in `server.py` but missing from `schemas.py`, or vice versa.

6. Add docs example tests.

   At minimum, add unit tests that exercise each example request in `docs/mcp.md` against the implementation. These do not have to assert the full output, but they should assert `ok`, major fields, and absence/presence of expected errors.

7. Add request-size protection at server read layer.

   Existing tool-level limits are useful, but the server should not parse arbitrarily large JSON lines before rejecting input.

   Add a constant such as:

   ```python
   MAX_REQUEST_BYTES = 1_000_000
   ```

   In `server.py`, reject lines exceeding the limit before `json.loads`.

8. Decide batch JSON-RPC behavior.

   Either implement batch requests or reject them clearly.

   Minimal acceptable behavior: if a request is a list, return a JSON-RPC invalid request error with a message such as `Batch requests are not supported`.

### Acceptance Criteria

`pytest` passes.

`tools/list` returns exactly the tools present in `TOOL_HANDLERS`.

`docs/mcp.md` correctly documents all registered tools.

All tool wrappers use the same error taxonomy.

Oversized requests are rejected before JSON parsing.

Unknown tools still return a helpful “Did you mean” message.

Normal validation failures are stable data results unless the project intentionally preserves the previous JSON-RPC-error behavior.

## Phase 1: High-Value Agent Tools

### Goal

Add the deterministic primitives most immediately useful for `codegg`.

### Tool 1: `text_window`

#### Rationale

Coding agents often need to map compiler/linter/parser diagnostics to exact source context. Existing text metrics are useful, but there is no direct tool for “show me the line and surrounding context for this byte/codepoint/line-column position.”

#### Proposed Signature

```json
{
  "text": "string",
  "position": {
    "kind": "byte_offset | codepoint_index | grapheme_index | line_column",
    "value": 123,
    "line": 10,
    "column": 5
  },
  "context_lines": 2,
  "include_visible_repr": true
}
```

For `line_column`, use 1-based line and 1-based column by default. Document this explicitly.

#### Proposed Result

```json
{
  "ok": true,
  "result": {
    "position": {
      "byte_offset": 120,
      "codepoint_index": 118,
      "grapheme_index": 117,
      "line": 10,
      "column": 5
    },
    "line_text": "...",
    "line_visible_repr": "...",
    "before": [
      {"line": 8, "text": "..."},
      {"line": 9, "text": "..."}
    ],
    "after": [
      {"line": 11, "text": "..."},
      {"line": 12, "text": "..."}
    ],
    "newline_style": "LF",
    "at_codepoint": {
      "char": "x",
      "codepoint": "U+0078",
      "name": "LATIN SMALL LETTER X",
      "category": "Ll"
    },
    "warnings": []
  }
}
```

#### Implementation Notes

Add primitive helpers if needed:
- byte offset to codepoint index
- codepoint index to line/column
- line/column to codepoint index
- surrounding line extraction
- grapheme boundary detection or best-effort warning

Do not silently treat bytes, codepoints, and graphemes as interchangeable.

#### Tests

Test ASCII.

Test CRLF.

Test mixed newlines.

Test emoji/ZWJ sequences.

Test combining marks.

Test line/column beyond range.

Test byte offset in middle of a multibyte sequence.

### Tool 2: `json_canonicalize`

#### Rationale

Agents frequently need deterministic JSON formatting, key ordering, duplicate-key detection, and stable hashes.

#### Proposed Signature

```json
{
  "text": "string",
  "sort_keys": true,
  "indent": 2,
  "ensure_ascii": false,
  "detect_duplicate_keys": true,
  "trailing_newline": true
}
```

#### Proposed Result

```json
{
  "valid": true,
  "canonical": "{\n  \"a\": 1\n}\n",
  "minified": "{\"a\":1}",
  "sha256": "...",
  "duplicate_keys": [],
  "top_level_type": "object",
  "top_level_keys": ["a"]
}
```

#### Implementation Notes

Use Python standard library `json`.

Use `object_pairs_hook` to detect duplicate keys.

If duplicate keys exist, decide whether the canonical object uses last-write-wins, first-write-wins, or returns no canonical output. Recommended: use standard JSON semantics for parsed object but report duplicates explicitly.

#### Tests

Valid object.

Valid array.

Invalid JSON.

Duplicate keys.

Unicode characters with `ensure_ascii` true/false.

Stable hash across key order when `sort_keys=true`.

### Tool 3: `json_query`

#### Rationale

Agents should not have to load whole config files into model context to answer “what is at this JSON path?”

#### Proposed Signature

```json
{
  "text": "string",
  "pointer": "/compilerOptions/paths"
}
```

Use RFC 6901-style JSON Pointer, not a custom query language.

#### Proposed Result

```json
{
  "found": true,
  "value": {},
  "type": "object",
  "pointer": "/compilerOptions/paths"
}
```

If not found:

```json
{
  "found": false,
  "missing_at": "/compilerOptions",
  "reason": "object_key_missing"
}
```

#### Tests

Root pointer `""`.

Object key.

Array index.

Escaped `~0` and `~1`.

Missing key.

Index out of range.

Invalid pointer syntax.

### Tool 4: `json_shape`

#### Rationale

Large JSON files can be summarized structurally without semantic interpretation.

#### Proposed Signature

```json
{
  "text": "string",
  "max_depth": 4,
  "max_keys": 100,
  "max_array_items": 5
}
```

#### Proposed Result

```json
{
  "valid": true,
  "shape": {
    "type": "object",
    "keys": {
      "scripts": {"type": "object", "keys": {"test": {"type": "string"}}},
      "dependencies": {"type": "object", "key_count": 12}
    }
  },
  "truncated": false
}
```

#### Tests

Object.

Array.

Mixed-type array.

Deep object truncated by max depth.

Large object truncated by max keys.

### Tool 5: `regex_finditer`

#### Rationale

`validate_regex` currently tests samples, but agents often need exact spans for all matches in a file-like string.

#### Proposed Signature

```json
{
  "pattern": "string",
  "text": "string",
  "flags": ["MULTILINE"],
  "max_matches": 100,
  "include_line_column": true,
  "include_groups": true
}
```

#### Proposed Result

```json
{
  "valid_pattern": true,
  "matches": [
    {
      "match": "abc",
      "span": [0, 3],
      "line": 1,
      "column": 1,
      "groups": [],
      "groupdict": {}
    }
  ],
  "truncated": false
}
```

#### Implementation Notes

Add limits:
- max pattern length
- max text length
- max matches
- max group count if needed

Use existing regex flag parsing if available.

#### Tests

No match.

One match.

Multiple matches.

Named groups.

Multiline mode.

Invalid regex.

Max match truncation.

### Tool 6: `regex_safety_check`

#### Rationale

A deterministic warning tool can catch obvious catastrophic-backtracking risks before agents generate problematic regex patterns.

#### Proposed Signature

```json
{
  "pattern": "string"
}
```

#### Proposed Result

```json
{
  "valid_pattern": true,
  "risk": "low | medium | high",
  "findings": [
    {
      "kind": "nested_quantifier",
      "span": [0, 8],
      "message": "Nested quantifiers may cause catastrophic backtracking"
    }
  ]
}
```

#### Implementation Notes

This is heuristic only. Do not claim formal proof of regex safety.

Flag obvious cases:
- nested quantifiers such as `(a+)+`
- ambiguous dot-star before repeated groups
- repeated alternations with overlapping prefixes
- backreferences if Python regex supports them and they are present

#### Tests

Safe literals.

Simple anchored pattern.

Nested quantifier.

Invalid regex.

Backreference.

### Tool 7: `path_normalize`

#### Rationale

Coding agents often confuse path separators, relative segments, and platform-specific semantics.

#### Proposed Signature

```json
{
  "path": "string",
  "platform": "posix | windows",
  "collapse_dot_segments": true,
  "preserve_trailing_separator": false
}
```

#### Proposed Result

```json
{
  "normalized": "src/main.rs",
  "is_absolute": false,
  "components": ["src", "main.rs"],
  "warnings": []
}
```

#### Implementation Notes

Do not use host OS behavior.

Use `posixpath` for POSIX semantics.

Use `ntpath` for Windows semantics.

Be careful with Windows drive letters and UNC paths.

#### Tests

POSIX relative path.

POSIX absolute path.

Windows drive path.

Windows UNC path.

Mixed separators.

Dot and dot-dot segments.

Trailing separator.

### Tool 8: `glob_match`

#### Rationale

Agents routinely misjudge globs in ignore files, config files, and project file selection.

#### Proposed Signature

```json
{
  "pattern": "src/**/*.rs",
  "path": "src/main.rs",
  "platform": "posix | windows",
  "case_sensitive": true
}
```

#### Proposed Result

```json
{
  "matches": true,
  "normalized_pattern": "src/**/*.rs",
  "normalized_path": "src/main.rs"
}
```

#### Implementation Notes

Use deterministic documented semantics. If using Python `fnmatch`, document its limitations around `**`.

If implementing `**`, define behavior precisely:
- `*` matches within one path segment
- `**` matches zero or more full path segments
- `?` matches one character within a segment

#### Tests

Exact match.

Single star.

Double star.

Path separator handling.

Windows case sensitivity option.

Non-match.

### Tool 9: `text_fingerprint`

#### Rationale

Codegg can use stable fingerprints to verify that text fragments, diagnostics, or tool outputs have not changed between planning and application.

#### Proposed Signature

```json
{
  "text": "string",
  "canonicalization": {
    "unicode": "raw | NFC | NFD | NFKC | NFKD",
    "newline": "raw | LF",
    "trim_final_newline": false,
    "casefold": false
  }
}
```

#### Proposed Result

```json
{
  "sha256": "...",
  "bytes_utf8": 123,
  "codepoints": 120,
  "graphemes": 119,
  "newline_style": "LF",
  "normalization": {
    "input_is_nfc": true,
    "applied": "NFC"
  }
}
```

#### Tests

Raw hash.

NFC-equivalent strings.

Newline normalization.

Casefold.

Final newline trimming.

### Tool 10: `identifier_inspect`

#### Rationale

`text_inspect` is general. Coding agents need identifier-specific collision detection across lists of names, imports, variables, config keys, package names, etc.

#### Proposed Signature

```json
{
  "identifiers": ["paypal", "pаypal"],
  "language": "generic | python | rust | javascript | typescript | json_key",
  "normalization": "NFC",
  "casefold": false,
  "check_confusables": true
}
```

#### Proposed Result

```json
{
  "identifiers": [
    {
      "raw": "pаypal",
      "normalized": "pаypal",
      "valid": true,
      "scripts": ["Latin", "Cyrillic"],
      "has_invisibles": false,
      "has_confusables": true,
      "warnings": ["mixed_script", "confusable"]
    }
  ],
  "collisions": [
    {
      "kind": "confusable",
      "a": "paypal",
      "b": "pаypal"
    }
  ]
}
```

#### Implementation Notes

Start with generic language mode if language-specific identifier validation is too much.

For language-specific validation, keep the first pass conservative:
- Python: `str.isidentifier()` plus keyword check.
- Rust: simple conservative ASCII identifier rule initially unless a better Unicode identifier implementation exists.
- JavaScript/TypeScript: conservative ASCII identifier rule initially.
- JSON key: any string valid, but inspect confusables/invisibles.

#### Tests

ASCII identifiers.

Python keyword.

Zero-width character.

Mixed Latin/Cyrillic.

Normalization collision.

Casefold collision.

Confusable collision.

## Phase 2: Refinements to Existing Tools

### `list_compare`

Refactor into explicit modes:

```json
{
  "a": ["..."],
  "b": ["..."],
  "mode": "ordered | set | multiset",
  "casefold": false,
  "normalization": "NFC",
  "include_near_matches": false,
  "near_match_threshold": 2
}
```

Expected behavior:

- `ordered`: report first differing index, equal prefix length, aligned replacements/inserts/deletes if feasible.
- `set`: report only-in-A and only-in-B, ignoring counts.
- `multiset`: report count deltas.
- near matches are optional and never replace exact missing/extra results.

Preserve the old `ignore_order` argument if needed, but document it as legacy.

### `text_inspect`

Add optional normalization analysis:

```json
{
  "text": "...",
  "normalize": "none | NFC | NFD | NFKC | NFKD",
  "compare_normalized": true
}
```

This is directly related to the question of whether `inspect_text()` should gain a `normalize_text()` option. Recommended answer: yes, but implement it explicitly as an option that reports both original and normalized analysis, rather than silently inspecting only the normalized form.

Result should include:

```json
{
  "original": {
    "safe_repr": "...",
    "confusables": [],
    "invisibles": []
  },
  "normalized": {
    "form": "NFKC",
    "text": "...",
    "safe_repr": "...",
    "changed": true,
    "diff": []
  },
  "normalization_findings": [
    {
      "kind": "compatibility_fold",
      "message": "NFKC changes fullwidth character to ASCII"
    }
  ]
}
```

Important: Do not hide the original text. Agents need to know whether the dangerous property exists in the raw text, the normalized text, or both.

### `text_count`

Consider adding `count_mode`:

```json
{
  "count_mode": "codepoint | grapheme | byte | substring"
}
```

Current behavior counts single codepoints. That is fine, but agents may ask “count user-perceived characters” or “count bytes.” Make the mode explicit.

### `math_eval`

Keep `math_eval`, but add structured helpers:

- `unit_convert`
- `unit_info`
- `constant_lookup`

This makes codegg less dependent on natural-language parsing when it already knows the operands.

### `validate_brackets`

Add quote/comment awareness only if it can be done deterministically and documented.

Potential option:

```json
{
  "language_hint": "none | python | rust | javascript | json"
}
```

Default should remain simple structural bracket checking. Language-aware behavior can be deferred.

## Phase 3: Additional Useful but Lower-Priority Tools

### `version_compare`

Compare two version strings with explicit scheme:

```json
{
  "a": "1.2.3",
  "b": "1.2.10",
  "scheme": "semver | pep440 | loose"
}
```

For Python stdlib only, PEP 440 support is difficult without `packaging`; defer full PEP 440 unless adding a dependency is acceptable. Semver is feasible to implement locally for basic cases.

### `semver_satisfies`

Check if a version satisfies a semver range. This is useful but more complex. Defer unless codegg has a strong need.

### `toml_validate` and `toml_shape`

If Python 3.11+ is required, use `tomllib`.

Useful for:
- `pyproject.toml`
- Rust `Cargo.toml`
- tool config files

If Python 3.10 compatibility is required and no dependency is allowed, defer TOML.

### `list_dedupe` and `list_sort`

Useful but not urgent. These should support normalization/casefold and stable output.

## MCP Exposure Strategy for codegg

For codegg integration, expose tools in tiers to avoid context pollution.

Tier 0: always useful, small, deterministic:
- `text_equal`
- `text_count`
- `text_measure`
- `text_window`
- `text_fingerprint`
- `validate_json`
- `json_query`
- `validate_regex`
- `regex_finditer`
- `path_normalize`
- `glob_match`
- `list_compare`

Tier 1: security/Unicode-specific:
- `text_inspect`
- `text_diff_explain`
- `identifier_inspect`

Tier 2: math/unit:
- `math_eval`
- `unit_convert`
- `unit_info`
- `constant_lookup`

Tier 3: lower-frequency structured helpers:
- `json_shape`
- `json_canonicalize`
- `version_compare`
- `toml_validate`
- `toml_shape`

The MCP server may still expose all tools, but `codegg` should choose which tool descriptions to load into active model context depending on the task. If codegg supports tool namespaces or lazy tool discovery, use that.

## Testing Strategy

Add tests in layers.

Primitive tests:
- no MCP envelope
- pure deterministic assertions
- edge-case heavy

Synthesis tests:
- realistic agent tasks
- structured result shape
- truncation behavior
- stable ordering

MCP adapter tests:
- `initialize`
- `tools/list`
- `tools/call`
- unknown method
- unknown tool with close match
- invalid params
- oversized request
- malformed JSON
- unsupported batch request behavior

Golden tests:
- canonical `tools/list` snapshot
- representative result snapshots for each tool
- docs examples

Fuzz/property tests if feasible:
- Unicode strings for normalization/equality
- random JSON round-trip for canonicalization
- random path components for normalization invariants

Avoid tests that depend on host OS path behavior.

## Suggested Implementation Order for MiMo v2.5

Do not try to implement every tool in one pass. Use this order:

1. Contract cleanup:
   - docs/schema/handler parity
   - error taxonomy
   - golden `tools/list` test
   - request-size limit
   - batch rejection behavior

2. Add `text_window`.

3. Add JSON tools:
   - `json_canonicalize`
   - `json_query`
   - `json_shape`

4. Add regex tools:
   - `regex_finditer`
   - `regex_safety_check`
   - stricter regex limits

5. Add path/glob tools:
   - `path_normalize`
   - `glob_match`

6. Add `text_fingerprint`.

7. Add `identifier_inspect`.

8. Refine existing tools:
   - `list_compare` modes
   - `text_inspect` normalization option
   - `text_count` count modes

9. Add structured math/unit helpers only after the above is stable.

## File Touch Map

Likely files to edit:

- `nl_calc/mcp/server.py`
  - request-size limit
  - batch handling
  - response behavior
  - handler registration

- `nl_calc/mcp/tools.py`
  - new tool wrappers
  - standardized envelopes
  - argument validation
  - error taxonomy

- `nl_calc/mcp/schemas.py`
  - new tool schemas
  - corrected existing schemas
  - defaults and descriptions

- `nl_calc/exact/primitives.py`
  - position conversion helpers
  - fingerprint canonicalization helpers
  - grapheme boundary helpers if needed

- `nl_calc/exact/validate.py`
  - JSON canonical/query/shape helpers
  - regex finditer
  - regex safety check
  - path/glob validation if not split elsewhere

- `nl_calc/exact/synthesis.py`
  - `text_window`
  - `identifier_inspect`
  - composed tool-level helpers

Consider adding new files if existing files become too broad:

- `nl_calc/exact/json_tools.py`
- `nl_calc/exact/regex_tools.py`
- `nl_calc/exact/path_tools.py`
- `nl_calc/exact/fingerprint.py`
- `nl_calc/exact/identifiers.py`

Docs to update:

- `docs/mcp.md`
- `architecture/mcp.md`
- `architecture/overview.md` if the tool list or module layout changes

Tests to add/update:

- MCP tests, likely under existing test directory
- exact primitive/synthesis tests
- docs example tests if feasible

## Coding Guidelines

Keep functions small.

Prefer dataclasses or typed dictionaries for internal structured results if consistent with the existing codebase.

Do not return sets directly; convert to sorted lists.

Do not include non-deterministic fields such as timestamps.

Do not expose Python exception text directly if it might vary across versions, unless sanitized and tested loosely.

Do not use `eval`.

Do not add network calls.

Do not add platform-dependent path semantics.

Use explicit `max_*` parameters and enforce upper bounds.

When returning truncated output, always include `truncated: true`.

When an operation is heuristic, say so in a field such as:

```json
{
  "heuristic": true,
  "confidence": "medium"
}
```

This matters especially for `regex_safety_check` and confusable/identifier warnings.

## Acceptance Criteria for the Whole Plan

The MCP server starts with `calc --mcp`.

`initialize` returns a valid server response.

`tools/list` exposes all implemented tools and no missing schemas.

Every MCP tool has:
- schema entry
- handler entry
- wrapper implementation
- docs section
- at least one positive test
- at least one negative/error test where applicable

All existing tests continue to pass.

The new tools are deterministic and pure.

The server remains stdio-based and side-effect-free.

The repo remains suitable as a reference codebase for a Rust `eggsact` rewrite.

The resulting MCP surface is materially more useful for `codegg` because it can answer exact low-level questions about source text, config files, regexes, paths, identifiers, lists, units, and fingerprints without spending frontier-model context.
