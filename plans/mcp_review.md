# mcp Architecture Review

## Document: architecture/mcp.md

## Verified Claims
| Claim | Status | Evidence |
|-------|--------|----------|
| Module structure (4 files) | VERIFIED | `__init__.py`, `schemas.py`, `tools.py`, `server.py` all exist |
| stdio-based JSON-RPC 2.0 | VERIFIED | server.py:312-372 reads stdin, writes stdout |
| `handle_request` routes tools/list and tools/call | VERIFIED | server.py:286-309 |
| Error codes -32700, -32600, -32601, -32602, -32603, -32000 | VERIFIED | server.py:142-151, 185, 201, 225, 307 |
| `notifications/initialized` returns None | VERIFIED | server.py:299-300 |
| `main` reads line-by-line from stdin | VERIFIED | server.py:317-318 |
| Batch requests rejected with -32600 | VERIFIED | server.py:333-342 |
| MAX_REQUEST_BYTES = 1_000_000 | VERIFIED | server.py:139 |
| `mcp_main = main` alias | VERIFIED | server.py:380 |
| `_find_close_match` for case-insensitive matching | VERIFIED | server.py:154-162 |
| Input limits: MAX_TEXT_LENGTH=100000, MAX_EXPRESSION_LENGTH=10000, MAX_LIST_ITEMS=10000, MAX_REGEX_SAMPLES=100 | VERIFIED | tools.py:185-188 |
| `_sanitize_error` uses ascii replace | VERIFIED | tools.py:191-193 |
| `handle_request` returns `dict \| None` | VERIFIED | server.py:286 |
| `initialize` handler returns protocolVersion "2024-11-05" | VERIFIED | server.py:274 |
| Server name "eggsact-exact", version "1.0.0" | VERIFIED | server.py:279-280 |
| Success response wraps result in `{"content": [{"type": "text", "text": json.dumps(result)}]}` | VERIFIED | server.py:206-217 |
| Error response uses code -32000 with `data` field containing error envelope | VERIFIED | server.py:196-204 |

## Discrepancies

### 1. **[MAJOR] ErrorEnvelope TypedDict has undocumented fields**
- **Document (lines 45-50)**: Shows 4 fields: `ok`, `error_type`, `error`, `hints`
- **Code (schemas.py:32-39)**: Has 6 fields: `ok`, `error_type`, `error`, `hints`, `tool`, `warnings`
- **Impact**: Documentation is missing `tool` (tool name that produced error) and `warnings` (list of warnings) fields that are present in actual code

### 2. **[MAJOR] TOOL_SCHEMAS count is drastically wrong**
- **Document (line 54)**: Claims "39 total"
- **Code (schemas.py:42)**: Actually defines 56 tools in TOOL_SCHEMAS
- **Missing from doc**: `line_range_extract`, `line_range_compare`, `shell_split`, `shell_quote_join`, `argv_compare`, `markdown_structure`, `code_fence_extract`, `dotenv_validate`, `ini_validate`, `patch_apply_check`, `patch_summary`, `unicode_policy_check`, `canonicalize_text`, `identifier_table_inspect`, `version_constraint_check`, `cargo_toml_inspect`, `prompt_input_inspect` — 17 tools entirely undocumented

### 3. **[MAJOR] _error_response signature is incomplete**
- **Document (lines 163-170)**:
  ```python
  def _error_response(error_type: str, error: str, hints: list[str] | None = None) -> dict
  ```
- **Code (tools.py:291-295)**: Actually has 4 parameters:
  ```python
  def _error_response(error_type: str, error: str, hints: list[str] | None = None, tool: str | None = None) -> dict
  ```
- **Impact**: Document doesn't show `tool` parameter used to identify which tool errored

### 4. **[MAJOR] _success_response signature is drastically incomplete**
- **Document (lines 172-175)**: Shows only `result: Any` parameter, returns `{"ok": True, "result": result}`
- **Code (tools.py:308-316)**: Actually has 5 additional parameters:
  ```python
  def _success_response(result: Any, tool: str | None = None, warnings: list[str] | None = None,
                        limits_applied: list[str] | None = None, findings: list[dict] | None = None,
                        machine_code: str | None = None, recommended_next_tool: str | list[str] | None = None) -> dict
  ```
- **Impact**: The entire response envelope system with `tool`, `warnings`, `limits_applied`, `findings`, `machine_code`, and `recommended_next_tool` is completely undocumented

### 5. **[MAJOR] Response format documentation is incomplete**
- **Document (lines 336-357)**: Shows basic success/error structure
- **Code (server.py:196-217)**: The success response actually wraps the result in `{"content": [{"type": "text", "text": json.dumps(result)}]}`. The error response includes a `data` field with the full error envelope, not just the message
- **Impact**: The documented format is a simplified view; actual responses are more complex

