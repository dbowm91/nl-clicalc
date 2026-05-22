# mcp_server.md Architecture Review

## Verified Claims

1. **Purpose**: MCP server for nl-calc exact tools via stdio - MATCHES (lines 1-6)
2. **Protocol**: JSON-RPC 2.0 over stdio - MATCHES (lines 186-224)
3. **Architecture diagram**: Shows correct modules (primitives, unicode_tools, diff, etc.) - MATCHES
4. **`handle_request()`**: Routes MCP requests to handlers - MATCHES (line 147)
5. **Method routing**: initialize, tools/list, tools/call, notifications/initialized - MATCHES (lines 154-174)
6. **Available Tools**: All 10 tools in TOOL_HANDLERS (lines 28-39) - MATCHES
7. **`main()` entry point**: Reads stdin, writes to stdout - MATCHES (line 186)
8. **Error handling**: Returns JSON-RPC error format - MATCHES (lines 42-52, 81-88, 119-127)

## Discrepancies

1. **ErrorEnvelope class mismatch - MAJOR**:
   - Architecture doc (lines 128-136) shows `ErrorEnvelope` TypedDict with `ok`, `error_type`, `error`, `hints`
   - Code does NOT define `ErrorEnvelope` class - errors are returned as standard JSON-RPC errors with `code` and `message`
   - Code uses JSON-RPC error codes like -32600, -32602, -32000, etc.
   - Architecture doc describes a non-existent class

2. **mcp_main() alias does not exist**:
   - Architecture doc line 150-151 shows `from nl_calc.mcp.server import main, mcp_main`
   - But code only defines `main()`, no `mcp_main` alias

3. **ServerInfo not documented**:
   - Code returns `serverInfo: {"name": "nl-calc-exact", "version": "1.0.0"}` (line 167-169)
   - Architecture doc doesn't mention server name/version

## Bugs Found

No bugs. Code is correct. Documentation issues only.

## Improvements

1. **High Priority**: Remove ErrorEnvelope class description from architecture doc - it doesn't exist
2. **High Priority**: Remove mcp_main() alias reference - doesn't exist
3. **Low Priority**: Add serverInfo (name: "nl-calc-exact", version: "1.0.0") to documentation

## Priority

- **High**: Fix documentation errors (ErrorEnvelope, mcp_main alias)
- **Low**: Document serverInfo