# Final MCP Cleanup Pass Plan

This plan is for the final cleanup pass after the MCP profile hardening work. The current implementation is close to stable as the Python reference implementation for deterministic MCP tooling, but a few final consistency and verification items remain.

The scope of this pass is deliberately narrow. Do not add new tools. Do not redesign the profile system. Do not change primitive tool semantics unless a failing test exposes a real contract bug.

## Current state summary

The repository now has:

- 64 MCP tools.
- Explicit `TOOL_METADATA` and generated `TOOL_PROFILES`.
- Fail-closed profile handling through `get_profile_tools()`.
- Profile enforcement in `tools/call`.
- Profile filtering in `tools/list`.
- `profiles/list` support.
- `--mcp-profile` and `--mcp-schema-detail` CLI flags.
- `EGGCALC_MCP_PROFILE` and `EGGCALC_MCP_SCHEMA_DETAIL` environment variables.
- Composite workflow tools for codegg-oriented workflows.
- Complete inventory count: 64 tools, 64 tested, 64 documented in `docs/mcp.md`.
- Cleaner split between model-facing profiles and harness/preflight profiles in metadata.

The remaining work is mostly documentation consistency and explicit protocol test coverage.

## Phase 1: Fix stale `docs/codegg_integration.md` profile text

### Problem

`docs/codegg_integration.md` currently contains conflicting guidance for `codegg_core_min`.

The newer section correctly says:

- `codegg_core_min` is minimal model-facing exposure.
- It should be composite-workflow focused.
- Harness/preflight profiles contain low-level primitives and are not typically model-facing.

But an older section still says `codegg_core_min` contains low-level harness primitives such as:

- `path_scope_check`
- `patch_apply_check`
- `text_replace_check`
- `shell_split`
- `unicode_policy_check`

That conflicts with the current metadata direction, where those low-level primitives are `harness_only` and live in `codegg_preflight` or task-specific profiles.

### Required change

Update the `Recommended Default Profile` section so it matches the actual generated profiles.

Do not hardcode a stale hand-written list unless a test guarantees it matches `TOOL_PROFILES`. Prefer a conceptual description plus a generated or easily maintained list.

Recommended wording:

```markdown
Use `codegg_core` or `codegg_core_min` as the default model-facing profile.

- `codegg_core_min` — Ultra-compact model-facing profile. Prefer composite workflow tools and a small number of safe reasoning primitives. This is the best default for small-context or high-tool-noise models.
- `codegg_core` — Practical model-facing profile. Includes `codegg_core_min` plus additional safe reasoning tools for JSON/TOML validation, text inspection, diffing, identifiers, and repository-adjacent checks.

Low-level primitives marked `harness_only` are intentionally kept out of these model-facing profiles. They belong in `codegg_preflight` and task-specific profiles such as `codegg_patch`, `codegg_shell`, and `codegg_unicode_security`.
```

If you include exact tool lists, source them from `TOOL_PROFILES` and update tests to fail on drift.

### Tests

Add a docs consistency test if practical:

1. Search `docs/codegg_integration.md` for the specific stale phrase/list.
2. Assert the old low-level primitive list is not described as `codegg_core_min`.
3. Optionally assert that `codegg_core_min` docs mention composite workflow tools.

Minimum acceptable fix: manual docs update plus inventory/profile tests remain green.

## Phase 2: Add explicit protocol-level profile tests

### Problem

The code now implements the correct profile behavior, but the final reference implementation should have direct protocol tests for the MCP behavior. Registry/metadata tests are not enough.

### Required tests

Add a focused test class, preferably `TestMCPProfilesProtocol`, in `tests/test_mcp_server.py` or a new `tests/test_mcp_profiles.py`.

Use fixtures to save and restore global state:

```python
@pytest.fixture(autouse=True)
def restore_mcp_profile_and_schema_detail():
    from eggcalc.mcp.server import get_active_profile, set_active_profile, get_schema_detail, set_schema_detail
    old_profile = get_active_profile()
    old_detail = get_schema_detail()
    try:
        yield
    finally:
        set_active_profile(old_profile)
        set_schema_detail(old_detail)
```

Add tests for `tools/list`:

1. `tools/list` with no profile under default `full` returns all non-hidden tools.
2. `tools/list` with `params.profile = "codegg_core_min"` returns exactly `TOOL_PROFILES["codegg_core_min"]`.
3. `tools/list` with `params.profile = "codegg_core"` returns exactly `TOOL_PROFILES["codegg_core"]`.
4. `tools/list` with `params.profile = "human_math"` includes `math_eval` and excludes `edit_preflight` / `command_preflight`.
5. `tools/list` with `params.profile = "does_not_exist"` returns a JSON-RPC error and no tools.
6. `tools/list` with both `profile` and `names` filters must not leak tools outside that profile. For example, requesting `names=["math_eval"]` under `codegg_core_min` should return no tools if `math_eval` is not in that profile.
7. `tools/list` with both `profile` and `tier` applies tier filtering after profile filtering.
8. `tools/list` with both `profile` and `tags` applies tag filtering after profile filtering.

Add tests for `tools/call`:

1. Set active profile to `codegg_core_min`; calling `math_eval` returns a profile-unavailable error.
2. Set active profile to `human_math`; calling `math_eval` succeeds.
3. Set active profile to `codegg_core_min`; calling a tool in that profile succeeds.
4. Switching profiles changes availability.
5. Profile enforcement happens before execution. Use a tool with required arguments outside the active profile and pass invalid/missing arguments; the returned error should be profile-unavailable, not argument validation.

Add tests for `profiles/list`:

1. `profiles/list` returns `active_profile`.
2. It includes every name in `PROFILE_NAMES`.
3. Every returned `tool_count` matches the length of the returned tool list.
4. `full` count matches all non-hidden tools.

## Phase 3: Add explicit schema-detail protocol tests

### Problem

Compact schema mode is implemented and improved, but it should have protocol-level tests so future changes do not regress tool-listing behavior.

### Required tests

Add tests for `tools/list` schema detail handling:

1. `schema_detail = "compact"` returns compact schemas.
2. Compact entries include:
   - `name`
   - `description`
   - `inputSchema`
   - `outputSchema`
   - `category`
   - `llm_exposure`
   - `cost`
3. Compact entries preserve enum values in input schemas.
4. Compact entries preserve top-level output property keys/types when an output schema exists.
5. Compact entries omit verbose fields such as full tags/tier if that is the intended compact contract.
6. `schema_detail = "full"` returns full entries with tier and tags.
7. `schema_detail = "normal"` is accepted.
8. Invalid `schema_detail` returns a JSON-RPC error.
9. Runtime tool behavior is identical regardless of schema detail. This can be tested by listing schemas under compact/full and then calling the same tool normally.

### Decide/document normal mode

`normal_schema()` currently returns the full schema and has a TODO. That is acceptable for now if explicitly documented.

Make one of these decisions:

Option A: Keep `normal` as an alias for `full` for this release.

- Update docs to say `normal` currently aliases `full`.
- Keep the TODO in code.
- Add a test that `normal` is accepted, not that it differs from full.

Option B: Implement true `normal` mode.

- Preserve concise input and output schema structure.
- Drop long descriptions/examples.
- Keep enough output detail for agents to plan.

Recommended for final cleanup: choose Option A. Do not implement true normal mode unless it is trivial and well tested.

## Phase 4: Add metadata/profile invariant tests for model-facing profiles

### Problem

The metadata appears corrected so model-facing profiles no longer include `harness_only` tools, but the invariant should be tested permanently.

### Required tests

Add tests in `tests/test_tool_inventory.py` or a profile-specific test file:

1. No tool in `codegg_core_min` has `llm_exposure == "harness_only"`.
2. No tool in `codegg_core` has `llm_exposure == "harness_only"`.
3. Every `harness_only` tool appears in at least one harness/task profile:
   - `codegg_preflight`
   - `codegg_patch`
   - `codegg_config`
   - `codegg_shell`
   - `codegg_unicode_security`
4. Every composite tool marked `llm_exposure == "default"` appears in at least one model-facing profile or has a documented reason not to.
5. `codegg_core_min` is a subset of `codegg_core` if that remains the intended contract.
6. `human_math` contains math tools and excludes codegg preflight/composite tools.

## Phase 5: Verify composite tool contract tests

### Problem

Composite workflow tools are now central to the model-facing profile story. They need stable verdict/machine-code tests.

### Required checks

Confirm tests exist for each composite tool. Add missing tests only where needed.

For `text_security_inspect`, ensure tests cover:

- Clean text -> `allow` and `TEXT_SECURITY_OK`, or absence of risk machine code if that is the chosen contract.
- Bidi override or invisible control -> `review` or `block`.
- Prompt-injection phrase under `policy="prompt"` -> not `allow`.
- Normalization change with `compare_normalized=true` is reported.

For `edit_preflight`, ensure tests cover:

- Clean literal replacement -> `ok_to_apply = true`.
- Missing literal -> not ok.
- Multiple matches with strict mode -> not ok.
- Patch that does not apply -> not ok.
- Expected fingerprint mismatch -> not ok.

For `command_preflight`, ensure tests cover:

- Simple safe command -> `allow` or low-risk verdict.
- Piped network-to-shell command -> `review` or `block`.
- Destructive command pattern -> `review` or `block`.
- Invalid shell syntax -> not `allow`.
- The tool does not execute commands.

For `config_preflight`, ensure tests cover:

- Valid JSON auto-detected.
- Invalid JSON with explicit format.
- Valid TOML auto-detected.
- Invalid TOML.
- Cargo.toml format if supported.

For `structured_data_compare`, ensure tests cover:

- Object key order ignored.
- Array order respected when `ignore_array_order=false`.
- Invalid JSON in either input returns structured invalid result, not raw exception.

Do not change contracts unnecessarily. The goal is to pin existing behavior.

## Phase 6: Final documentation pass

Update docs after tests and metadata are final.

### `docs/codegg_integration.md`

Ensure it consistently says:

- `codegg_core_min` and `codegg_core` are model-facing profiles.
- `codegg_core_min` is composite-first/minimal.
- `codegg_preflight` is not normally model-facing; it is a reference profile for automatic harness checks.
- Low-level `harness_only` tools should be called automatically by codegg at side-effect boundaries.
- Composite tools are preferred for model-facing workflows.
- `full` is for debugging/human expert use.
- `human_math` is only for math/unit-heavy tasks.

Include exact launch commands:

```bash
calc --mcp --mcp-profile codegg_core_min --mcp-schema-detail compact
calc --mcp --mcp-profile codegg_core --mcp-schema-detail compact
```

### `docs/mcp.md`

Confirm all 64 tools are listed and the profile/schema behavior is documented.

Ensure the docs mention:

- `tools/list` supports `profile`, `tier`, `tags`, `names`, and `schema_detail` filters.
- Unknown profile names fail closed.
- `profiles/list` exists.
- `normal` schema detail currently aliases `full`, if choosing Option A above.

### `docs/tool_inventory.md`

Regenerate or update if any profile/docs/test changes alter counts.

The final summary should still show:

- Total tools: 64
- Documented in docs/mcp.md: 64
- Missing from docs/mcp.md: 0
- Have tests: 64
- Missing tests: 0

## Phase 7: Final CI and release-readiness checks

Run the standard checks locally or in CI:

```bash
python -m pytest
python -m pytest tests/test_mcp_server.py tests/test_tool_inventory.py
python -m ruff check .
python -m mypy eggcalc
```

If mypy is not currently clean because of pre-existing issues, document that rather than expanding this cleanup pass.

Manual smoke checks:

```bash
calc --mcp --mcp-profile codegg_core_min --mcp-schema-detail compact
calc --mcp --mcp-profile codegg_core --mcp-schema-detail compact
calc --mcp --mcp-profile does_not_exist
EGGCALC_MCP_PROFILE=does_not_exist calc --mcp
```

Expected behavior:

- Valid profiles start normally.
- Invalid profiles fail clearly.
- Compact schemas list only profile-visible tools.
- Tools outside active profile are rejected.

## Acceptance criteria

This final cleanup pass is complete when:

1. `docs/codegg_integration.md` no longer contains stale `codegg_core_min` tool-list guidance.
2. `codegg_core_min` and `codegg_core` docs match metadata/profile semantics.
3. Explicit protocol tests cover `tools/list` profile filtering and unknown profile errors.
4. Explicit protocol tests cover `tools/call` profile enforcement.
5. Explicit protocol tests cover `profiles/list`.
6. Explicit protocol tests cover compact/full/normal schema-detail behavior.
7. Metadata invariant tests prevent `harness_only` tools from re-entering model-facing profiles.
8. Composite tool verdict/machine-code behavior is pinned by tests.
9. `docs/mcp.md` and `docs/tool_inventory.md` remain consistent with 64 tools.
10. The standard test suite passes.

## Notes for implementation agents

Keep this final pass boring. The repo is already functionally strong. The purpose now is to remove ambiguity and prevent regressions.

Prioritize in this order:

1. Fix stale docs.
2. Add protocol-level tests.
3. Add metadata/profile invariant tests.
4. Confirm composite contract tests.
5. Update docs and inventory.
6. Run CI.

Do not add new features unless a test reveals an actual bug in the intended current behavior.