### 6. **[MAJOR] TOOL_HANDLERS is missing documented tools**
- **Document (lines 268-310)**: Lists 39 tools in TOOL_HANDLERS map
- **Code (server.py:77-137)**: Actually defines 47 tools
- **Additional tools in code but not doc**: `argv_compare`, `cargo_toml_inspect`, `code_fence_extract`, `dotenv_validate`, `identifier_table_inspect`, `ini_validate`, `line_range_compare`, `line_range_extract`, `markdown_structure`, `patch_apply_check`, `patch_summary`, `prompt_input_inspect`, `shell_argv_compare`, `shell_quote_join`, `shell_split`, `unicode_policy_check`, `canonicalize_text`, `version_constraint_check`

### 7. **[MEDIUM] _handle_initialize description is misleading**
- **Document (line 264)**: "Note: `_handle_initialize` is a separate function in `server.py` called directly from `handle_request`'s routing logic."
- **Code (server.py:268-283)**: `_handle_initialize` IS a separate function, but `handle_request` (line 297) calls it inline (`return _handle_initialize(request)`), not via special routing logic. The phrasing "called directly" is ambiguous.
- **Impact**: Minor documentation clarity issue

### 8. **[MEDIUM] text_equal schema in doc is simplified example**
- **Document (lines 131-152)**: Shows `text_equal` schema with partial fields
- **Code (schemas.py:164-214)**: Actually has additional fields: `ignore_newline_style`, `ignore_trailing_whitespace`, `ignore_final_newline`
- **Impact**: The document shows an abridged version that omits 3 boolean parameters

### 9. **[MEDIUM] text_measure schema in doc omits detail field enum values**
- **Document (lines 118-129)**: Shows `text_measure` schema but only partially
- **Code (schemas.py:130-163)**: The `detail` field has enum `["summary", "normal", "full"]` but doc doesn't explicitly list these options in the schema excerpt

### 10. **[MEDIUM] math_eval schema in doc simplified**
- **Document (lines 98-114)**: Shows basic math_eval schema
- **Code (schemas.py:43-64)**: Actually has `tier`, `tags`, `inputSchema`, `outputSchema` with additional detail in description

### 11. **[LOW] Entry point section implies bidirectional aliasing**
- **Document (lines 438-441)**:
  ```python
  from eggcalc.mcp.server import main, mcp_main  # Both refer to same function
  ```
- **Code (server.py:312, 380)**: `main` is defined first, then `mcp_main = main`. The statement is technically true but implies both are equally "original" when `mcp_main` is the alias
- **Impact**: Minor - phrasing could be clearer

## Bugs Identified
| Bug | Location | Severity | Description |
|-----|----------|----------|-------------|
| No bugs | - | - | Code appears functionally correct |

## Improvements Surface
| Area | Priority | Description |
|------|----------|-------------|
| Documentation | High | ErrorEnvelope needs `tool` and `warnings` fields documented |
| Documentation | High | TOOL_SCHEMAS count is 56, not 39. Document all 56 tools or clarify subset |
| Documentation | High | _error_response and _success_response signatures are significantly incomplete |
| Documentation | High | Response format section should document the actual wrapping in `content` array |
| Documentation | Medium | 17 tools are implemented but completely undocumented in the tool table (lines 56-96) |
| Documentation | Medium | text_equal schema excerpt omits 3 boolean parameters |
| Documentation | Medium | Close match suggestions mechanism (lines 312-320) is documented but the `_find_close_match` function implementation details (substring matching) could be clarified |
| Documentation | Low | _handle_initialize note is worded ambiguously |
| Documentation | Low | Entry point alias explanation could be clearer about which is primary |
| Consistency | Medium | TOOL_HANDLERS uses `_mcp` suffixes inconsistently (some tools like `path_compare_mcp` vs `path_compare` directly) — this works but the naming convention could be documented |

## Notes
- The architecture document captures the high-level design correctly: stdio-based JSON-RPC, tool registry, error envelopes, case-insensitive matching, input validation
- The most significant issue is that the document describes a simplified/shrunk-down view of the actual implementation. Many fields, parameters, and tools that exist in code are not mentioned in the document at all
- The ErrorEnvelope discrepancy (4 documented fields vs 6 actual) means agents using the documented schema would produce incomplete error responses
- The `_success_response` documentation is particularly misleading — it shows a 2-field response but actual success envelopes contain 6+ fields including `tool`, `warnings`, `limits_applied`, `findings`, `machine_code`, and `recommended_next_tool`
- All security claims (input length limits, error sanitization via ASCII replacement) are verified correct
- The tool discovery via `tools/list` returning filtered results based on tier/tags is correctly implemented (server.py:230-265) but not documented in the architecture
- The MCP protocol version "2024-11-05" and server identity "eggsact-exact" are correctly documented
