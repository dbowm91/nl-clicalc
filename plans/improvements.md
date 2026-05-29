# Eggsact / nl-clicalc MCP Expansion Plan

## Status: PARTIALLY COMPLETED (2026-05-29)

### Completed Phases (13 of 17)

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Inventory and Documentation Consistency | ✅ Completed |
| 2 | Response Envelope Finding Metadata | ✅ Completed |
| 3 | Text Replacement and Line-Range Tools | ✅ Completed |
| 4 | Patch Applicability Tools | ✅ Completed |
| 5 | Shell and Command String Sanity Tools | ✅ Completed |
| 6 | Markdown and Code Fence Structure Tools | ✅ Completed |
| 7 | .env and INI Config Validation | ✅ Completed |
| 8 | Path and Scope Checks | ✅ Completed |
| 9 | Unicode Policy Presets and Canonicalization | ✅ Completed |
| 14 | Tiering and MCP Exposure Cleanup | ✅ Completed |
| 15 | Test Corpus and Golden Fixtures | ✅ Completed |
| 16 | Human-Facing CLI Improvements | ✅ Completed |
| 17 | Codegg Integration Guidance | ✅ Completed |

### Deferred Phases (4 of 17)

| Phase | Description | Status |
|-------|-------------|--------|
| 10 | Identifier Table and Symbol Collision | ⏳ Deferred |
| 11 | Version Constraint Checks | ⏳ Deferred |
| 12 | Rust/Cargo-Specific Inspection | ⏳ Deferred |
| 13 | Prompt/Input Inspection | ⏳ Deferred |

### Implementation Summary

- **55 MCP tools** (up from 39 originally)
- **6 new CLI commands** (replace-check, lines, patch-check, shell-split, md-structure, dotenv-check)
- **1016 tests passing** (up from 631 originally)
- **17 fixture files** with 117 test cases
- **Consistent documentation** across README, docs/mcp.md, and docs/tool_inventory.md
- **Structured findings envelope** for machine-readable results
- **Tiered tool exposure** with 5 named profiles

## Purpose

This plan converts the current `nl-clicalc` MCP server into a more complete reference implementation for `eggsact`, the deterministic exactness/sanity-check substrate intended for use by `codegg` and other coding agents.

The main objective is not to expand the calculator feature set. The objective is to strengthen the MCP server around deterministic operations that LLMs frequently perform poorly: exact string comparison, Unicode inspection, text replacement, line/offset accounting, patch applicability, structured config validation, shell quoting, path normalization, identifier analysis, and small structured diffs.

This plan is written for a smaller implementation model. Prefer conservative, incremental changes with tests after each phase. Avoid broad rewrites unless explicitly called out.

## Working Assumptions

The current repository is `dbowm91/nl-clicalc`.

The current Python implementation already contains:

- Calculator and unit conversion functionality.
- MCP stdio server support.
- Deterministic text tools such as equality, counting, diff explanation, Unicode/confusable inspection, text measurement, and text transforms.
- Structured tools for JSON, TOML, regex, list comparison, path handling, identifier inspection, hashing/fingerprinting, and version comparison.
- Documentation in `README.md`, `docs/mcp.md`, and `docs/exact.md`.

The future Rust crate is expected to be named `eggsact`, but this plan targets the current Python reference codebase unless otherwise noted.

## Design Principles

Keep every tool deterministic and side-effect-free unless the repository already has an explicit safe exception. MCP tools should not read or write arbitrary files, execute shell commands, inspect the live filesystem, or access the network.

Prefer exact, machine-readable outputs over prose. Human-readable summaries are useful, but every finding should have structured fields that `codegg` can consume.

Preserve the existing response envelope style: `ok`, `tool`, `result`, `warnings`, and `limits_applied`. Add richer error/finding metadata where useful, but do not break existing callers unless there is a planned compatibility update.

Prefer small composable primitives over large semantic classifiers. For example, do not implement a general “prompt injection detector.” Instead implement deterministic scanners for hidden Markdown links, HTML comments, bidi controls, zero-width characters, ANSI escapes, suspicious literal phrases, and oversized encoded blobs.

Avoid context pollution in MCP descriptions. Tool names and schemas should be concise. Use tiered exposure so common tools stay discoverable and specialized tools remain opt-in.

## Phase 1: Inventory and Documentation Consistency

