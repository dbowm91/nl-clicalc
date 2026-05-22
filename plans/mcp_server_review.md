# MCP Server Module Review

## Verified Claims

| Claim | Status |
|-------|--------|
| JSON-RPC 2.0 over stdio | Verified - `server.py:191-224` reads from stdin, writes to stdout |
| `handle_request()` routes methods | Verified - `server.py:147-183` dispatches `initialize`, `tools/list`, `tools/call`, `notifications/initialized` |
| `_handle_list_tools()` returns schema | Verified - `server.py:130-144` iterates `TOOL_SCHEMAS` |
| `_handle_call_tool()` executes tools | Verified - `server.py:65-127` dispatches to `TOOL_HANDLERS` |
| All 10 tools implemented | Verified - `server.py:28-39` defines all tools |
| Error envelope format | Verified - `schemas.py:13-18` defines `ErrorEnvelope` with `ok`, `error_type`, `error`, `hints` |
| Case-insensitive tool matching | Verified - `server.py:54-62` `_find_close_match()` provides suggestions |
| Tool result wrapped in `content[].text` | Verified - `server.py:106-116` |
| `main()` entry point | Verified - `server.py:186-224` |

## Discrepancies

### 1. `mcp_main()` Alias Not in Source
**Doc claims** (`mcp_server.md:148-152`):
```python
from nl_calc.mcp.server import main, mcp_main  # Both refer to same function
```

**Actual**: `server.py` only defines `main()`. The `mcp_main` alias is created at build time by `build_single.py:255-256`:
```python
if '"""Main entry point for MCP server.' in code:
    code = code.replace("def main() -> int:", "def mcp_main() -> int:")
```

**Impact**: Documentation suggests a runtime alias that doesn't exist in source. Users importing from the source module won't find `mcp_main`.

### 2. `mcp_main()` Import Path
**Doc claims** (`mcp_server.md:152`):
```python
from nl_calc.mcp.server import main, mcp_main
```

**Actual**: `normalize.py:1259-1260` imports from `nl_calc.mcp.server` and calls `mcp_main()`:
```python
from nl_calc.mcp.server import mcp_main
return mcp_main()
```

This works only after `build_single.py` renames `main` to `mcp_main`. Direct import from source fails.

## Bugs Found

### Bug 1: Unused `SuccessEnvelope` TypedDict
**Location**: `schemas.py:21-25`

```python
class SuccessEnvelope(TypedDict):
    """Standard success envelope for MCP tool responses."""
    ok: bool
    result: dict
```

**Issue**: `tools.py` never uses `SuccessEnvelope`. Success responses use `_success_response()` which returns a plain dict `{"ok": True, "result": ...}`, not the TypedDict.

**Fix**: Either use `SuccessEnvelope` consistently in `tools.py` or remove the unused TypedDict.

### Bug 2: Redundant Double Length Check
**Location**: `tools.py:77-80`

```python
if len(expression) > MAX_TEXT_LENGTH:
    return _error_response("InputError", f"Input exceeds maximum length of {MAX_TEXT_LENGTH}")
if len(expression) > MAX_EXPRESSION_LENGTH:
    return _error_response("InputError", f"Expression exceeds maximum length of {MAX_EXPRESSION_LENGTH}")
```

**Issue**: `MAX_TEXT_LENGTH = 100_000` and `MAX_EXPRESSION_LENGTH = 10_000`. If expression > 100K, first check triggers. If 10K < expression <= 100K, second check triggers. But `MAX_TEXT_LENGTH` is never used elsewhere in `math_eval` - it's imported but only one of the two checks can ever fire.

**Fix**: If `MAX_TEXT_LENGTH` is intended as a separate limit, restructure checks. If only `MAX_EXPRESSION_LENGTH` matters, remove the redundant `MAX_TEXT_LENGTH` check.

## Improvements

### Improvement 1: Document `mcp_main` Build-Time Alias
**Priority**: Medium

The documentation should note that `mcp_main` is a build-time alias created by `build_single.py`, not a native export of `server.py`. Users of the source module should use `main()`.

**Fix**: Update `mcp_server.md:148-152`:
```markdown
For build compatibility, the function is renamed to `mcp_main()` during assembly by `build_single.py`:
- Source module: `from nl_calc.mcp.server import main`
- Built single file: `from nl_calc.mcp.server import mcp_main`
```

### Improvement 2: Use `SuccessEnvelope` Consistently
**Priority**: Low

`SuccessEnvelope` is defined but not used. Either use it in `tools.py`:
```python
return SuccessEnvelope(ok=True, result=result)
```
or remove it to avoid confusion.

### Improvement 3: Remove Redundant Input Length Check
**Priority**: Low

The double check in `math_eval` is confusing. If both limits are intended, use a chained condition:
```python
if len(expression) > MAX_TEXT_LENGTH:
    return _error_response("InputError", f"Input exceeds maximum length of {MAX_TEXT_LENGTH}")
elif len(expression) > MAX_EXPRESSION_LENGTH:
    return _error_response("InputError", f"Expression exceeds maximum length of {MAX_EXPRESSION_LENGTH}")
```
This makes the logic clearer and adds `elif` since only one can trigger.

## Summary

| Category | Count |
|----------|-------|
| Verified Claims | 9 |
| Discrepancies | 2 |
| Bugs | 2 |
| Improvements | 3 |

**Key Finding**: The documentation is generally accurate but fails to mention the build-time `mcp_main` alias, which could confuse users. The source code has a minor inconsistency with unused `SuccessEnvelope` and a redundant input length check in `math_eval`.

**Priority**: Medium - The `mcp_main` documentation gap is the most significant issue as it could cause import errors for users following the documented interface.