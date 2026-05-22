# Architecture Overview

nl-clicalc is a natural language math expression calculator that uses only Python's standard library. It parses math expressions in English ("five plus three") and converts them to numeric results, with support for unit conversions.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              nl_calc                                       │
│                    (Single-file build output)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  normalize   │  │  evaluator   │  │    units     │  │     mcp      │  │
│  │   (NL→math)  │  │  (AST eval)  │  │  (converts)  │  │   (server)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│                              │                                              │
│                              ▼                                              │
│                    ┌──────────────────┐                                   │
│                    │      exact/       │                                   │
│                    │  (text tools)     │                                   │
│                    └──────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Calculator Pipeline

| Component | File | Purpose |
|-----------|------|---------|
| **Normalize** | [normalize.md](normalize.md) | Converts NL expressions to normalized math strings |
| **Evaluator** | [evaluator.md](evaluator.md) | AST-based safe expression evaluation |
| **Units** | [units.md](units.md) | Unit definitions and conversion |
| **CLI** | [cli.md](cli.md) | Command-line interface |

### 2. Text/Unicode Tools (exact/)

Low-level Unicode text primitives for detecting hidden characters, confusables, and text metrics.

| Module | Purpose |
|--------|---------|
| [primitives.md](primitives.md) | UTF-8 encoding, codepoint iteration, Unicode normalization |
| [unicode_tools.md](unicode_tools.md) | Script detection, confusable character detection |
| [confusables.md](confusables.md) | Confusable character identification (homoglyphs) |
| [validate.md](validate.md) | JSON/bracket/regex validation |
| [diff.md](diff.md) | String diffing algorithms |
| [measure.md](measure.md) | Text metrics (words, lines, categories) |
| [synthesis.md](synthesis.md) | Higher-level text analysis tools |

### 3. MCP Server (mcp/)

Model Context Protocol server for AI agent tool access via stdio.

| Module | Purpose |
|--------|---------|
| [mcp_server.md](mcp_server.md) | MCP server implementation, JSON-RPC request handling |

## Processing Pipelines

### Full Pipeline (Natural Language Input)

```
Input → run() → normalize_expression() → normalize() → evaluate() → Result
```

1. **run()** - Orchestrates the full pipeline
2. **normalize_expression()** - Tokenizes, converts words, handles functions
3. **normalize()** - Final cleanup (percentages, complex suffix, whitespace)
4. **evaluate()** - AST parsing and evaluation

### Direct Evaluation (Pre-normalized Input)

```
Input → evaluate() → Result
```

Skips normalization, directly parses via Python AST. Used when input is already normalized.

### Unit Conversion Pipeline

```
Input → run() → _handle_unit_conversion_from_tokens() → convert() → Result
```

Detects patterns like `2m in feet` and generates `convert(2*m, ft)` calls.

## Data Flow

```
                    ┌─────────────────┐
                    │   User Input    │
                    │ "30m + 100ft"  │
                    └────────┬────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   normalize.normalize()        │
              │   - word_to_operator          │
              │   - word_to_number            │
              │   - percentage handling      │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   normalize_expression()     │
              │   - split_at_operators      │
              │   - convert_from_human      │
              │   - apply_math_functions   │
              │   - _preprocess_units       │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   evaluator.evaluate()       │
              │   - AST parse               │
              │   - visit_* methods        │
              │   - UnitValue arithmetic   │
              └──────────────┬───────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Result      │
                    │   130.48 m      │
                    └─────────────────┘
```

## Key Data Structures

### NUMBER_WORDS
Maps number values to word variants:
- `1` → ["one"]
- `100` → ["hundred"]
- `1000` → ["thousand"]

### OPERATOR_CONVERSIONS
Maps operator words to symbols:
- `"+"` → ["plus", "positive"]
- `"*"` → ["times", "multiplied by", "of"]

### UNIT_BASE
Base units with conversion factors to canonical form:
- `m` (meters) with conversions to km, cm, ft, in, etc.

### UNIT_ALIASES
Maps all unit variants to canonical forms:
- `"kilometer"` → `"km"`
- `"feet"` → `"ft"`

### FUNCTION_MAPPINGS
Maps function name variants to canonical names:
- `"square root"` → `"sqrt"`
- `"absolute"` → `"abs"`

## Security Model

1. **AST-based evaluation** - No `eval()`, only whitelisted operations
2. **Node validation** - Forbidden node types blocked (Lambda, Subscript, etc.)
3. **DoS protection** - Limits on exponent (10000), factorial (1000), nesting (100)
4. **Timeout support** - `evaluate_with_timeout()` for untrusted input
5. **Unit safety** - Incompatible units raise errors on add/subtract

## Build Process

```
build_single.py                    nl_calc.py
─────────────────────────►  ─────────────────────────────
                              - units.py (inlined)
                              - evaluator.py (inlined)
                              - normalize.py (inlined)
                              - exact/* (inlined)
                              - mcp/* (inlined)
```

The `build_single.py` script combines all modules into a single `nl_calc.py` for portability.

## Index

### Core Modules
- [normalize.md](normalize.md) - NL processing pipeline
- [evaluator.md](evaluator.md) - AST-based evaluator
- [units.md](units.md) - Unit definitions and conversions
- [cli.md](cli.md) - Command-line interface

### Supporting Modules
- [primitives.md](primitives.md) - Unicode text primitives
- [unicode_tools.md](unicode_tools.md) - Script and confusable detection
- [confusables.md](confusables.md) - Homoglyph identification
- [validate.md](validate.md) - Validation utilities
- [diff.md](diff.md) - String diffing algorithms
- [measure.md](measure.md) - Text measurement
- [synthesis.md](synthesis.md) - Text analysis synthesis
- [mcp_server.md](mcp_server.md) - MCP server implementation