### Goal

Make the repository self-consistent before adding new tools. The README, MCP docs, exact docs, tool registry, and tests should agree on what tools exist and what each one returns.

### Tasks

1. Inspect the actual MCP tool registry and implementation.

   Likely files to inspect:

   - `nl_calc/mcp/tools.py`
   - `nl_calc/mcp/server.py`
   - `nl_calc/exact.py` or equivalent exact/text modules
   - `README.md`
   - `docs/mcp.md`
   - `docs/exact.md`
   - existing tests under `tests/`

2. Create a tool inventory table.

   Include these fields:

   - Tool name
   - Category
   - Tier, if currently assigned
   - Implemented: yes/no
   - Documented in README: yes/no
   - Documented in `docs/mcp.md`: yes/no
   - Has tests: yes/no
   - Notes on mismatch or ambiguity

   Suggested output path:

   - `docs/tool_inventory.md`

3. Reconcile obvious documentation drift.

   The README currently appears to describe a smaller MCP surface than `docs/mcp.md`. Update the README to describe the MCP server at a high level and point to `docs/mcp.md` for the full table. Avoid duplicating long tool tables in multiple places unless there is a generation mechanism.

4. Add or update a schema/docs consistency test.

   The test should fail if documented MCP tool names diverge from the actual registry. If exact parsing of docs is too brittle, create a small generated or manually maintained canonical list, such as:

   - `docs/mcp_tool_registry.json`
   - or `tests/fixtures/mcp_tool_registry_expected.json`

   Then test that the runtime registry matches the canonical list.

### Acceptance Criteria

- `README.md` no longer contradicts `docs/mcp.md` about the MCP tool surface.
- A human can inspect `docs/tool_inventory.md` and see the status of every MCP tool.
- A test fails if a tool is added to the registry without documentation or added to docs without implementation.
- Existing tests still pass.

## Phase 2: Response Envelope and Finding Metadata

### Goal

Standardize outputs so that `codegg` and future `eggsact` callers can consume results predictably.

### Tasks

1. Review all MCP tool return shapes.

   Identify tools that return ad hoc structures or inconsistent warning/error fields.

2. Define a shared finding shape for deterministic scanners.

   Recommended shape:

   ```json
   {
     "code": "ZERO_WIDTH_CHAR",
     "severity": "warn",
     "message": "Zero-width character found",
     "span": {
       "byte_start": 12,
       "byte_end": 15,
       "char_start": 10,
       "char_end": 11,
       "line": 1,
       "column": 11
     },
     "details": {}
   }
   ```

   Severity values should be conservative:

   - `info`
   - `warn`
   - `error`

3. Add optional fields to the common envelope where appropriate:

   - `findings`: structured list of issues or observations
   - `machine_code`: stable error or result code
   - `recommended_next_tool`: optional string or list of strings

4. Do not force every existing tool to use `findings` immediately. Start with new tools and high-value existing scanners such as Unicode inspection, regex safety, JSON validation, path analysis, and identifier inspection.

### Acceptance Criteria

- New tools introduced in later phases use a consistent `findings` structure.
- Existing callers are not broken by envelope changes.
- Tests cover at least one successful result, one warning/finding result, and one parse/error result using the shared shape.

## Phase 3: Text Replacement and Line-Range Tools

### Goal

Add deterministic tools for exact edit verification. These are high-value for coding agents because they prevent hallucinated replacements, duplicate-match edits, and line-number drift.

### Tool: `text_replace_check`

#### Purpose

Check whether a replacement would apply cleanly before an agent attempts to edit text.

#### Inputs

- `text`: source text
- `old`: text to find
- `new`: replacement text
- `mode`: optional, default `exact`
  - `exact`
  - `nfc`
  - `nfkc`
  - `casefold`
  - `whitespace_collapse`
- `expected_count`: optional integer
- `allow_multiple`: optional boolean, default false
- `newline_policy`: optional
  - `preserve`
  - `normalize_lf`
  - `normalize_crlf`
- `return_preview`: optional boolean, default false
- `max_preview_chars`: optional integer with safe cap

#### Output

Recommended result fields:

- `match_count`
- `unique_match`
- `expected_count_met`
- `would_change`
- `positions`
  - byte offsets
  - character offsets
  - line/column positions
