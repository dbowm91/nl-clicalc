# MCP Profile Hardening and Cleanup Plan

This plan covers the remaining hardening and cleanup work after the MCP profile, metadata, compact schema, and composite-tool pass. The repo is now much closer to a stable Python reference implementation for deterministic MCP tooling, but several semantic and protocol-level details should be tightened before treating the profile system as a stable contract for `codegg` or downstream implementations.

The goal of this pass is not to add more tools. The goal is to make the existing 64-tool surface safer, more internally consistent, and easier for `codegg` to consume without accidental broad exposure.

## Current state

The repository now has:

- 64 MCP tools in `eggcalc.mcp.server.TOOL_HANDLERS`.
- Explicit `TOOL_METADATA` and generated `TOOL_PROFILES` in `eggcalc.mcp.schemas`.
- Named profiles including `full`, `default`, `codegg_core_min`, `codegg_core`, `codegg_preflight`, `codegg_patch`, `codegg_config`, `codegg_unicode_security`, `codegg_shell`, `codegg_repo_audit`, and `human_math`.
- Compact schema support through `compact_schema()` and `--mcp-schema-detail`.
- Runtime profile selection through `--mcp-profile` and `EGGCALC_MCP_PROFILE`.
- Runtime schema-detail selection through `--mcp-schema-detail` and `EGGCALC_MCP_SCHEMA_DETAIL`.
- Composite workflow tools: `text_security_inspect`, `edit_preflight`, `command_preflight`, `config_preflight`, and `structured_data_compare`.
- Inventory tests that check handler/schema/fixture/doc count consistency and metadata coverage.
- Updated `docs/codegg_integration.md` with profile guidance and codegg preflight semantics.

This is a strong state. The remaining concerns are mostly about fail-closed behavior, profile semantics, documentation completeness, and protocol-level test coverage.

## Phase 1: Make profile handling fail closed

### Problem

`get_profile_tools(profile)` currently returns all tools when an unknown profile is passed and the profile is not `full`. That is unsafe for an exposure-control mechanism. The CLI path is partly protected because `set_active_profile()` validates profile names, but `tools/list` accepts a per-request `profile` parameter and calls `get_profile_tools(profile_filter)`. A typo or unrecognized profile in `tools/list` should not silently expose the full tool surface.

### Required behavior

Unknown profile names must fail closed.

Implement this behavior:

```python
def get_profile_tools(profile: str | None = None) -> list[str]:
    if profile is None:
        profile = get_active_profile()
    if profile == "full":
        ...
    if profile not in TOOL_PROFILES:
        raise ValueError(...)
    return list(TOOL_PROFILES[profile])
```

Then update callers:

- `set_active_profile()` already raises on unknown profile. Keep that behavior.
- `_handle_list_tools()` must catch `ValueError` and return a JSON-RPC invalid params error.
- `_handle_call_tool()` must catch `ValueError` defensively, even though the active profile should already be valid.
- `profiles/list` should remain unaffected.

### Error shape

Use a clear error message with the invalid name and available profile names:

```text
Unknown MCP profile: 'codgg_core'. Available profiles: codegg_core, codegg_core_min, ...
```

For `tools/list`, return `-32602` or use `_invalid_request()` consistently with the rest of the server’s parameter validation. Prefer `-32602` because the profile parameter is invalid.

### Tests

Add protocol-level tests:

1. `tools/list` with `params.profile = "does_not_exist"` returns an error.
2. `tools/list` with unknown profile does not return any tools.
3. `get_profile_tools("does_not_exist")` raises `ValueError`.
4. `set_active_profile("does_not_exist")` raises `ValueError`.
5. If `EGGCALC_MCP_PROFILE` is invalid at import/startup, either startup should reject it clearly or the first profile-dependent request should return a clear error. Prefer validating it during MCP startup if practical.

## Phase 2: Resolve `harness_only` versus model-facing profile semantics

### Problem

Several tools included in `codegg_core` or `codegg_core_min` are marked as `llm_exposure = "harness_only"`. Examples likely include lower-level preflight primitives such as `patch_apply_check`, `path_scope_check`, `shell_split`, and `unicode_policy_check`.

That creates a semantic mismatch. The docs describe `codegg_core` and `codegg_core_min` as model-facing profiles, but `harness_only` implies the model should not call those tools directly.

### Decision to make

Choose one of these models and make the metadata/docs/profiles agree.

#### Option A: Model-facing core exposes composite tools, not harness-only primitives

Recommended.

`codegg_core_min` should expose compact, model-friendly workflow tools rather than low-level harness-only primitives:

```text
validate_json
text_diff_explain
text_security_inspect
edit_preflight
command_preflight
config_preflight
```

`codegg_core` can add:

```text
validate_toml
text_inspect
text_equal
path_normalize
regex_safety_check
identifier_inspect
cargo_toml_inspect
structured_data_compare
```

Under this option:

- Keep `patch_apply_check`, `path_scope_check`, `shell_split`, `unicode_policy_check`, and similar low-level tools as `harness_only`.
- Put those low-level tools in `codegg_preflight`, `codegg_patch`, `codegg_shell`, `codegg_unicode_security`, etc.
- Remove low-level `harness_only` primitives from model-facing `codegg_core_min` and possibly from `codegg_core` unless there is a clear model-facing reason.

#### Option B: Treat selected low-level tools as model-callable

If direct model access to `patch_apply_check`, `path_scope_check`, `shell_split`, and `unicode_policy_check` is desired, reclassify them from `harness_only` to `default` or `contextual`.

Under this option:

- `harness_only` must mean truly hidden from model-facing profiles.
- Any tool included in `codegg_core` should not be marked `harness_only`.
- Use `harness_use` to express that codegg should also call the tool automatically at side-effect boundaries.

### Recommended implementation

Use Option A. Make `codegg_core_min` composite-first. Keep low-level primitives available in task-specific or preflight profiles.

### Tests

Add invariants:

1. No tool in `codegg_core_min` has `llm_exposure == "harness_only"`.
2. No tool in `codegg_core` has `llm_exposure == "harness_only"`, unless an explicit allowlist is documented in the test.
3. Every tool with `llm_exposure == "harness_only"` appears in at least one harness/preflight profile, such as `codegg_preflight`, `codegg_patch`, `codegg_shell`, `codegg_config`, or `codegg_unicode_security`.
4. Every composite tool marked `llm_exposure == "default"` has at least one basic protocol test.

Update docs after deciding. `docs/codegg_integration.md` should distinguish:

- Model-facing profiles: `codegg_core_min`, `codegg_core`.
- Harness/preflight profiles: `codegg_preflight`, `codegg_patch`, `codegg_config`, `codegg_shell`, `codegg_unicode_security`.
- Debug/specialist profiles: `full`, `codegg_repo_audit`, `human_math`.

## Phase 3: Complete MCP documentation for all 64 tools or explicitly define doc tiers

### Problem

`docs/tool_inventory.md` reports 64 total tools, but only 60 documented in `docs/mcp.md`, with 4 missing. The missing tools are likely the newly added composites or recent additions.

### Required behavior

Either document all 64 tools in `docs/mcp.md`, or explicitly make `docs/tool_inventory.md` the canonical full listing and adjust the docs language so `docs/mcp.md` is an overview rather than an exhaustive reference.

Recommended: document all 64 tools briefly in `docs/mcp.md`, but keep detailed examples only for high-value tools.

### Required docs updates

Add sections for any missing tools, especially:

- `text_security_inspect`
- `edit_preflight`
- `command_preflight`
- `config_preflight`
- `structured_data_compare`

Each section should include:

- Purpose.
- Arguments.
- Tier.
- Tags/category.
- Output shape summary.
- One minimal JSON call example.
- Notes on whether the tool is composite and which primitive tools it wraps.

Also update any stale count references:

- If `docs/codegg_integration.md` says “all 60 tools,” update to 64 or phrase as “all tools.”
- If README references older counts, update it.
- If `docs/mcp.md` still claims older tier assignments, sync them with `TOOL_SCHEMAS` and `TOOL_METADATA`.

### Tests

Extend the inventory doc tests if practical:

1. `docs/mcp.md` should mention every tool name, unless a tool is explicitly annotated as intentionally undocumented.
2. The documented count in `docs/tool_inventory.md` should be generated or tested against actual matches.
3. README count references should be checked if the README claims a total tool count.

## Phase 4: Add protocol-level tests for profile and schema behavior

### Problem

The repo now has strong registry and metadata consistency tests, but protocol-level behavior needs more explicit coverage. Metadata can be correct while `tools/list`, `tools/call`, profile filtering, or compact schema behavior are wrong.

### Required tests for `tools/list`

Add tests in `tests/test_mcp_server.py` or a new `tests/test_mcp_profiles.py`:

1. `tools/list` with no params under default `full` returns all non-hidden tools.
2. `tools/list` with `params.profile = "codegg_core_min"` returns exactly the profile list from `TOOL_PROFILES["codegg_core_min"]`.
3. `tools/list` with `params.profile = "codegg_core"` returns exactly `TOOL_PROFILES["codegg_core"]`.
4. `tools/list` with `params.profile = "human_math"` returns math tools and excludes codegg preflight tools.
5. `tools/list` with `tier` filters after profile filtering, not before.
6. `tools/list` with `names` filters after profile filtering and does not leak tools outside the requested profile.
7. `tools/list` with `tags` filters after profile filtering.
8. `tools/list` with unknown profile returns an error.

### Required tests for `tools/call`

Add tests:

1. Under active profile `codegg_core_min`, a tool outside the profile, such as `math_eval`, is rejected.
2. Under active profile `human_math`, `math_eval` succeeds.
3. Under active profile `codegg_core_min`, a profile tool such as `text_security_inspect` or `validate_json` succeeds.
4. Switching active profile changes tool availability.
5. Profile enforcement happens before tool execution.
6. The error message names the active profile and does not execute the handler.

Ensure tests restore the active profile after mutation. Use fixtures to save/restore `get_active_profile()` and `get_schema_detail()`.

### Required tests for `profiles/list`

Add tests:

1. `profiles/list` returns `active_profile`.
2. `profiles/list` includes every `PROFILE_NAMES` entry.
3. Each profile reports `tool_count` matching the length of the profile’s tool list.
4. `full` count matches non-hidden tools.

### Required tests for schema detail

Add tests:

1. `tools/list` with `schema_detail = "compact"` returns compact schemas.
2. Compact schemas still include tool name, description, input schema, category, exposure, and cost.
3. Compact schemas omit or minimize verbose output schemas.
4. `schema_detail = "normal"` and `schema_detail = "full"` are accepted.
5. Invalid `schema_detail` returns an error.
6. Runtime tool behavior is identical regardless of schema detail.

## Phase 5: Tighten compact schema semantics

### Problem

Compact mode currently drops output schemas to `{"type": "object"}` and strips defaults. This may be acceptable for context reduction, but it is potentially too lossy for agents that use output hints for planning.

### Recommended change

Introduce three clear schema-detail levels:

```text
compact:
  Minimal model-routing schema. Preserve name, short description, required args, types, enums, category, exposure, cost. Output schema can be minimal.

normal:
  Default model-facing schema. Preserve concise input and concise output shape. Drop verbose examples and long descriptions.

full:
  Full reference schema. Preserve complete descriptions, defaults, output schemas, tags, tier, and metadata.
```

Currently, non-compact mode effectively behaves like full. Either implement true `normal`, or document that `normal` is currently an alias for `full` and add a TODO/test marker.

### Implementation notes

1. Add `normal_schema(schema)` if implementing true normal mode.
2. Keep `compact_schema(schema)` deterministic.
3. Do not alter runtime argument validation based on schema-detail mode.
4. Make sure compact schemas still include enum values; these are important for agents.
5. Consider preserving output keys in compact mode without full nested detail:

```json
"outputSchema": {
  "type": "object",
  "properties": {
    "verdict": {"type": "string"},
    "findings": {"type": "array"},
    "machine_code": {"type": "string"}
  }
}
```

Do this especially for composite workflow tools.

## Phase 6: Strengthen composite tool contracts

### Problem

Composite tools are now present and tested enough to appear in inventory, but they should become stable workflow contracts. `codegg` will likely depend on their verdicts and machine codes, so the output semantics need to be rigid.

### Required invariants

For every composite tool:

- Must return a stable top-level verdict or equivalent action field.
- Must return `machine_code` at the success-envelope level or result level; choose one convention and document it.
- Must return structured `findings` for actionable issues.
- Must not perform side effects.
- Must preserve primitive subresults when `detail = "full"`, if supported.
- Must provide compact summary output under `detail = "summary"`, if supported.

### Tool-specific expectations

#### `text_security_inspect`

Expected verdicts:

```text
allow, review, block
```

Expected machine-code families:

```text
TEXT_SECURITY_OK
UNICODE_RISK
PROMPT_INJECTION_RISK
IDENTIFIER_COLLISION_RISK
ANSI_ESCAPE_RISK
NORMALIZATION_CHANGED
```

Tests:

- Clean source text -> `allow`, `TEXT_SECURITY_OK`.
- Text with bidi override -> `review` or `block` depending policy.
- Text with prompt-injection phrase under `policy="prompt"` -> not `allow`.
- Text with normalization change under `compare_normalized=true` reports changed state.

#### `edit_preflight`

Expected action field:

```text
ok_to_apply: bool
```

Expected machine-code families:

```text
EDIT_OK
PATCH_FAILED
AMBIGUOUS_REPLACEMENT
FINGERPRINT_MISMATCH
LINE_RANGE_INVALID
```

Tests:

- Clean literal replacement -> ok.
- Missing literal -> not ok.
- Multiple literal matches with strict mode -> not ok.
- Patch that does not apply -> not ok.
- Expected fingerprint mismatch -> not ok.

#### `command_preflight`

Expected verdicts:

```text
allow, review, block
```

Expected tests:

- Simple command -> allow or review based on policy.
- Piped network-to-shell command -> review or block.
- Destructive command pattern -> review or block.
- Invalid shell syntax -> not allow.

This tool must not execute commands.

#### `config_preflight`

Expected tests:

- Valid JSON auto-detected -> valid.
- Invalid JSON with explicit format -> invalid with line/column.
- Valid TOML auto-detected -> valid.
- Invalid TOML -> invalid.
- Cargo.toml format routes through Cargo inspection if format is `cargo_toml`.

#### `structured_data_compare`

Expected tests:

- Semantically equal JSON with different object key order -> equal.
- Array order difference with `ignore_array_order=false` -> not equal.
- Invalid JSON in either input -> invalid structured result, not raw exception.

## Phase 7: Update codegg guidance after profile semantics are finalized

After profile semantics are fixed, update `docs/codegg_integration.md` again.

Required additions:

1. Show the exact command for model-facing MCP exposure:

```bash
calc --mcp --mcp-profile codegg_core --mcp-schema-detail compact
```

2. Show the exact command for minimal exposure:

```bash
calc --mcp --mcp-profile codegg_core_min --mcp-schema-detail compact
```

3. State that `codegg_preflight` is not necessarily model-facing; it is a reference profile for automatic harness checks.
4. Recommend composite tools for model-facing workflows and primitives for harness enforcement.
5. Document that `full` is for debugging and human/expert use, not normal model exposure.
6. Document that `human_math` should only be enabled for math/unit-heavy tasks.
7. Include an event-log example showing `machine_code`, tool name, profile, verdict, and findings count.

Example event log entry:

```json
{
  "event": "preflight_result",
  "tool": "edit_preflight",
  "profile": "codegg_preflight",
  "verdict": "block",
  "machine_code": "AMBIGUOUS_REPLACEMENT",
  "findings_count": 2
}
```

## Phase 8: Final acceptance criteria

This hardening pass is complete when:

1. Unknown profiles fail closed everywhere.
2. `tools/list` unknown profile returns an error, not all tools.
3. `get_profile_tools()` raises on unknown profile.
4. `codegg_core_min` and `codegg_core` no longer contain `harness_only` tools, or the exception is explicitly documented and tested.
5. `codegg_preflight` contains the low-level harness primitives needed for automatic checks.
6. All 64 tools are documented in `docs/mcp.md`, or `docs/mcp.md` explicitly states it is not exhaustive and tests account for that.
7. `docs/tool_inventory.md` count and documented/missing docs stats are accurate.
8. Protocol-level tests cover profile filtering, profile enforcement, unknown profile errors, `profiles/list`, and schema-detail behavior.
9. Compact schema mode has tested semantics.
10. Composite tools have stable verdict/machine-code tests.
11. `docs/codegg_integration.md` reflects the final model-facing versus harness-facing profile split.
12. CI passes.

## Suggested implementation order

1. Change `get_profile_tools()` to fail closed.
2. Add protocol tests for unknown profile behavior.
3. Decide and implement `harness_only` versus model-facing profile semantics. Prefer composite-first `codegg_core_min`.
4. Add metadata/profile invariant tests for `harness_only` tools.
5. Add or update profile snapshot tests.
6. Add `tools/list`, `tools/call`, `profiles/list`, and schema-detail protocol tests.
7. Tighten compact/normal/full schema semantics.
8. Add missing `docs/mcp.md` sections for composite tools and any other missing tools.
9. Update `docs/codegg_integration.md` with final profile commands and event-log guidance.
10. Strengthen composite tool verdict and machine-code tests.
11. Regenerate or update `docs/tool_inventory.md` if counts or docs coverage changed.

## Notes for smaller implementation models

Keep this pass narrow. Do not add new primitive tools unless a failing test exposes a genuine missing primitive. The current surface is already broad enough.

The priority order is safety first, then semantic consistency, then documentation polish. The most important single fix is fail-closed profile behavior. The most important design cleanup is resolving whether `codegg_core` is model-facing, harness-facing, or mixed. It should not remain ambiguous.
