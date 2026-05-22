# MCP Server Review Plan

## Verified Claims

1. **Architecture diagram** - The architecture correctly shows AI Agent <-> MCP Server <-> exact tools
2. **Protocol** - JSON-RPC 2.0 over stdio is correctly implemented (lines 193-226 in server.py)
3. **Request Handling** - All routing handlers present: `handle_request`, `_handle_initialize`, `_handle_list_tools`, `_handle_call_tool`
4. **Tool definitions** - All tools documented in arch doc are present in TOOL_SCHEMAS
5. **Error Envelope** - ErrorEnvelope TypedDict correctly defined in schemas.py (lines 13-18)
6. **Files** - server.py, tools.py, schemas.py are the only files (no extra files)

## Discrepancies

| Issue | Arch Doc | Actual Implementation |
|-------|----------|----------------------|
| `mcp_main()` alias | Claims `mcp_main()` is available as alias for `main()` | NOT DEFINED - only `main()` exists |
| `SuccessEnvelope` | Documented as "standardized envelopes" but shows only ErrorEnvelope definition | SuccessEnvelope exists in schemas.py but is **never used** - tools.py uses `{"ok": True, "result": ...}` dicts directly instead |
| `text_truncate` tool | Not mentioned in arch doc | Implemented and registered in TOOL_HANDLERS |

## Bugs Found

### Priority: High

1. **`mcp_main` alias missing** (server.py:188)
   - Arch doc claims: `from nl_calc.mcp.server import main, mcp_main  # Both refer to same function`
   - Reality: `mcp_main` is not defined. Build system may rely on this alias.
   - Fix: Add `mcp_main = main` after main() definition or at module level

2. **`SuccessEnvelope` unused** (schemas.py:21-24, tools.py)
   - `SuccessEnvelope` TypedDict is defined but never imported or used
   - All tools use raw `{"ok": True, "result": ...}` dicts instead
   - This creates inconsistency with ErrorEnvelope usage
   - Fix: Either use SuccessEnvelope consistently or remove dead code

### Priority: Medium

3. **`_handle_initialize` doesn't exist** (server.py)
   - Arch doc table shows `_handle_initialize()` handler
   - Actual: initialization is handled inline in `handle_request()` (lines 160-174)
   - Not a bug, but documentation is misleading about function structure

4. **`text_truncate` undocumented** (tools.py:377-418)
   - Tool exists in TOOL_HANDLERS and TOOL_SCHEMAS
   - Not listed in arch doc "Available Tools" section
   - Fix: Add to arch doc or remove from TOOL_HANDLERS if not meant to be exposed

## Improvements with Priority

### High

1. **Add `mcp_main` alias** - Add `mcp_main = main` to server.py for build compatibility

2. **Unify envelope usage** - Either:
   - Import and use `SuccessEnvelope` in tools.py instead of raw dicts
   - Or remove `SuccessEnvelope` from schemas.py if intentionally unused

### Medium

3. **Update arch doc** - Add `text_truncate` to "Available Tools" section or remove from TOOL_HANDLERS

4. **Clarify handler structure** - Update arch doc to reflect that `_handle_initialize` is not a separate function

### Low

5. **Add type hints to ErrorEnvelope/SuccessEnvelope fields** - Currently using bare `list[str]` instead of `list[str]`

6. **Consider adding `tools/list` changed notification support** - Currently `capabilities.tools.listChanged = False` but no support for signaling changes