- `changed_text_fingerprint`
- `newline_style_before`
- `newline_style_after`
- `preview_before`, optional bounded
- `preview_after`, optional bounded
- `findings`

#### Behavior

- If `allow_multiple` is false and more than one match exists, return `ok: true` but include a warning/finding that the replacement is ambiguous.
- If no match exists, return `ok: true`, `would_change: false`, and include a finding.
- Do not return full changed text by default.
- Respect existing input-size limits.

### Tool: `line_range_extract`

#### Purpose

Extract exact line ranges and return stable offsets/fingerprints.

#### Inputs

- `text`
- `start_line`
- `end_line`
- `line_base`: optional, default `1`
- `include_line_numbers`: optional boolean
- `include_fingerprint`: optional boolean, default true

#### Output

- `line_count_total`
- `start_line`
- `end_line`
- `valid_range`
- `text`
- `lines`, optional structured list
- `byte_start`
- `byte_end`
- `char_start`
- `char_end`
- `newline_style`
- `ends_with_newline`
- `fingerprint`
- `findings`

### Tool: `line_range_compare`

#### Purpose

Compare a line range from two text inputs.

#### Inputs

- `left_text`
- `right_text`
- `start_line`
- `end_line`
- `line_base`: optional
- `comparison_mode`: optional
  - `exact`
  - `ignore_trailing_whitespace`
  - `normalize_newlines`

#### Output

- `equal`
- `left_fingerprint`
- `right_fingerprint`
- `diff_summary`
- `first_difference`, if any

### Tests

Add tests for:

- No replacement match.
- Exactly one replacement match.
- Multiple replacement matches with `allow_multiple=false`.
- Unicode-normalized match.
- CRLF versus LF handling.
- Valid line range extraction.
- Out-of-range line extraction.
- Line range comparison with newline normalization.

### Acceptance Criteria

- Tools are exposed through MCP.
- Tools are documented in `docs/mcp.md`.
- Tests pass for replacement ambiguity, no-match, exact-match, and line-range edge cases.

## Phase 4: Patch Applicability Tools

### Goal

Allow an agent to verify whether a generated unified diff or hunk-like patch applies to a given source string without touching the filesystem.

### Tool: `patch_apply_check`

#### Purpose

Validate and simulate a unified diff against provided in-memory files/text.

#### Inputs

Initial minimal version:

- `original_text`
- `patch_text`
- `strict`: optional boolean, default true
- `return_result_fingerprint`: optional boolean, default true
- `return_result_text`: optional boolean, default false, with strict size cap

Future version may support multiple files as:

```json
{
  "files": [
    {"path": "src/lib.rs", "original_text": "..."}
  ],
  "patch_text": "..."
}
```

For the first implementation, single-text support is acceptable.

#### Output

- `patch_parse_ok`
- `applies`
- `hunks_total`
- `hunks_applied`
- `hunks_failed`
- `failed_hunks`
- `affected_line_ranges`
- `newline_style_before`
- `newline_style_after`
- `result_fingerprint`
- `result_text`, optional bounded
- `findings`

#### Behavior

- Parse standard unified diff hunks.
- Report hunk failure with expected context and actual nearby context when bounded.
- Do not modify files.
- Do not execute commands.
- Apply strict input caps.

### Tool: `patch_summary`

#### Purpose

Summarize a unified diff without applying it.

#### Inputs

- `patch_text`

#### Output

- `files_changed`
- `hunks_total`
- `additions`
- `deletions`
- `renames_detected`, if detectable
- `binary_patch_detected`
- `line_ranges_by_file`
- `findings`

### Tests

Add fixtures for:

- Valid one-hunk patch.
- Patch with wrong context.
- Multiple hunks.
- CRLF/LF behavior.
- Empty patch.
- Malformed patch.

### Acceptance Criteria

- `patch_apply_check` can verify a simple unified diff against a string.
- Failure output is specific enough for an agent to repair the patch.
- Tool remains side-effect-free.

## Phase 5: Shell and Command String Sanity Tools

### Goal

Add lexical shell/argv tools for command sanity checking without execution.

### Tool: `shell_split`

#### Purpose

Parse a shell-like command string into argv and report risky lexical features.

#### Inputs

- `command`
- `shell`: optional, default `posix`
  - initially only `posix` is required
- `detect_risky_features`: optional boolean, default true

#### Output

