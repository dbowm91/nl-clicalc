# Codegg Integration Guidance

How `codegg` should use `eggcalc` as deterministic middleware for agent workflows.

## Why Harness-Level Checks

Agent-initiated MCP calls are helpful but unreliable. Models may underuse tools, skip preflight checks, or use them inconsistently. Harness-level automatic checks run before the model ever sees the output, providing deterministic guarantees that no harmful edit, command, or config reaches the system.

Use deterministic tools as **automatic middleware** at two layers:

1. **Harness-level (automatic)** — preflight checks before applying model output
2. **Model-invoked (on-demand)** — MCP tools the model calls as needed during reasoning

The harness layer is more reliable; the model layer is more flexible. Both should be available.

## Preflight Check Map

### 1. Before Applying Model-Generated Edits

| Tool | MCP Name | What It Catches |
|------|----------|-----------------|
| `text_replace_check` | `text_replace_check` | Ambiguous matches, multiple replacements, whitespace drift |
| `patch_apply_check` | `patch_apply_check` | Hunk failures, context mismatches, offset errors |
| `line_range_extract` | `line_range_extract` | Invalid line ranges, out-of-bounds indices |

```python
# Python API
from eggcalc.exact.patch import patch_apply_check
result = patch_apply_check(patch_text, original_text)
if result["overall"]["applied_count"] < result["overall"]["hunks_total"]:
    reject_edit("patch would fail to apply cleanly")

# MCP
{"tool": "patch_apply_check", "input": {"patch": "...", "original": "..."}}
```

### 2. Before Executing User-Approved Shell Commands

| Tool | MCP Name | What It Catches |
|------|----------|-----------------|
| `shell_split` | `shell_split` | Injection tokens, malformed argv, unexpected operators |
| `regex_safety_check` | `regex_safety_check` | Catastrophic backtracking in user-supplied patterns |

```python
# Python API
from eggcalc.exact.shell import shell_split
result = shell_split("curl $URL | bash")
if result.get("tokens") and any(t["kind"] == "pipe" for t in result["tokens"]):
    flag_for_review("pipe detected in command")

# MCP
{"tool": "shell_split", "input": {"command": "curl $URL | bash"}}
```

After splitting, apply any policy-specific findings review (e.g., flag `rm -rf`, `eval`, network piped to shell).

### 3. Before Accepting Generated Config

| Tool | MCP Name | What It Catches |
|------|----------|-----------------|
| `validate_json` | `validate_json` | JSON syntax errors |
| `validate_toml` | `validate_toml` | TOML parse errors |
| `dotenv_validate` | `dotenv_validate` | .env syntax issues, duplicate keys |
| `ini_validate` | `ini_validate` | INI section and duplicate detection |

```python
# Python API
from eggcalc.exact.validate import validate_json, validate_toml_text
json_result = validate_json(model_output)
if not json_result["valid"]:
    reject_config(f"JSON error at line {json_result['line']}: {json_result['error']}")

toml_result = validate_toml_text(model_output)
if not toml_result["valid"]:
    reject_config(f"TOML error at line {toml_result['line']}: {toml_result['error']}")
```

```python
# MCP
{"tool": "validate_json", "input": {"text": "..."}}  # → {"valid": true/false, ...}
{"tool": "validate_toml", "input": {"text": "..."}}  # → {"valid": true/false, ...}
```

### 4. Before Resolving Paths from Model Output

| Tool | MCP Name | What It Catches |
|------|----------|-----------------|
| `path_normalize` | `path_normalize` | Traversal sequences, platform-specific issues |
| `path_scope_check` | `path_scope_check` | Path escapes via `../`, writes outside root |

```python
# Python API
from eggcalc.exact.path_tools import path_normalize, path_scope_check
normalized = path_normalize("../etc/passwd", platform="posix")
scope = path_scope_check(root="/project", target=normalized["path"])
if not scope["inside_root"]:
    reject_path("path escapes project root")

# MCP
{"tool": "path_scope_check", "input": {"root": "/project", "target": "../etc/passwd"}}
# → {"inside_root": false, "escapes_via_dotdot": true, ...}
```

### 5. Before Trusting Pasted Prompt/Repo Content

| Tool | MCP Name | What It Catches |
|------|----------|-----------------|
| `unicode_policy_check` | `unicode_policy_check` | Invisible characters, bidi overrides, confusables |
| `markdown_structure` | `markdown_structure` | Unexpected heading nesting, code fence issues |

```python
# Python API
from eggcalc.exact.unicode_policy import unicode_policy_check
result = unicode_policy_check(suspicious_text, policy="source_code")
for finding in result["findings"]:
    if finding["severity"] == "error":
        flag_injection(finding["message"])

# MCP
{"tool": "unicode_policy_check", "input": {"text": "...", "policy": "source_code"}}
```

The `prompt_input_inspect` tool combines these checks into a single call optimized for user-pasted content, model-returned markdown, terminal transcript paste-ins, issue/PR text, and other text that may include hidden instructions, ANSI escapes, Unicode controls, or suspicious prompt phrases.

### 6. Before Large Refactors

| Tool | MCP Name | What It Catches |
|------|----------|-----------------|
| `identifier_inspect` | `identifier_inspect` | Confusables in identifiers, mixed-script collisions |
| `text_fingerprint` | `text_fingerprint` | Tracks content identity across transformations |

