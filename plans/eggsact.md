# eggsact - Natural Language Math Calculator with MCP Server

## Overview

`eggsact` is a Rust re-implementation of `nl-clicalc`, a natural language math expression calculator that uses Python's standard library. This project targets the **codegg** agent coding harness, providing math and text processing tools via an MCP (Model Context Protocol) server to reduce hallucinations in AI coding agents.

### Goals
- Provide reliable math evaluation (including natural language input like "thirty plus five")
- Support unit conversions ("30m + 100ft")
- Offer text processing tools via MCP for AI agents
- Single self-contained crate with no external dependencies beyond standard library + essential crates
- Complete test suite for reliability

---

## Project Structure

```
eggsact/                       # Rust project (crate: eggsact)
├── Cargo.toml                 # Crate manifest
├── build.sh                   # Development build script
├── release.sh                 # Release build (regenerates data first)
├── src/
│   ├── main.rs                # CLI entry, --mcp mode flag
│   ├── mcp/
│   │   ├── mod.rs
│   │   ├── server.rs          # stdio JSON-RPC 2.0 server
│   │   ├── tools.rs           # 10 MCP tool implementations
│   │   └── schemas.rs         # JSON-RPC type definitions
│   ├── calc/
│   │   ├── mod.rs
│   │   ├── normalize.rs       # NL word → number conversion, tokenization
│   │   ├── evaluator.rs       # AST math expression evaluator
│   │   └── units.rs           # UnitValue, UNIT_BASE, conversions
│   └── text/
│       ├── mod.rs
│       ├── confusables.rs      # Lazy-loaded HashMap
│       ├── confusables_generated.rs  # Auto-generated 6565 entries
│       ├── diff.rs             # Levenshtein distance
│       ├── measure.rs          # Text metrics
│       └── validate.rs         # Bracket, JSON, regex validation
├── scripts/
│   └── generate_confusables.py  # Downloads Unicode confusables.txt
├── data/
│   └── confusables.rs         # Full generated file (reference)
└── tests/                     # Test suite (to be created)
    └── ...
plans/
└── eggsact.md                 # This plan document
```

---

## Current Status

### Feature Parity Matrix

| Category | Feature | nl-clicalc | eggsact |
|----------|---------|:-----------:|:------:|
| **Math** | NL parsing ("thirty plus five") | ✅ | ✅ |
| | Basic arithmetic (+, -, *, /, **, %) | ✅ | ✅ |
| | Trig functions (sin, cos, tan, etc.) | ✅ | ✅ |
| | Logarithmic (log, log10, log2, exp) | ✅ | ✅ |
| | Mathematical constants | ✅ (50+) | ✅ (minimal) |
| | Statistical (mean, median, std, sum) | ✅ | ❌ |
| | Number theory (gcd, lcm, factorial) | ✅ | ✅ |
| | Complex numbers (3+4i) | ✅ | ❌ |
| **Units** | Length, time, mass, volume | ✅ | ✅ |
| | Energy, pressure, power, force | ✅ | ✅ |
| | Temperature conversions | ✅ | ✅ |
| | Compound units (m/s) | ✅ | ❌ |
| **Text Tools** | text_measure | ✅ | ✅ |
| | text_equal (normalization) | ✅ | ✅ |
| | text_diff_explain | ✅ | ✅ |
| | text_inspect (confusables) | ✅ | ✅ |
| | text_count | ✅ | ✅ |
| | validate_brackets | ✅ | ✅ |
| | validate_json | ✅ | ✅ |
| | validate_regex | ✅ | ✅ |
| | list_compare | ✅ | ✅ |
| **Unicode** | NFC/NFD/NFKC/NFKD normalization | ✅ | ❌ |
| | Casefold comparison | ✅ | ❌ |
| | Mixed script detection | ✅ | ❌ |
| **MCP Server** | All 10 tools | ✅ | ✅ |
| **CLI** | Interactive REPL | ✅ | ❌ |
| | Extended options (--json, -i, --usage) | ✅ | ❌ |
| **Testing** | 315 tests | 43 tests (growing) |
| **Dependencies** | Zero (stdlib only) | ⚠️ (5 crates) |

---

## Feature Parity Plan

### Phase A: Missing Math Features (High Priority)

| Feature | Status | Effort | Notes |
|---------|--------|--------|-------|
| Statistical functions (mean, median, std, variance, sum, min, max) | ❌ | 1 day | Port from evaluator.py |
| Complex number support (3+4i) | ❌ | 1 day | Need `j` suffix handling |
| Physical constants (c, h, k, G, etc.) | ⚠️ partial | 0.5 day | Add ~20 more constants |
| Bitwise operations (<<, >>, &, \|, ^) | ❌ | 0.5 day | Low priority |
| Random functions (random, randint, seed) | ❌ | 0.5 day | Low priority |

### Phase B: Unicode Features (Medium Priority)

| Feature | Status | Effort | Notes |
|---------|--------|--------|-------|
| Unicode normalization (NFC/NFD/NFKC/NFKD) | ❌ | 1-2 days | Need unicode-normalization crate |
| Casefold comparison | ❌ | 0.5 day | Can use `.casefold()` |
| Mixed script detection | ❌ | 1 day | Complex logic |