- `parse_ok`
- `argv`
- `argc`
- `features`
  - `has_pipe`
  - `has_redirection`
  - `has_command_substitution`
  - `has_variable_expansion`
  - `has_glob_pattern`
  - `has_control_operator`
  - `has_unbalanced_quotes`
- `findings`

#### Implementation Notes

Python can use `shlex` for the first version. Be explicit that this is lexical POSIX-like parsing, not full shell evaluation.

### Tool: `shell_quote_join`

#### Purpose

Safely quote a list of argv tokens into a POSIX-like shell string.

#### Inputs

- `argv`: list of strings
- `shell`: optional, default `posix`

#### Output

- `command`
- `roundtrip_ok`
- `findings`

### Tool: `argv_compare`

#### Purpose

Compare two command strings or argv lists by parsed argv rather than raw text.

#### Inputs

- `left_command` or `left_argv`
- `right_command` or `right_argv`
- `shell`: optional

#### Output

- `argv_equal`
- `left_argv`
- `right_argv`
- `first_difference`
- `findings`

### Tests

Add tests for:

- Simple command splitting.
- Quoted spaces.
- Unbalanced quotes.
- Command substitution detection.
- Redirection and pipe detection.
- Round-trip quote/join.
- `cargo test -- --nocapture` parsing.

### Acceptance Criteria

- No command is executed.
- Tool output clearly distinguishes parse failure from risky-but-parseable features.
- Docs explicitly say this is lexical, not a security sandbox.

## Phase 6: Markdown and Code Fence Structure Tools

### Goal

Help agents and humans reason about Markdown boundaries, code fences, links, comments, and hidden prompt content.

### Tool: `markdown_structure`

#### Purpose

Parse Markdown enough to report document structure and risky or confusing constructs.

#### Inputs

- `text`
- `include_sections`: optional boolean, default true
- `include_links`: optional boolean, default true
- `include_code_fences`: optional boolean, default true
- `include_html_comments`: optional boolean, default true

#### Output

- `headings`
  - level
  - text
  - line
  - slug, if easy
- `code_fences`
  - language
  - start_line
  - end_line
  - closed
- `links`
  - visible_text
  - target
  - line
  - mismatch_flags
- `html_comments`
- `frontmatter`
  - present
  - format guess: yaml/toml/json/unknown
  - line range
- `tables_detected`
- `findings`

#### Behavior

This does not need to be a full CommonMark parser for the first implementation. A deterministic line scanner is acceptable if documented.

### Tool: `code_fence_extract`

#### Purpose

Extract fenced code blocks with exact line ranges and fingerprints.

#### Inputs

- `text`
- `language`: optional filter
- `include_content`: optional boolean, default true with cap

#### Output

- `blocks`
  - `index`
  - `language`
  - `start_line`
  - `end_line`
  - `closed`
  - `content`
  - `fingerprint`
- `unclosed_fences`
- `findings`

### Tests

Add tests for:

- Multiple code fences.
- Unclosed code fence.
- HTML comments.
- Markdown link where visible URL and href differ.
- Frontmatter detection.

### Acceptance Criteria

- Agents can determine whether a requested code block exists and where it is.
- Unclosed fences are reported deterministically.
- Hidden HTML comments are surfaced.

## Phase 7: `.env`, INI, and Small Config Validation

### Goal

Add deterministic validation for common human and agent-generated config snippets.

### Tool: `dotenv_validate`

#### Purpose

Validate `.env`-style key/value text.

#### Inputs

- `text`
- `allow_export`: optional boolean, default true
- `key_pattern`: optional string, default POSIX-ish identifier pattern
- `duplicate_policy`: optional
  - `warn`
  - `error`
  - `allow`

#### Output

- `parse_ok`
- `entries`
  - key
  - value_present
  - quote_style
  - line
- `duplicates`
- `invalid_lines`
- `requires_quoting`
- `contains_expansion_syntax`
- `findings`

### Tool: `ini_validate`

#### Purpose

Validate simple INI-style config.

#### Inputs

- `text`
- `duplicate_policy`: optional

#### Output

- `parse_ok`
- `sections`
- `keys_by_section`
- `duplicates`
- `invalid_lines`
- `findings`

### Tests

Add tests for:

- Duplicate `.env` keys.
- Invalid key names.
- Quoted values.
- Empty values.
- `export KEY=value`.
- INI duplicate sections or keys.

