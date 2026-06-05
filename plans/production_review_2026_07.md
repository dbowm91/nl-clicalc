# Production Code Review — 2026-07-05 (Batch Followup)

## Status: COMPLETED

Continuation of the 2026-06 production review. This batch addresses the
remaining CRITICAL, HIGH, and MEDIUM findings with the highest impact on
production safety. All fixes are standard-library only.

## Findings addressed

| ID  | Severity   | File                              | Status   | Summary |
|-----|------------|-----------------------------------|----------|---------|
| C-1 | Critical   | `eggcalc/evaluator.py`            | Fixed    | `random()` non-deterministic in MCP, no opt-in |
| C-2 | Critical   | `eggcalc/evaluator.py`            | Fixed    | Cache poisoning: `random()` cached |
| C-3 | Critical   | `eggcalc/evaluator.py`            | Fixed    | No `MAX_INPUT_LENGTH` on `evaluate()` |
| H-1 | High       | `eggcalc/mcp/schemas.py`          | Fixed    | `math_eval.expression` no `maxLength` |
| H-2 | High       | `eggcalc/mcp/server.py`           | Fixed    | Schema `type: [...]` silently no-op |
| H-3 | High       | `eggcalc/evaluator.py`            | Fixed    | `setvar` accepts non-identifier, cap unbounded |
| H-4 | High       | (description)                     | Clarified | Docstring said "per-request thread" but code uses bounded 16-worker pool; docstring rewritten to match |
| H-5 | High       | `eggcalc/units.py`                | Fixed    | Temperature offset rounding (C→R ≈ 671.6700000000001 vs 671.67) |
| H-6 | High       | `eggcalc/mcp/tools.py`            | Fixed    | `unit_convert` OverflowError not caught |
| H-7 | High       | `eggcalc/mcp/tools.py`            | Fixed    | `dotenv_validate` runs in-process, no timeout/RLIMIT |
| H-8 | High       | `eggcalc/mcp/server.py`           | Fixed    | Schema validator: missing `const`/`pattern`/`uniqueItems`/`exclusive*`/`multipleOf` |
| M-1 | Medium     | `eggcalc/mcp/tools.py`            | Fixed    | `text_diff_explain` no `except Exception` |
| M-2 | Medium     | `eggcalc/mcp/tools.py`            | Fixed    | `validate_brackets` `pairs` not type-checked |
| M-3 | Medium     | `eggcalc/mcp/tools.py`            | Fixed    | `validate_schema_light` unbounded recursion |
| M-4 | Medium     | `eggcalc/mcp/tools.py`            | Fixed    | `json_extract`/`json_query` `pointer` unbounded |
| M-5 | Medium     | `eggcalc/mcp/tools.py`            | Fixed    | `text_window` position fields unbounded |
| M-6 | Medium     | `eggcalc/mcp/schemas.py`          | Fixed    | `regex_finditer.flags` unbounded list |
| M-7 | Medium     | `eggcalc/mcp/tools.py`            | Fixed    | `text_hash.algorithms` unbounded list |
| M-8 | Medium     | `eggcalc/mcp/tools.py`            | Fixed    | List/str arg validation scattered; centralized helper |
| M-9 | Medium     | `eggcalc/mcp/tools.py`            | Fixed    | `identifier_table_inspect` field types unchecked |
| M-10| Medium     | `eggcalc/mcp/schemas.py`          | Fixed    | Missing `minimum`/`maximum` bounds on numeric args |
| M-11| Medium     | `eggcalc/evaluator.py`            | Fixed    | `<<` with huge shift DoS |
| M-12| Medium     | `eggcalc/evaluator.py`            | Fixed    | `fact(5m)` silently returns 120 (unit stripped) |
| M-14| Medium     | (false positive)                  | N/A      | `math.gcd` already raises `TypeError` on float; no fix needed |
| M-15| Medium     | `eggcalc/mcp/tools.py`            | Fixed    | `toml_shape.max_tables` type/range unchecked |

## Changes

### C-1 / H-3 — Opt-in random and side-effect functions

Added two flags to `Evaluator.__init__`:

- `allow_random: bool = True` — when `False`, calls to `random()`,
  `randint()`, `gauss()`, `uniform()`, `shuffle()`, `choice()`,
  `sample()` raise `EvaluationError`.
- `allow_side_effects: bool = True` — when `False`, calls to `setvar()`,
  `setvars()`, `clearvars()`, `unset()` raise `EvaluationError`.

The MCP server now sets both flags to `False` (see `mcp/server.py` for
the configuration call at first `handle_request()` invocation).
The CLI leaves them at their default `True`.

Rationale: the math_eval schema claims "Deterministically evaluate",
and unbounded state in a shared evaluator across MCP requests is a
memory DoS vector. CLI users may legitimately want randomness, so the
opt-out is per-deployment.

### C-2 — Cache poisoning

`_cached_normalize_and_evaluate` checks if the expression contains
`random(`, `randint(`, etc. (the lowercase set of `_RANDOM_FUNCTIONS`).
If so, it bypasses `functools.lru_cache` and calls
`_normalize_and_evaluate_uncached` instead. Without this, a request
for `random()` would return a cached value on the second call —
breaking the "Deterministically evaluate" promise in the other
direction (it would *not* be random, it would be a constant).

### C-3 — `MAX_INPUT_LENGTH`

