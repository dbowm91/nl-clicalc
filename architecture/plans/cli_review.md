# cli.md Architecture Review

## Verified Claims

1. **Entry Point**: __main__.py is bootstrap that imports main() from normalize.py - MATCHES
2. **CLI Options**: All documented options (-h, --help, --usage, -v/--version, -e/--expression, -q/--quiet, -s/--show, --json, -i/--interactive, --mcp) - MATCHES (normalize.py lines 1220-1254)
3. **Text Commands**: inspect, count, regex - all MATCH (normalize.py lines 1106-1212)
4. **Interactive REPL**: Commands (help, history, clear, quit/exit) - MATCHES (normalize.py lines 991-1031)
5. **Shell Glob Detection**: Detects expanded globs - MATCHES (normalize.py lines 1284-1304)
6. **Output Formats**: plain, quiet, json - MATCHES
7. **Error Handling**: User-friendly error messages - MATCHES (normalize.py lines 602-616)

## Discrepancies

1. **Documentation error**:
   - Architecture doc line 13 mentions "`normalize_main()` for build compatibility" but this alias does not exist in source code
   - The `-v` flag is for `--version` only, NOT verbose mode (architecture doc line 121 incorrectly says verbose mode shows traceback)
   - `error_message(verbose=False)` is called in `run()` but `verbose` is never set to True in main()

2. **Missing from documentation**:
   - Entry point is actually __main__.py which just imports from normalize.py (delegation pattern not fully explained)
   - No mention that the actual main() is in normalize.py, not __main__.py

## Bugs Found

No actual bugs - the CLI works as expected from user perspective. Documentation issues only.

## Improvements

1. **Medium Priority**: Remove erroneous mention of `normalize_main()` alias
2. **Medium Priority**: Fix verbose mode claim - `-v` is version flag, not verbose traceback
3. **Low Priority**: Document that actual CLI logic is in normalize.py main(), not in __main__.py

## Priority

- **Medium**: Fix documentation errors about normalize_main() and verbose mode
- **Low**: Clarify delegation pattern between __main__.py and normalize.py