### Acceptance Criteria

- Tools do not attempt to evaluate variable expansion.
- Duplicate keys are reported with line numbers.
- Hidden Unicode in keys is surfaced through findings or reuse of existing text inspection primitives.

## Phase 8: Path and Scope Checks

### Goal

Strengthen lexical path tools for safe agent workflows.

### Tool: `path_compare`

#### Purpose

Compare paths under explicit normalization rules.

#### Inputs

- `left`
- `right`
- `platform`: optional
  - `posix`
  - `windows`
- `case_sensitive`: optional boolean
- `normalize_separators`: optional boolean, default true
- `collapse_dot_segments`: optional boolean, default true

#### Output

- `equal`
- `left_normalized`
- `right_normalized`
- `differences`
- `findings`

### Tool: `path_scope_check`

#### Purpose

Determine whether a target path remains lexically inside a declared root.

#### Inputs

- `root`
- `target`
- `platform`: optional
- `case_sensitive`: optional

#### Output

- `inside_root`
- `root_normalized`
- `target_normalized`
- `relative_path`
- `escapes_via_dotdot`
- `absolute_target`
- `findings`

#### Behavior

This must be lexical only. Do not resolve symlinks. Document that symlink-safe enforcement requires filesystem-aware checks outside this tool.

### Tests

Add tests for:

- `../` traversal.
- Absolute target path.
- Windows separator handling.
- Case-sensitive and case-insensitive comparisons.
- Trailing slash normalization.

### Acceptance Criteria

- Tool helps detect lexical path traversal.
- Docs clearly state that symlink resolution is out of scope.

## Phase 9: Unicode Policy Presets and Canonicalization Profiles

### Goal

Make existing Unicode/text functionality easier for agents to use correctly.

### Tool: `unicode_policy_check`

#### Purpose

Apply a named deterministic Unicode safety policy to input text.

#### Inputs

- `text`
- `policy`
  - `identifier_strict`
  - `filename_safe`
  - `source_code`
  - `human_text`
  - `json_key`
  - `domain_like`
- `normalization`: optional, default policy-specific

#### Output

- `pass`
- `policy`
- `normalized_form`
- `findings`
- `summary`

#### Policy Suggestions

`identifier_strict` should warn/fail on:

- mixed scripts
- bidi controls
- zero-width characters
- confusables
- normalization instability

`filename_safe` should warn/fail on:

- control characters
- path separators
- bidi controls
- zero-width characters
- reserved Windows names if platform is windows or generic-safe

`human_text` should be less strict and primarily warn.

### Tool: `canonicalize_text`

#### Purpose

Apply a named text canonicalization profile.

#### Inputs

- `text`
- `profile`
  - `source_file_identity`
  - `identifier_compare`
  - `human_label_compare`
  - `json_key_compare`
  - `path_segment_compare`
- `return_mapping`: optional boolean, default false

#### Output

- `text`
- `changed`
- `operations_applied`
- `fingerprint_before`
- `fingerprint_after`
- `mapping`, optional if feasible
- `findings`

### Tests

Add tests for:

- NFC/NFD equivalent strings.
- Zero-width characters.
- Bidi controls.
- Mixed-script identifiers.
- Human label whitespace collapse.

### Acceptance Criteria

- Policies are documented as deterministic heuristics, not semantic security guarantees.
- Agents can select a profile without manually specifying many low-level normalization flags.

## Phase 10: Identifier Table and Symbol Collision Analysis

### Goal

Extend single-identifier analysis into multi-symbol collision detection for generated code and refactors.

### Tool: `identifier_table_inspect`

#### Purpose

Analyze a list of identifiers for collisions and suspicious near-collisions.

#### Inputs

```json
{
  "identifiers": [
    {"name": "user_id", "kind": "variable", "file": "src/lib.rs", "line": 10},
    {"name": "userID", "kind": "variable", "file": "src/lib.rs", "line": 20}
  ],
  "language": "rust",
  "checks": ["casefold", "normalization", "style", "confusable"]
}
```

Fields other than `name` should be optional.

#### Output

- `count`
- `collisions`
  - type: `casefold`, `normalization`, `confusable`, `style_variant`, etc.
  - identifiers involved
- `reserved_keyword_hits`
- `mixed_style_groups`
- `findings`

### Tests

Add tests for:

- Casefold collision.
- NFC/NFD collision.
- Snake-case/camel-case near collision.
- Rust keyword conflict.

### Acceptance Criteria

- Single identifier tools remain simple.
- Table-level analysis is opt-in and documented as a heavier Tier 2 or Tier 3 tool.

## Phase 11: Version Constraint Checks

### Goal

Improve deterministic version reasoning for package/config work.

### Tool: `version_constraint_check`

#### Purpose

Check whether a version satisfies a constraint under a declared versioning scheme.

#### Inputs

- `version`
- `constraint`
- `scheme`
  - `semver`
  - `cargo`
  - optional future: `pep440`, `npm`

#### Output

- `satisfies`
- `parsed_version`
- `parsed_constraint`
- `scheme`
- `explanation`
- `findings`

### Initial Scope

Implement strict SemVer first. Cargo-style caret, tilde, wildcard, comparison, and comma constraints can follow if manageable.

Examples to support eventually:

- `^1.2.3`
- `~1.2`
- `>=1.2,<2.0`
- `1.*`
- `=1.2.3`
- pre-release comparisons

### Tests

Add tests for:

- Exact version match.
- Greater-than/less-than ranges.
- Pre-release ordering.
- Cargo caret behavior if implemented.

### Acceptance Criteria

- Tool is explicit about unsupported constraint forms.
- Unsupported forms return structured parse findings, not vague failures.

## Phase 12: Rust/Cargo-Specific Inspection

### Goal

Add a small deterministic Rust project config helper, useful for `codegg` and the future Rust `eggsact` crate.

### Tool: `cargo_toml_inspect`

#### Purpose

Inspect `Cargo.toml` text without network or filesystem access.

#### Inputs

- `text`
- `check_workspace`: optional boolean, default true
- `check_dependencies`: optional boolean, default true

#### Output

- `parse_ok`
- `package`
  - name
  - version
  - edition
  - license
  - repository
  - readme
- `workspace`
  - present
  - members
  - exclude
- `dependencies`
  - by section: dependencies, dev-dependencies, build-dependencies, target-specific dependencies
  - dependency form: version/path/git/workspace/inline-table
- `path_dependencies`
- `suspicious_dependency_names`
- `duplicate_or_confusable_dependency_names`
- `findings`

#### Behavior

- Use existing TOML parsing support.
- Do not resolve paths against filesystem.
- Use lexical path checks for path dependencies where possible.

### Tests

Add tests for:

- Basic package metadata.
- Workspace members.
- Path dependency.
- Git dependency.
- Missing edition.
- Confusable or duplicate dependency names if existing Unicode tools make this easy.

### Acceptance Criteria

- Tool can summarize a `Cargo.toml` for agent planning.
- No dependency resolution or network access is attempted.

## Phase 13: Prompt/Input Inspection for Humans and Agents

### Goal

Add a deterministic scanner for hidden or misleading content in user-pasted input, repository docs, issue bodies, and prompt-like text.

### Tool: `prompt_input_inspect`

#### Purpose

Surface deterministic red flags in text that may influence agents or humans unexpectedly.

#### Inputs

- `text`
- `checks`: optional list
  - `unicode_hidden`
  - `bidi`
  - `html_comments`
  - `markdown_links`
  - `ansi_escapes`
  - `terminal_controls`
  - `base64_like_blobs`
  - `instruction_phrases`
  - `long_minified_lines`
- `phrase_patterns`: optional list of literal strings or safe regexes

#### Output

- `findings`
- `summary`
- `risk_score`: optional simple deterministic score, if desired
- `recommended_next_tool`

#### Behavior

- Do not call this a definitive prompt-injection detector.
- Do not infer intent.
- Report observable features only.

### Tests

Add tests for:

- HTML comments with hidden instructions.
- Markdown link text/target mismatch.
- ANSI escape sequence.
- Zero-width and bidi control characters.
- Very long base64-like blob.

### Acceptance Criteria

- Tool helps humans and agents notice hidden content.
- Docs explicitly describe it as deterministic inspection, not semantic classification.

## Phase 14: Tiering and MCP Exposure Cleanup

### Goal

Make the MCP surface useful without overwhelming agent context.

### Proposed Tiers

#### Tier 0: Ultra-common, small-schema tools

These should be cheap to expose by default.