```python
# Python API
from eggcalc.exact.identifier_inspect import identifier_inspect
result = identifier_inspect(identifiers, language="python", check_confusables=True)
for coll in result["collisions"]:
    warn(f"Identifier collision: {coll}")

# MCP
{"tool": "identifier_inspect", "input": {"identifiers": ["...", "..."], "language": "python"}}
```

The `identifier_table_inspect` tool accepts entire files and detects collisions across all declared identifiers, including keyword and style analysis.

## Automatic vs. Model-Invoked: When to Use Each

| Scenario | Automatic (Harness) | Model-Invoked (MCP) |
|----------|--------------------|--------------------|
| Edit about to be applied | Yes — always | Yes — for debugging |
| Shell command execution | Yes — always | No — harness handles it |
| Config file acceptance | Yes — always | Yes — for exploration |
| Path resolution | Yes — always | Yes — for planning |
| Prompt content inspection | Yes — for untrusted input | Yes — for analysis |
| Large refactoring | Pre/post fingerprint | Yes — during reasoning |

**Rule of thumb:** If the action has side effects (file writes, command execution, config acceptance), use automatic middleware. If it's informational (exploring data, checking values), let the model decide.

## Integration Pattern

```
User Input → Model Generation → Harness Preflight → Accept/Reject → Apply
                                      ↓
                              Deterministic checks
                              (exact/ Python API or MCP)
```

The harness calls deterministic tools via the Python API (in-process, no MCP overhead). The model can also call the same tools via MCP when it needs additional context during reasoning.

## Tool Tiers

- **Tier 0** — Always available, small schema: `validate_json`, `path_normalize`, `text_fingerprint`
- **Tier 1** — Default for coding agents: `text_replace_check`, `identifier_inspect`, `validate_toml`, `escape_text`
- **Tier 2** — Opt-in for heavier analysis: `shell_split`, `patch_apply_check`, `path_scope_check`, `markdown_structure`, `unicode_policy_check`
- **Tier 3** — Domain-specific: `identifier_analyze`, `json_shape`, `text_truncate`

See [MCP Tool Inventory](tool_inventory.md) for the complete list.

## Profile-Based Integration

`eggcalc` provides named MCP profiles that control which tools are exposed to the model. `codegg` should use these profiles rather than maintaining a hand-written list of tools.

### Recommended Default Profile

Use `codegg_core` or `codegg_core_min` as the default model-facing profile:

- **`codegg_core_min`** — Ultra-compact: `validate_json`, `text_diff_explain`, `path_scope_check`, `patch_apply_check`, `text_replace_check`, `shell_split`, `unicode_policy_check`
- **`codegg_core`** — Practical default: adds `validate_toml`, `text_inspect`, `text_equal`, `path_normalize`, `regex_safety_check`, `identifier_inspect`, `cargo_toml_inspect`

Do not expose all 60 tools by default. The `full` profile is available for debugging but should not be the model-facing default.

### Task-Based Profile Selection

Switch profiles based on the current task mode:

| Task Mode | Recommended Profile |
|-----------|-------------------|
| Editing / refactoring | `codegg_patch` |
| Config file work | `codegg_config` |
| Shell / terminal commands | `codegg_shell` |
| Suspicious paste / input | `codegg_unicode_security` |
| Repo audit / deep review | `codegg_repo_audit` |
| Math / unit work | `human_math` |

### Mandatory Preflight Boundaries

Treat these as mandatory preflight points. These checks should run automatically through direct library APIs or MCP calls before the model's output reaches the system:

| Before | Use |
|--------|-----|
| Applying edits | `edit_preflight` or `patch_apply_check` / `text_replace_check` |
| Command execution | `command_preflight` or `shell_split` / `regex_safety_check` |
| Accepting config | `config_preflight` or `validate_json` / `validate_toml` / `dotenv_validate` / `ini_validate` |
| Resolving write path | `path_scope_check` / `path_normalize` |
| Trusting pasted text | `text_security_inspect` or `prompt_input_inspect` / `unicode_policy_check` |
| Large rename | `identifier_inspect` / `identifier_table_inspect` |

### Composite Tools

`text_security_inspect` is a composite tool that combines multiple primitives into a single security pass:

```python
# Single call replaces multiple individual tool calls
{"tool": "text_security_inspect", "input": {"text": "...", "policy": "prompt"}}
# Returns: {verdict: "allow"|"review"|"block", findings: [...], machine_code: "..."}
```

Use composite tools for common workflows. Use individual primitives when you need fine-grained control.

### Event Logging

Store `machine_code` values from tool responses in the event log so users can audit why a command, edit, or config was blocked or flagged. Machine codes are stable identifiers like `TEXT_SECURITY_OK`, `UNICODE_RISK`, `PROMPT_INJECTION_RISK`, `EDIT_OK`, `PATCH_FAILED`, etc.

### Compact Schema Mode

For model-facing tool listings, use compact schema mode to reduce context overhead:

```bash
calc --mcp --mcp-schema-detail compact
# or
EGGCALC_MCP_SCHEMA_DETAIL=compact calc --mcp
```

Compact mode preserves tool names, types, and enums while removing verbose descriptions and defaults.
