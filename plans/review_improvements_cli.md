# CLI Module Review - Improvement Plan

## Review Summary

Document reviewed:
- `architecture/cli.md` (125 lines)
- `nl_calc/__main__.py` (19 lines)
- `nl_calc/normalize.py` main function (lines 1226-1340), REPL (lines 1002-1042), text commands (lines 1117-1223)

---

## Verified Claims

### Entry Point Architecture ✓
- `__main__.py:12-18` correctly bootstraps by importing `main` from `normalize.py` and calling it
- Build system correctly renames `normalize.main()` to `normalize_main()` in single-file build (`build_single.py:236`)

### Text Commands ✓
- `inspect`, `count`, `regex` commands implemented in `_cli_text_command()` at `normalize.py:1117-1223`
- Commands follow documented syntax

### Interactive REPL ✓
- REPL implemented in `_run_repl()` at `normalize.py:1002-1042`
- Commands `help`, `history`, `clear`, `quit`/`exit` work as documented

### Shell Glob Detection ✓
- Glob expansion detection at `normalize.py:1296-1316`
- Error message matches documentation

---

## Discrepancies

### 1. `--verbose` vs `--show` Documentation Error

**Documentation** (`cli.md:28`):
```
| `-s`, `--show` | Show expression in output |
```

**Code** (`normalize.py:1246,1258-1263`):
```python
parser.add_argument("--verbose", action="store_true", help="Show expression in output")
parser.add_argument("-s", "--show", action="store_true", help="Show expression in output (default for interactive)")
```

**Issue**: Documentation only mentions `-s`/`--show` but code also has `--verbose` that does the same thing. This is undocumented functionality.

**Severity**: Low (docs just need updating)

### 2. Interactive Mode Expression Display Logic Bug

**Documentation** (`cli.md:71`):
```
# >>> five plus two
# 5+2 -> 7
```

**Code** (`normalize.py:1287,1328-1333`):
```python
if args.interactive:
    return _run_repl(show_expression=True)

# ...
elif args.show:
    show_expression = True
elif quiet_by_default:
    show_expression = False
else:
    show_expression = False  # BUG: Should be True for interactive by default
```

**Issue**: When running `calc -i`, `show_expression=True` is passed correctly to `_run_repl`. However, when `run()` is called inside REPL (`normalize.py:1037`), the logic at lines 1330-1333 has `quiet_by_default=False` for interactive mode, but the final `else` also sets `show_expression = False`, contradicting the explicitly passed `True`.

**Severity**: Medium (feature works due to `_run_repl` passing `show_expression=True` directly, but logic is convoluted)

### 3. REPL Exit Command `exit()` vs `exit`

**Documentation** (`cli.md:79`):
```
- `quit` / `exit` - Exit REPL
```

**Code** (`normalize.py:1021`):
```python
if line.lower() in ("quit", "exit", "exit()"):
```

**Issue**: Documentation doesn't mention `exit()` as valid, but code accepts it.

**Severity**: Low (docs need updating)

---

## Potential Bugs

### Bug 1: REPL History Result Variable Conflict

**Location**: `normalize.py:1039-1040`
```python
if exit_code == 0 and _ is not None:
    history.append((line, _))
```

**Issue**: Uses `_` as result variable but `_` is a Python built-in for last expression value. While this works, it's shadowing a useful Python feature. The `_` from `run()` is the first return value (result), but the code doesn't use it consistently.

**Severity**: Low (works but confusing)

### Bug 2: JSON Output Format Inconsistency

**Location**: `normalize.py:981-987`
```python
if output_format == "json":
    import json
    if show_expression:
        print(json.dumps({"expression": joined, "result": str(result)}))
    else:
        print(json.dumps({"result": str(result)}))
```

**Issue**: Documentation (`cli.md:111-115`) shows JSON output without the `joined` (normalized) expression. The code includes `joined` when `show_expression=True`. This could be intentional but differs from plain output behavior.

**Severity**: Low (could be intentional design)

---

## Improvement Suggestions

### High Priority

1. **Fix confusing show_expression logic** (`normalize.py:1324-1333`)
   - Current logic is hard to follow
   - Should explicitly handle each case with clear precedence

### Medium Priority

2. **Update documentation for `--verbose` flag**
   - Add to CLI options table in `cli.md:20-29`
   - Currently only `-s`/`--show` documented

3. **Add `exit()` to REPL documentation**
   - Update `cli.md:79` to mention `exit()` as valid

### Low Priority

4. **Consider renaming REPL result variable**
   - `normalize.py:1039` uses `_` which shadows Python's last-expression-value built-in
   - Could use `result` instead for clarity

5. **Consider consolidating duplicate logic**
   - `_run_repl` hardcodes `show_expression=True` then passes it to `run()`
   - The `show_expression` logic in `main()` is then partially ignored

---

## Code Reference Summary

| Component | Location | Status |
|-----------|----------|--------|
| Entry point bootstrap | `__main__.py:12-18` | ✓ Correct |
| Main CLI function | `normalize.py:1226-1336` | ✓ Works |
| REPL implementation | `normalize.py:1002-1042` | ✓ Works |
| Text commands | `normalize.py:1117-1223` | ✓ Works |
| Glob detection | `normalize.py:1296-1316` | ✓ Works |
| Help system | `normalize.py:1059-1114` | ✓ Works |
| Build renaming | `build_single.py:236` | ✓ Correct |

---

## Files Reviewed

- `architecture/cli.md` - 125 lines
- `nl_calc/__main__.py` - 19 lines
- `nl_calc/normalize.py` - key sections at lines 959-1340
- `build_single.py` - lines 230-270 (build compatibility)