### Phase C: Unit Features (Low Priority)

| Feature | Status | Effort | Notes |
|---------|--------|--------|-------|
| Compound unit parsing (m/s, kg*m/s^2) | ❌ | 1 day | Parse and evaluate |
| Unit exponents (m^2, kg^3) | ❌ | 0.5 day | Extend UnitValue |

### Phase D: CLI Enhancements (Low Priority)

| Feature | Status | Effort | Notes |
|---------|--------|--------|-------|
| Interactive REPL | ❌ | 1 day | Low priority for MCP use |
| Extended CLI options (--json, --usage) | ❌ | 0.5 day | Nice to have |

---

## Test Suite Plan

### Test Structure

```
eggsact/tests/
├── lib.rs                  # Test module root
├── calc/
│   ├── mod.rs
│   ├── test_evaluator.rs  # Math expression tests
│   ├── test_normalize.rs  # NL processing tests
│   └── test_units.rs      # Unit conversion tests
├── mcp/
│   ├── mod.rs
│   └── test_tools.rs      # MCP tool integration tests
└── text/
    ├── mod.rs
    ├── test_diff.rs       # Diff algorithm tests
    ├── test_validate.rs  # Validation tests
    └── test_confusables.rs # Confusables lookup tests
```

### Test Categories to Port

| Source File | Test Count | Focus Areas |
|------------|:----------:|-------------|
| `test_clicalc.py` | ~95 | Math expressions, constants, functions |
| `test_exact.py` | ~70 | Text tools, Unicode handling |
| `test_security_fuzz.py` | ~22 | Security limits, DoS protection |
| `test_tokenization.py` | ~54 | Edge cases in tokenization |
| `test_math_identities.py` | ~28 | Mathematical law verification |
| `test_cli_text.py` | ~15 | CLI text commands |

### Testing Approach

1. **Unit tests** - Rust `#[test]` with `#[should_panic]` for error cases
2. **Integration tests** - MCP tool testing via stdio JSON-RPC
3. **Property-based tests** - Mathematical identities (commutative, associative)
4. **Fuzz tests** - Random expression generation with bounds checking

### Rust Testing Dependencies

```toml
[dev-dependencies]
criterion = "0.3"        # Benchmarking
proptest = "1.2"          # Property-based testing
```

---

## Implementation Phases

### Phase 1: Project Setup ✅
- [x] Create `eggsact/` directory
- [x] Initialize Cargo project
- [x] Add dependencies to `Cargo.toml`
- [x] Create `build.sh` and `release.sh`
- [x] Add `eggsact/` to `.gitignore`

### Phase 2: MCP Server Foundation ✅
- [x] Implement JSON-RPC 2.0 request/response types in `schemas.rs`
- [x] Implement stdio server loop in `server.rs`
- [x] Implement `initialize`, `tools/list`, `tools/call` handlers
- [x] Implement error envelope pattern
- [x] Test with simple MCP client

### Phase 3: Math Evaluator ✅ (partial)
- [x] Implement arithmetic parser
- [x] Basic arithmetic operations
- [x] Trig and log functions
- [x] Basic constants (pi, e, tau)
- [x] Factorial and power functions
- [ ] Statistical functions (mean, median, std, variance, sum, min, max)
- [ ] Complex number support (3+4i → 3+4j)
- [ ] Additional physical constants (c, h, k, G, NA, etc.)
- [ ] DoS protection limits (fully implemented but not all tested)

### Phase 4: Natural Language Processing ✅
- [x] Port `NUMBER_WORDS` dictionary (~117 entries)
- [x] Port `OPERATOR_CONVERSIONS` dictionary
- [x] Port `FUNCTION_MAPPINGS` dictionary
- [x] Implement tokenization with operator splitting
- [x] Implement single-pass word substitution
- [x] Implement phrase stripping
- [ ] Combinatorial NL for compound numbers ("sixteen thousand five hundred twenty two")

### Phase 5: Unit Handling ✅
- [x] Port `UNIT_BASE` table (~150 units across 15 categories)
- [x] Implement `UnitValue` struct with arithmetic
- [x] Implement temperature offset handling
- [x] Implement automatic unit conversion on add/subtract
- [ ] Compound unit parsing (m/s, kg*m/s^2)

### Phase 6: Text Processing Tools ✅
- [x] `text_measure` (length, words, lines, etc.)
- [x] `text_equal` (normalization, Unicode-aware)
- [x] `text_diff_explain` (Levenshtein with codepoints)
- [x] `text_inspect` (hidden chars, confusables)
- [x] `text_count` (char counting, frequency)
- [x] `validate_brackets` (balanced parens/brackets)
- [x] `validate_json` (JSON parsing)
- [x] `validate_regex` (regex matching)
- [x] `list_compare` (list diff with options)
- [ ] Unicode normalization (NFC/NFD/NFKC/NFKD)
- [ ] Casefold comparison
- [ ] Mixed script detection