- `text_equal`
- `text_count`
- `text_measure` or `text_measure_summary`
- `text_fingerprint`
- `validate_json`
- `math_eval`
- `path_normalize`

#### Tier 1: Default coding-agent sanity tools

- `text_diff_explain`
- `text_inspect` summary mode
- `text_replace_check`
- `line_range_extract`
- `json_query`
- `json_compare`
- `validate_toml`
- `glob_match`
- `regex_finditer` or `regex_test`
- `identifier_inspect`
- `escape_text`
- `unescape_text`

#### Tier 2: Heavier analysis tools

- full `text_inspect`
- `patch_apply_check`
- `patch_summary`
- `markdown_structure`
- `code_fence_extract`
- `identifier_table_inspect`
- `shell_split`
- `shell_quote_join`
- `argv_compare`
- `unicode_policy_check`
- `canonicalize_text`
- `dotenv_validate`
- `ini_validate`
- `path_scope_check`
- `path_compare`

#### Tier 3: Domain-specific tools

- `cargo_toml_inspect`
- `version_constraint_check`
- future package-manager helpers
- future lockfile shape tools

### Tasks

1. Check whether the existing MCP server has tier filtering.
2. If yes, update tier metadata.
3. If no, add a simple metadata field per tool and expose docs by tier.
4. Keep default exposure conservative.
5. Add a docs section explaining recommended profiles:

   - `minimal`
   - `coding-agent-default`
   - `text-unicode-heavy`
   - `config-heavy`
   - `rust-project`

### Acceptance Criteria

- Agents can be configured with a smaller default tool set.
- Specialized tools do not pollute the default schema unless explicitly enabled.
- Docs explain which profile `codegg` should use by default.

## Phase 15: Test Corpus and Golden Fixtures

### Goal

Create a durable adversarial fixture corpus for deterministic exactness behavior.

### Suggested Fixture Directory

- `tests/fixtures/exact/`
- `tests/fixtures/unicode/`
- `tests/fixtures/patches/`
- `tests/fixtures/markdown/`
- `tests/fixtures/config/`
- `tests/fixtures/paths/`
- `tests/fixtures/shell/`

### Required Fixture Categories

Unicode/text:

- NFC vs NFD equivalents.
- NFKC-changing characters.
- Zero-width joiner/non-joiner.
- Bidi override/control characters.
- Mixed-script identifiers.
- Confusable identifiers.
- CRLF vs LF.
- Trailing whitespace-only differences.

Patch:

- Valid unified diff.
- Wrong context.
- Malformed hunk header.
- Multiple hunks.
- Final newline change.

Markdown:

- Unclosed code fence.
- HTML comment.
- Link text/target mismatch.
- YAML/TOML frontmatter.

Config:

- Duplicate `.env` key.
- Invalid `.env` key.
- Quoted `.env` value.
- INI duplicate key.
- Invalid TOML.

Path:

- Dot-dot traversal.
- Absolute target.
- Windows separator variants.
- Case sensitivity examples.

Shell:

- Quoted spaces.
- Unbalanced quotes.
- Command substitution.
- Redirection.
- Pipeline.

### Acceptance Criteria

- New tools have golden tests against fixtures.
- Edge cases are easy to port later into Rust `eggsact`.
- Fixture names clearly describe the behavior being tested.

## Phase 16: Human-Facing CLI Improvements

### Goal

Make the same deterministic tools useful to humans, not just MCP agents.

### Tasks

1. Add concise CLI commands or subcommands for the highest-value new tools, if the current CLI architecture makes this easy.

   Suggested commands:

   - `nl-calc inspect-input`
   - `nl-calc replace-check`
   - `nl-calc lines`
   - `nl-calc patch-check`
   - `nl-calc shell-split`
   - `nl-calc md-structure`
   - `nl-calc dotenv-check`

2. Support JSON output where practical.

   Recommended flag:

   - `--json`

3. Provide compact human-readable summaries by default.

   Examples:

   - “Replacement is ambiguous: 3 matches found.”
   - “Path escapes root lexically via `..`.”
   - “Markdown contains 1 unclosed code fence.”
   - “Command contains command substitution and redirection.”

### Acceptance Criteria

- Humans can use at least the most important new tools without invoking MCP directly.
- CLI output remains compact.
- JSON output is available for scripts.

## Phase 17: Codegg Integration Guidance

### Goal

