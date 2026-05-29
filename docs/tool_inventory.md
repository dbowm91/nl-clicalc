# MCP Tool Inventory

Canonical reference for all MCP tools exposed by `nl_calc.mcp.server.TOOL_HANDLERS`.

**Total: 55 tools**

## Inventory Table

| # | Tool Name | Category | Tier | Implemented | README | docs/mcp.md | Tests | Notes |
|---|-----------|----------|------|-------------|--------|-------------|-------|-------|
| 1 | `argv_compare` | shell | 2 | yes | no | yes | yes | Compare argv lists or command strings by parsed argv |
| 2 | `code_fence_extract` | markdown | 2 | yes | no | yes | yes | Extract fenced code blocks with line ranges and fingerprints |
| 3 | `constant_lookup` | math | 2 | yes | no | no | no | Physical constant lookup (avogadro, planck, etc.) |
| 4 | `dotenv_validate` | config | 2 | yes | no | yes | yes | Validate .env key=value text with duplicate and expansion detection |
| 5 | `escape_text` | text | 1 | yes | no | yes | yes | Escape text for various output formats |
| 6 | `glob_match` | path | 1 | yes | no | yes | yes | Match glob pattern against path |
| 7 | `identifier_analyze` | identifier | 3 | yes | no | yes | yes | Classify identifier naming conventions |
| 8 | `identifier_inspect` | identifier | 1 | yes | no | yes | yes | Detect confusables/collisions in identifiers |
| 9 | `ini_validate` | config | 2 | yes | no | yes | yes | Validate INI config with section and duplicate detection |
| 10 | `json_canonicalize` | json | 1 | yes | no | yes | yes | Deterministic JSON formatting with stable hashes |
| 11 | `json_compare` | json | 1 | yes | no | yes | yes | Semantic JSON comparison |
| 12 | `json_extract` | json | 2 | yes | no | yes | yes | JSON Pointer extraction (RFC 6901) |
| 13 | `json_query` | json | 1 | yes | no | yes | yes | JSON Pointer query (RFC 6901) |
| 14 | `json_shape` | json | 3 | yes | no | no | no | Analyze JSON structure without values |
| 15 | `line_range_compare` | text | 2 | yes | no | yes | yes | Compare line ranges from two texts |
| 16 | `line_range_extract` | text | 1 | yes | no | yes | yes | Extract line ranges with offsets and fingerprints |
| 17 | `list_compare` | list | 2 | yes | yes | yes | yes | List comparison (ordered/set/multiset) |
| 18 | `list_dedupe` | list | 1 | yes | no | yes | no | Deduplicate list with normalization support |
| 19 | `list_sort` | list | 1 | yes | no | yes | no | Sort list with normalization support |
| 20 | `markdown_structure` | markdown | 2 | yes | no | yes | yes | Markdown document structure analysis |
| 21 | `math_eval` | math | 0 | yes | yes | yes | yes | Evaluate math expressions with NL/unit support |
| 22 | `patch_apply_check` | patch | 2 | yes | no | yes | yes | Validate and simulate unified diff application |
| 23 | `patch_summary` | patch | 2 | yes | no | yes | yes | Summarize unified diff without applying |
| 24 | `path_analyze` | path | 2 | yes | no | yes | yes | Lexical path analysis (no filesystem) |
| 25 | `path_compare` | path | 2 | yes | no | yes | yes | Compare paths under normalization rules |
| 26 | `path_normalize` | path | 0 | yes | no | yes | yes | Normalize path with platform semantics |
| 27 | `path_scope_check` | path | 2 | yes | no | yes | yes | Lexical scope check (no symlink resolution) |
| 28 | `regex_finditer` | regex | 1 | yes | no | no | yes | Find all regex matches with positions |
| 29 | `regex_safety_check` | regex | 1 | yes | no | no | yes | Check regex for catastrophic backtracking |
| 30 | `shell_quote_join` | shell | 2 | yes | no | yes | yes | Safely quote argv tokens into shell string |
| 31 | `shell_split` | shell | 2 | yes | no | yes | yes | Parse shell command into argv with risk detection |
| 32 | `text_count` | text | 0 | yes | yes | yes | yes | Character counting and frequency table |
| 33 | `text_diff_explain` | text | 1 | yes | yes | yes | no | Explain string differences with codepoints |
| 34 | `text_equal` | text | 0 | yes | yes | yes | yes | String comparison with normalization modes |
| 35 | `text_fingerprint` | text | 0 | yes | no | yes | yes | Deterministic SHA-256 fingerprint |
| 36 | `text_hash` | text | 2 | yes | no | yes | yes | Cryptographic hash computation |
| 37 | `text_inspect` | text | 1 | yes | yes | yes | no | Hidden characters, confusables, mixed scripts |
| 38 | `text_measure` | text | 0 | yes | yes | yes | yes | Comprehensive text metrics |
| 39 | `text_position` | text | 2 | yes | no | yes | yes | Position conversion (byte/cp/line/UTF-16) |
| 40 | `text_replace_check` | text | 1 | yes | no | yes | yes | Pre-edit replacement safety check |
| 41 | `text_truncate` | text | 3 | yes | no | yes | yes | Grapheme-aware truncation |
| 42 | `text_transform` | text | 2 | yes | no | yes | yes | Unicode normalization, casefold, trim, etc. |
| 43 | `text_window` | text | 1 | yes | no | yes | yes | Context window around a text position |
| 44 | `toml_shape` | toml | 2 | yes | no | yes | no | TOML structure analysis |
| 45 | `unit_convert` | math | 2 | yes | no | no | no | Unit conversion with factors |
| 46 | `unit_info` | math | 2 | yes | no | no | no | Unit metadata (canonical, category) |
| 47 | `unescape_text` | text | 1 | yes | no | yes | yes | Unescape text from various formats |
| 48 | `validate_brackets` | validation | 1 | yes | yes | yes | yes | Bracket balance checking |
| 49 | `validate_json` | validation | 0 | yes | yes | yes | yes | JSON parsing validation |
| 50 | `validate_regex` | regex | 1 | yes | yes | yes | yes | Regex pattern testing against samples |
| 51 | `validate_schema_light` | validation | 3 | yes | no | yes | yes | Light JSON schema validation |
| 52 | `validate_toml` | validation | 1 | yes | no | yes | yes | TOML parsing validation |
| 53 | `version_compare` | version | 2 | yes | no | yes | no | Version string comparison (semver/pep440/loose) |
| 54 | `unicode_policy_check` | unicode | 2 | yes | no | yes | yes | Apply named Unicode safety policy to text |
| 55 | `canonicalize_text` | unicode | 2 | yes | no | yes | yes | Apply named text canonicalization profile |

