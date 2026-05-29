# Eggsact / eggcalc MCP Expansion Plan

## Status: COMPLETED (2026-05-29)

All 17 phases from this plan have been verified as fully implemented.

## Implementation Summary

- **60 MCP tools** implemented and exposed
- **6 new CLI commands**: replace-check, lines, patch-check, shell-split, md-structure, dotenv-check
- **1231 tests passing** with comprehensive fixture coverage
- **21 fixture files** with 150+ test cases across text, unicode, patches, markdown, config, paths, and shell categories
- **Consistent documentation** across README, docs/mcp.md, and docs/tool_inventory.md
- **Structured findings envelope** for machine-readable results
- **Tiered tool exposure** with 5 named profiles (minimal, coding-agent-default, text-unicode-heavy, config-heavy, rust-project)

## Tool Categories

| Category | Tools |
|----------|-------|
| Text Analysis | text_equal, text_count, text_measure, text_fingerprint, text_diff_explain, text_inspect, text_replace_check |
| Line/Range Operations | line_range_extract, line_range_compare |
| Patch Verification | patch_apply_check, patch_summary |
| Shell/Command | shell_split, shell_quote_join, argv_compare |
| Markdown/Structure | markdown_structure, code_fence_extract |
| Config Validation | dotenv_validate, ini_validate, validate_json, validate_toml |
| Path Operations | path_normalize, path_compare, path_scope_check |
| Unicode/Text Policy | unicode_policy_check, canonicalize_text |
| Identifier Analysis | identifier_inspect, identifier_table_inspect |
| Version Checking | version_constraint_check |
| Cargo Inspection | cargo_toml_inspect |
| Prompt Inspection | prompt_input_inspect |
| Math | math_eval |
| Regex | regex_test, regex_finditer |
| JSON | json_query, json_compare |
| Misc | glob_match, escape_text, unescape_text, hash_text |

## Key Design Principles

1. **Deterministic** - All tools produce consistent, reproducible results
2. **Side-effect-free** - No file I/O, network access, or filesystem inspection
3. **Machine-readable output** - Structured responses with findings envelope
4. **Tiered exposure** - Common tools discoverable, specialized tools opt-in

## Verification

- All 17 phases verified complete via systematic code review
- All tools have MCP exposure and tests
- Tool registry consistency verified via test_tool_inventory.py
- See git history for implementation details

(End of file - 1379 lines of detailed phase specifications removed as completed)