### Phase 7: Test Suite Construction
- [x] Create `tests/` directory structure
- [x] Add `cargo test` infrastructure
- [x] Port `test_clicalc.py` → `tests/calc/test_evaluator.rs`
- [ ] Port `test_tokenization.py` → `tests/calc/test_normalize.rs`
- [ ] Port unit tests → `tests/calc/test_units.rs`
- [ ] Port `test_exact.py` text tests → `tests/text/`
- [ ] Port `test_security_fuzz.py` → security bounds tests
- [ ] Port `test_math_identities.py` → property-based tests
- [x] Add MCP integration tests via stdio

### Phase 8: Integration & Polish
- [ ] Performance testing
- [ ] Memory profiling
- [ ] CLI REPL (optional)
- [ ] Documentation

---

## Effort Estimate

| Phase | Component | Days |
|-------|-----------|------|
| 1 | Project Setup | 0.5 |
| 2 | MCP Server | 1-2 |
| 3 | Math Evaluator (missing features) | 2-3 |
| 4 | NL Processing | 1 |
| 5 | Units (compound) | 1 |
| 6 | Text Processing (Unicode) | 2-3 |
| 7 | Test Suite Construction | 2-3 |
| 8 | Integration & Polish | 1-2 |
| **Total** | | **10-15 days** |

---

## Dependencies

### Current

```toml
[dependencies]
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
regex = "1.10"
once_cell = "1.19"
ahash = "0.8"
```

### Potential Additions for Full Parity

```toml
[dependencies]
# For Unicode normalization (if needed)
unicode-normalization = "1.0"

[dev-dependencies]
criterion = "0.3"        # Benchmarking
proptest = "1.2"          # Property-based testing
```

---

## API Reference

### MCP Server

```rust
// Entry point
pub fn main() -> !

// Request types
#[derive(Deserialize)]
pub struct JsonRpcRequest {
    pub jsonrpc: String,
    pub method: String,
    pub params: Option<Value>,
    pub id: Option<Value>,
}

// Response types
#[derive(Serialize)]
pub struct JsonRpcResponse {
    pub jsonrpc: String,
    pub result: Value,
    pub id: Option<Value>,
}

// Tool envelope
#[derive(Serialize)]
pub struct ToolResponse {
    pub ok: bool,
    pub result: Option<Value>,
    pub error_type: Option<String>,
    pub error: Option<String>,
    pub hints: Option<Vec<String>>,
}
```

### Calculator

```rust
pub fn run(expr: &str) -> Result<String, String>
pub fn evaluate(expr: &str) -> Result<String, String>
pub fn normalize(expr: &str) -> Result<String, String>
```

### Units

```rust
pub struct UnitValue {
    pub value: f64,
    pub unit: Option<String>,
}

impl UnitValue {
    pub fn convert_to(&self, target: &str) -> Result<UnitValue, String>
}
```

---

## File Manifest

```
eggsact/
├── Cargo.toml
├── build.sh
├── release.sh
├── src/
│   ├── main.rs
│   ├── lib.rs
│   ├── mcp/
│   │   ├── mod.rs
│   │   ├── server.rs
│   │   ├── tools.rs
│   │   └── schemas.rs
│   ├── calc/
│   │   ├── mod.rs
│   │   ├── normalize.rs
│   │   ├── evaluator.rs
│   │   └── units.rs
│   └── text/
│       ├── mod.rs
│       ├── confusables.rs
│       ├── confusables_generated.rs  # Auto-generated (6565 entries)
│       ├── diff.rs
│       ├── measure.rs
│       └── validate.rs
├── scripts/
│   └── generate_confusables.py
├── data/
│   └── confusables.rs
└── tests/                     # To be created
plans/
└── eggsact.md
```

---

## Appendix: Original nl-clicalc Architecture

For reference, the original Python project's key modules:

| Module | Purpose |
|--------|---------|
| `nl_calc/normalize.py` | NL tokenization, number word conversion, expression normalization |
| `nl_calc/evaluator.py` | AST parsing and evaluation, mathematical operations |
| `nl_calc/units.py` | Unit definitions, conversion factors, temperature conversions |
| `nl_calc/mcp/server.py` | stdio JSON-RPC request handling |
| `nl_calc/mcp/tools.py` | 10 MCP tool implementations |
| `nl_calc/mcp/schemas.py` | Type schemas |
| `nl_calc/exact/confusables.py` | Unicode confusables table (6581 lines, auto-generated) |

### Original Test Files

| File | Tests | Description |
|------|:-----:|-------------|
| `tests/test_clicalc.py` | ~95 | Core calculator functionality |
| `tests/test_exact.py` | ~70 | Exact text/Unicode tools |
| `tests/test_security_fuzz.py` | ~22 | Security and fuzzing |
| `tests/test_tokenization.py` | ~54 | Tokenization edge cases |
| `tests/test_math_identities.py` | ~28 | Mathematical law verification |
| `tests/test_cli_text.py` | ~15 | CLI text commands |
| **Total** | **315** | |