## Legend

- **Tier 0**: Ultra-common, small-schema tools - always available
- **Tier 1**: Default coding-agent sanity tools - low context, recommended default
- **Tier 2**: Heavier analysis tools - moderate context, opt-in for text/unicode/config work
- **Tier 3**: Domain-specific tools - more context, opt-in for specialized workflows

## Summary Statistics

| Field | Count |
|-------|-------|
| Total tools | 55 |
| Documented in README | 10 |
| Documented in docs/mcp.md | 49 |
| Missing from docs/mcp.md | 3 (`constant_lookup`, `json_shape`, `unit_convert`) |
| Have tests | 49 |
| Missing tests | 3 (`constant_lookup`, `list_dedupe`, `list_sort`) |

## Category Breakdown

| Category | Tools |
|----------|-------|
| config | `dotenv_validate`, `ini_validate` |
| math | `math_eval`, `unit_convert`, `unit_info`, `constant_lookup` |
| patch | `patch_apply_check`, `patch_summary` |
| text | `text_measure`, `text_equal`, `text_diff_explain`, `text_inspect`, `text_count`, `text_truncate`, `text_transform`, `text_position`, `text_hash`, `text_window`, `text_fingerprint`, `escape_text`, `unescape_text`, `text_replace_check`, `line_range_extract`, `line_range_compare` |
| json | `json_compare`, `json_extract`, `json_shape`, `json_canonicalize`, `json_query` |
| validation | `validate_brackets`, `validate_json`, `validate_regex`, `validate_toml`, `validate_schema_light` |
| regex | `regex_finditer`, `regex_safety_check` |
| list | `list_compare`, `list_dedupe`, `list_sort` |
| path | `path_normalize`, `path_analyze`, `path_compare`, `path_scope_check`, `glob_match` |
| identifier | `identifier_analyze`, `identifier_inspect` |
| shell | `shell_split`, `shell_quote_join`, `argv_compare` |
| markdown | `markdown_structure`, `code_fence_extract` |
| version | `version_compare` |
| toml | `toml_shape` |
| unicode | `unicode_policy_check`, `canonicalize_text` |

## Source of Truth

The canonical tool list lives in `tests/fixtures/mcp_tool_registry_expected.json`.
The test at `tests/test_tool_inventory.py` enforces that `TOOL_HANDLERS` keys match this fixture.
