# Production Code Review — 2026-06-05

## Status: COMPLETED

Review of `eggcalc` for production use, with focus on the MCP server, the
public math_eval / unit_convert / unit_info / constant_lookup surface, and
AST evaluator safety. All fixes are standard-library only.

## Findings (priority order)

| ID  | Severity   | File                              | Status   | Summary |
|-----|------------|-----------------------------------|----------|---------|
| C1  | Critical   | `eggcalc/evaluator.py:2113,2125`  | Fixed    | `queue.Empty` shadowing bug |
| C2  | Critical   | `eggcalc/evaluator.py`            | Fixed    | `polar` exposed with wrong arity |
| C3  | Critical   | `eggcalc/evaluator.py`            | Documented | `RLIMIT_AS` silently no-op on macOS |
| M2  | Critical   | `eggcalc/normalize.py:853`        | Fixed    | `str.replace` substring match |
| H1  | High       | `eggcalc/mcp/server.py:771`       | Fixed    | `bool` `requestId` accepted |
| H4  | High       | `eggcalc/mcp/server.py:541`       | Fixed    | 4-worker `ThreadPoolExecutor` DoS |
| H5  | High       | `eggcalc/evaluator.py:2153`       | Fixed    | Orphan-process set unbounded |
| M1  | Medium     | `eggcalc/mcp/schemas.py`          | Deferred | `unit_info` arg-name hint (polish) |
| M6  | Medium     | `eggcalc/mcp/schemas.py:65`       | Fixed    | `unit_convert` accepts `nan`/`inf` |

## Changes

### C1 — `queue.Empty` shadowing
Replaced `import queue` + `queue.Empty` reference with a module-level
`from queue import Empty as _QueueEmpty` so the local `queue: multiprocessing.Queue`
variable cannot shadow the module attribute.

### C2 — `polar()` arity
Added `_polar_from_coords(r, phi)` wrapper that returns the (r, phi) tuple
and rejects negative r. Bound the public name `polar` to the wrapper; the
internal `_polar(z: complex)` helper remains for callers that already
have a complex number.

### C3 — `RLIMIT_AS` on macOS
Expanded the docstring and inline comment on
`_evaluate_with_timeout_worker` to make the platform-specific behavior
explicit. Production deployments needing a hard memory cap should run
the MCP server on Linux or pair it with a cgroup/jail container limit.

### M2 — `convert_from_human_handler` substring bug
Replaced `str.replace` with `re.sub(rf"\b{re.escape(word)}\b", ...)` so
substrings inside other words ("one" inside "None", "Phone", "stone",
"done") are not mutated. Bare number words still convert normally.

### H1 — `bool` `requestId` in `notifications/cancelled`
Added `and not isinstance(cancelled_id, bool)` to the type guard so
`True`/`False` are not silently treated as integer ids `1`/`0`.

### H4 — Per-request thread for tool execution
Removed the 4-worker `_SHARED_EXECUTOR` and `_running_futures` set. Each
`tools/call` now spawns a dedicated daemon `threading.Thread` and joins
it with `MAX_TOOL_TIMEOUT_SECONDS` wall-clock. If the thread has not
returned after the timeout, the request is reported as timed out and the
thread continues in the background to drain child processes naturally.

### H5 — Orphan-process cap
Each orphan set (`_orphaned_eval_processes` in `evaluator.py`,
`_orphaned_regex_processes` in `mcp/tools.py`) is now paired with an
FIFO `_orphaned_*_order` list. When the cap (`MAX_ORPHANED_PROCESSES=256`
or `MAX_ORPHANED_REGEX_PROCESSES=256`) is reached, the oldest entry is
evicted on insert.

### M6 — NaN/Inf rejection
Extended `_validate_value_against_schema` to reject `math.isnan` and
`math.isinf` for any `number`/`integer` argument. Existing tests for
`unit_convert(value=inf)` and `unit_convert(value=nan)` were relaxed to
accept either the schema-level JSON-RPC error or the handler-level
`isError: True` result.

## New tests

- `tests/test_normalize.py::TestNumberWordSubstringBoundary` — 5 cases
  (None, Phone, stone, bare `one`, compound `twenty one`).
- `tests/test_mcp_server.py::TestProductionReview2026_06` — 8 cases
  (NaN/inf rejection, polar r/phi signature, polar negative r,
  orphan-set caps, bool requestId, per-request thread).

## Deferred

- H2 — `_cancelled_requests` lock (single-threaded today; defer until
  async I/O is added).
- H3 — Pin float `id` round-trip in tests (behavior is already correct;
  covered implicitly by the existing schema validation).
- H6 — `_validate_value_against_schema` enforcing `default` (defaults
  are Python kwargs; the schema `default` is documentation only).
- L1–L9 — Polish items; not blocking.
- M1 — "Did you mean" hint for `unit_info`/`constant_lookup` unknown
  arg names (would need a small change to schema validation flow;
  current behavior already rejects the call with a clear error).

## Verification

- `python -m pytest tests/ -q` — 1674 passed, 32 skipped, 0 failed
  (baseline was 1231 pass + 32 skipped; +430 tests from existing
  additions, +13 new tests from this review).
- `python build_single.py` — single-file build still works.
- `python eggcalc.py -e "..."` — CLI smoke tests pass:
  - `five plus three` → `8`
  - `30m + 100ft` → `60.480000000000004 m`
  - `polar(1, 0)` → `(1.0, 0.0)`
  - `1km in m` → `1000.0 m`
