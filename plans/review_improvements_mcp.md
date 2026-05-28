# mcp Module Review — Improvement Plan

**Reviewed:** architecture/mcp.md against nl_calc/mcp/server.py, tools.py, schemas.py
**Date:** 2026-05-28

## Verified Claims (with line references)

- ErrorEnvelope TypedDict (docs line 45-50) — VERIFIED at schemas.py:13-18
- TOOL_SCHEMAS 11 tools list (docs line 56-68) — VERIFIED at schemas.py:21-332
- Input limits MAX_TEXT_LENGTH, MAX_EXPRESSION_LENGTH, MAX_LIST_ITEMS, MAX_REGEX_SAMPLES (docs lines 176-180) — VERIFIED at tools.py:46-49
- TOOL_HANDLERS map (docs lines 213-226) — VERIFIED at server.py:29-41
- _find_close_match function (docs lines 233-236) — VERIFIED at server.py:56-64
- Error code -32600 InvalidRequest — VERIFIED at server.py:50
- Error code -32601 MethodNotFound — VERIFIED at server.py:187
- Error code -32602 InvalidParams — VERIFIED at server.py:87
- Error code -32603 InternalError — VERIFIED at server.py:223
- Error code -32000 ToolError — VERIFIED at server.py:102, 126
- main() entry point (docs line 345) — VERIFIED at server.py:193
- mcp_main build alias (docs line 353) — VERIFIED at server.py:239

## Discrepancies Between Documentation and Code

- [LOW] Documentation text about "_handle_initialize" called "inline" is imprecise but not technically wrong
  - Documentation says: "`initialize` | `_handle_initialize()` (called inline) | Initialize connection" (docs line 203)
  - Code actually does: handle_request routes "initialize" method to _handle_initialize at server.py:178-179
  - Impact: Minor clarity issue; code behaves correctly

- [LOW] Error code -32700 (Parse error) appears in code (server.py:209) but is not documented in the error codes table
  - Documentation shows codes -32600 to -32000 (docs lines 240-246)
  - Code has -32700 for JSON decode errors at server.py:209
  - Impact: JSON parse errors may be returned with code -32700 but users have no reference for this code

## Potential Bugs

- None identified. Code is well-structured with proper error handling, input validation, and sanitization.

## Improvement Suggestions

### MEDIUM Priority

- Document error code -32700 (Parse error) in the error codes table at mcp.md:240-246
  - Currently documented range is -32600 to -32603 and -32000
  - Code at server.py:209 returns -32700 for JSON decode failures
  - Suggested addition: `| -32700 | ParseError | Invalid JSON |`

### LOW Priority

- Consider clarifying "(called inline)" note at docs line 203 — code shows `handle_request` routes to `_handle_initialize` via conditional check, not a direct call
  - Current wording: "`initialize` | `_handle_initialize()` (called inline)"
  - This is technically accurate (the function is defined inline within routing) but could be clearer
  - Alternative wording: "`initialize` | `_handle_initialize()` | via handle_request routing"

## Summary

The MCP architecture documentation is accurate and well-aligned with the source code. All public functions, constants, and error codes match between docs and code. Only two minor improvements are needed: documenting the -32700 error code used for JSON parse errors, and slightly clarifying how the initialize request is routed.