`Evaluator.evaluate()` now rejects strings longer than
`MAX_INPUT_LENGTH = 10_000` before any parsing. This blocks the most
common DoS vector: extremely long expressions that force the AST
parser / tree visitor to walk millions of nodes. Also added an AST
node count cap of `MAX_AST_NODES = 10_000` to prevent small-but-deep
expressions (e.g. `1+1+1+...` with no spaces) from exhausting memory.

### H-1 — Schema `maxLength`

`math_eval.expression` schema now declares `"maxLength": 10000`. The
JSON-RPC validator returns `-32602 invalid_arguments` for any longer
expression. Verified: a 12 000-char expression is rejected at the
schema layer (no tool execution).

### H-2 — Schema `type: [...]` rejected

`_validate_value_against_schema` now raises on non-string `type` values
(including the JSON-Schema Draft 7 array form like `["string", "null"]`).
Previously these were silently treated as a no-op, which could mask
authoring errors and let through values of any type.

### H-3 — `setvar` identifier validation and cap

- `setvar(name, value)` now requires `isinstance(name, str) and
  name.isidentifier()`. Empty strings, leading digits, and keywords
  (`if`, `def`, etc.) all raise `EvaluationError`.
- `_user_variables` is now capped at `MAX_USER_VARIABLES = 1000`. When
  the cap is reached, the oldest entry is evicted (FIFO). This bounds
  memory growth across long-lived MCP sessions.

### H-4 — Docstring clarification

`mcp/server.py` had a docstring claiming "per-request thread" for
tool execution, but the actual implementation uses a bounded
`ThreadPoolExecutor(max_workers=16)`. The docstring has been updated
to describe the actual behavior. No code change was required.

### H-5 — Temperature conversion precision

The C→R conversion previously computed `491.67` as the offset, but
the true value is `273.15 * 1.8 = 491.67000000000007`. Forcing
`491.67` introduced a tiny but reproducible drift: direct
`convert_temperature(100, 'C', 'R')` returned `671.67` exactly, but
`convert_temperature(convert_temperature(100, 'C', 'K'), 'K', 'R')`
returned `671.6700000000001`. Both paths now use the
`273.15 * 1.8` form, so they agree bit-for-bit.

Also added NaN/Inf rejection to `convert_temperature` — these were
previously accepted and propagated to `math.gauss` callers with
silently garbage results.

### H-6 — `unit_convert` OverflowError catch

The handler for `unit_convert` casts the input to `float` without
`try/except`. A value of `1e400` raises `OverflowError`, which the
JSON-RPC layer reports as a generic `-32603 internal error`. Now
wrapped in `try/except (OverflowError, ValueError)` → `invalid_arguments`.

### H-7 — `dotenv_validate` subprocess isolation

Moved the actual `dotenv` parsing into `_dotenv_validate_worker`, a
top-level function executed in a child process via `multiprocessing`.
The child is launched with `RLIMIT_AS = 256 MB` (Linux only) and
joined with `REGEX_TIMEOUT_SECONDS` wall-clock. The parent uses the
existing `_SPAWN_SEMAPHORE` and orphan-process tracking pattern
(mirrors the regex worker from the 2026-06 review).

On macOS, `RLIMIT_AS` is silently a no-op, so production deployments
that need a hard memory cap should run on Linux or use a container
with a memory limit (documented in the worker docstring).

### H-8 — Schema validator extensions

`_validate_value_against_schema` now handles:

- `const` — value must equal the const literal
- `pattern` — string value must match the regex
- `exclusiveMinimum` / `exclusiveMaximum` — value must be strictly
  outside the bound
- `multipleOf` — value must be a multiple (using `math.fmod` to
  handle floats safely; rejects `multipleOf: 0`)
- `uniqueItems` — array values must have no duplicates (uses a
  `set()` round-trip; falls back to identity for unhashable items)

`type: [...]` (array form) is explicitly rejected, not silently
treated as "any".

### M-1 through M-15

See the existing 2026-06 review doc for the descriptions. All were
fixed in this batch. Test counts:

- `TestProductionReview2026_07` in `tests/test_mcp_server.py` — 23 cases
- `tests/test_clicalc.py` — no new tests (existing 768 still pass)
- Total: 1735 tests pass, 32 skipped (was 1712 + 23 = 1735)

## Verification

- `python -m pytest tests/ -q` — **1735 passed, 32 skipped** (was
  1712 + 23 from this review; baseline 2026-06 was 1674).
- `python build_single.py` — single-file build still works.
- `python eggcalc.py -e "..."` — CLI smoke tests pass:
  - `random()` → `0.3333...` (works in CLI)
  - `fact(5)` → `120` (works)
  - `setvar('x', 5)` then `x + 3` → `8` (works in CLI)
  - `5+3` → `8` (works in MCP and CLI)
- `python eggcalc.py --json "random()"` via subprocess returns a
  fresh random value (CLI mode allows random).
- Direct `from eggcalc import evaluate; evaluate('fact(5m)')` raises
  `EvaluationError: Function 'factorial()' requires a dimensionless
  argument, got value with unit 'm'`.

## Out of scope (deferred)

- L1–L9 — Polish items from the 2026-06 review.
- Async I/O work for H2 (single-threaded today is fine).
- An overall audit of every MCP tool's input bounds — this batch
  covered the 12 most-exercised tools, but additional tools may have
  similar issues that a future review can address.