Document how `codegg` should use `eggsact`/`nl-clicalc` as deterministic middleware, not only as optional model-invoked MCP tools.

### Suggested Document

Create:

- `docs/codegg_integration.md`

### Content to Include

Recommended automatic preflight checks:

1. Before applying model-generated edits:

   - `text_replace_check`
   - `patch_apply_check`
   - `line_range_extract`

2. Before executing user-approved shell commands:

   - `shell_split`
   - optional policy-specific findings review

3. Before accepting generated config:

   - `validate_json`
   - `validate_toml`
   - `dotenv_validate`
   - `ini_validate`

4. Before resolving paths from model output:

   - `path_normalize`
   - `path_scope_check`

5. Before trusting pasted prompt/repo content:

   - `prompt_input_inspect`
   - `unicode_policy_check`
   - `markdown_structure`

6. Before large refactors:

   - `identifier_table_inspect`
   - `text_fingerprint`

Explain that agent-initiated MCP calls are helpful, but harness-level automatic checks are more reliable because models may underuse tools.

### Acceptance Criteria

- `docs/codegg_integration.md` gives concrete examples of when to call deterministic tools.
- The document distinguishes MCP exposure from internal middleware use.

## Suggested Implementation Order

For a smaller model, implement in this order:

1. Phase 1: inventory and docs consistency. ✅
2. Phase 3: `text_replace_check` and `line_range_extract`. ✅
3. Phase 15: initial fixtures for text and line tools. ✅
4. Phase 8: `path_scope_check` and `path_compare`. ✅
5. Phase 5: `shell_split` and `shell_quote_join`. ✅
6. Phase 6: `markdown_structure` and `code_fence_extract`. ✅
7. Phase 7: `dotenv_validate`. ✅
8. Phase 4: `patch_apply_check` and `patch_summary`. ✅
9. Phase 9: `unicode_policy_check` and `canonicalize_text`. ✅
10. Phase 14: tier cleanup. ✅
11. Phase 17: `codegg` integration docs. ✅
12. Later: `identifier_table_inspect`, `version_constraint_check`, and `cargo_toml_inspect`. ⏳ Deferred

This order front-loads tools with the best ratio of implementation effort to agent usefulness.

### Additional Completed Phases

- Phase 2: Response Envelope Finding Metadata ✅
- Phase 16: Human-Facing CLI Improvements ✅

## Non-Goals

Do not add network access.

Do not execute shell commands.

Do not inspect the live filesystem from MCP tools unless a separate explicitly sandboxed design is approved.

Do not build a semantic prompt-injection classifier.

Do not add broad symbolic mathematics, matrix algebra, plotting, or statistics unless separately requested.

Do not make YAML a hard requirement unless dependency policy is decided. `.env`, INI, JSON, and TOML are sufficient for the near-term coding-agent use case.

Do not make tool descriptions verbose by default. Long descriptions belong in documentation, not necessarily in MCP schemas.

## Definition of Done

The plan is complete when:

- ✅ Documentation and actual MCP registry are consistent.
- ✅ New deterministic tools exist for replacement checking, line extraction, patch checking, shell lexing, Markdown/code-fence structure, config validation, path scoping, Unicode policies, and canonicalization profiles.
- ✅ Each new tool has deterministic tests and fixture coverage.
- ✅ Outputs follow a consistent structured envelope.
- ✅ Tool tiering is documented and usable.
- ✅ Human-facing CLI affordances exist for the highest-value checks or are explicitly deferred.
- ✅ `docs/codegg_integration.md` explains how to use these tools as automatic middleware and as model-invoked MCP tools.

### Remaining Items (Deferred)

- `identifier_table_inspect` tool (Phase 10)
- `version_constraint_check` tool (Phase 11)
- `cargo_toml_inspect` tool (Phase 12)
- `prompt_input_inspect` tool (Phase 13)

## Final Notes for the Implementing Model

Prefer small pull-request-sized changes. After each tool, add tests and documentation before moving to the next tool.

When uncertain, implement the narrower deterministic version rather than a broad semantic version.

For every new tool, ask:

1. Is it deterministic?
2. Is it side-effect-free?
3. Does it address a known LLM or coding-agent failure mode?
4. Can a human also understand the output?
5. Are edge cases covered by fixtures?

If the answer to any of these is no, narrow the tool until the answer is yes.

