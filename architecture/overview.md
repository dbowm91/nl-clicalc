# Architecture Overview

nl-clicalc is a natural language math expression calculator that uses only Python's standard library.

## System Architecture

```
                                    ┌─────────────────────────────────────────┐
                                    │              nl_calc.__init__            │
                                    │   (Public API surface, re-exports)     │
                                    └─────────────────────────────────────────┘
                                                       │
                ┌──────────────────────────────────────┼──────────────────────────────────────┐
                │                                      │                                      │
                ▼                                      ▼                                      ▼
┌───────────────────────────────────────┐  ┌───────────────────────────────────────┐  ┌───────────────────┐
│            normalize.py               │  │            evaluator.py                 │  │     units.py      │
│   (NL parsing, text normalization)    │  │   (AST-based expression evaluation)   │  │ (Unit definitions)│
└───────────────────────────────────────┘  └───────────────────────────────────────┘  └───────────────────┘
                │                                      │
                │          ┌───────────────────────────┘
                │          │
                ▼          ▼
┌───────────────────────────────────────────────────────┐
│                    exact/                              │
│   (Unicode text inspection tools)                    │
│   ┌──────────┬──────────┬──────────┬──────────┐      │
│   │primitives│unicode_  │ confusables│ validate │     │
│   │          │ tools    │           │          │      │
│   └──────────┴──────────┴──────────┴──────────┘      │
│   ┌──────────┬──────────┬──────────┐                  │
│   │  diff    │ measure  │synthesis │                  │
│   └──────────┴──────────┴──────────┘                  │
└───────────────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────┐
│                     mcp/                              │
│   (MCP server for AI agent tool access)              │
│   ┌──────────┬──────────┬──────────┐                  │
│   │ server   │  tools   │ schemas │                  │
│   └──────────┴──────────┴──────────┘                  │
└───────────────────────────────────────────────────────┘
```

## Processing Pipelines

nl-clicalc supports two evaluation paths:

### 1. Full Pipeline (for Natural Language Input)

```
Input → normalize() → normalize_expression() → evaluate() → Result
```

Steps:
1. **Normalization** (`normalize.py`): Convert natural language to Python syntax
2. **Tokenization**: Split expression at operator boundaries
3. **Unit Preprocessing**: Add multiplication before units (e.g., `30m` → `30*m`)
4. **AST Evaluation** (`evaluator.py`): Parse and evaluate the normalized expression

### 2. Direct Evaluation (for Pre-normalized Input)

```
Input → evaluate() → Result
```

Skips normalization, directly parses via Python AST. Used when input is already normalized.

## Core Modules

| Module | Purpose |
|--------|---------|
| [normalize.py](normalize.md) | Natural language tokenization, number word conversion, expression normalization |
| [evaluator.py](evaluator.md) | AST parsing and evaluation, mathematical operations |
| [units.py](units.md) | Unit definitions, conversion factors, temperature conversions |
| [__main__.py](cli.md) | CLI entry point |
| [__init__.py](api.md) | Public API surface |

## Supporting Modules

## Supporting Modules

### exact/ - Text Inspection Tools

Provides low-level Unicode text primitives for detecting hidden characters, confusables, and text metrics.

| Module | Purpose |
|--------|---------|
| [primitives.md](primitives.md) | UTF-8 encoding, codepoint iteration, Unicode normalization |
| [unicode_tools.md](unicode_tools.md) | Script detection, confusable character detection |
| [confusables.md](confusables.md) | Confusable character identification (homoglyphs) |
| [validate.md](validate.md) | JSON/bracket/regex validation |
| [diff.md](diff.md) | String diffing algorithms |
| [measure.md](measure.md) | Text metrics (words, lines, categories) |
| [synthesis.md](synthesis.md) | Higher-level text analysis tools |

### mcp/ - MCP Server

Model Context Protocol server for exposing text tools to AI agents.

| Module | Purpose |
|--------|---------|
| [mcp_server.md](mcp_server.md) | MCP server implementation |
| [server.md](mcp_server.md) | stdio-based MCP request handling |
| [tools.md](mcp_server.md) | MCP tool definitions |
| [schemas.md](mcp_server.md) | JSON schemas for MCP tool definitions |

## Data Structures

### Key Constants and Mappings

- **`NUMBER_WORDS`** - Dictionary mapping number values to word variants ("one" → "1", "five" → "5")
- **`OPERATOR_CONVERSIONS`** - Maps operator words to symbols ("plus" → "+")
- **`UNIT_BASE`** - Base units and their conversion factors
- **`UNIT_CONVERSIONS`** - Cached pairwise conversion factors
- **`UNIT_ALIASES`** - Maps all unit variants to canonical forms
- **`FUNCTION_MAPPINGS`** - Maps function name variants to canonical names

### Types

- **`UnitValue`** - Represents a numeric value with optional units (`60.48 m`)
- **`EvaluationError`** - Raised when an expression is invalid
- **`TimeoutError`** - Raised when evaluation exceeds timeout

## Security Model

nl-clicalc uses AST-based parsing instead of `eval()`:
- No arbitrary code execution
- Controlled function access via whitelist
- Built-in DoS protection (max nesting, exponent, factorial limits)
- Timeout support for untrusted input

## Build Process

The codebase is designed to be assembled into a **single self-contained Python script**:

1. **`build_single.py`** - Combines modules into `nl_calc.py`
2. **`install.py`** - Calls `build_single.py` then installs to `~/.local/bin/calc`

All code must be in one of the core modules for assembly to work.

## Index

- [normalize.md](normalize.md) - Natural language processing pipeline
- [evaluator.md](evaluator.md) - AST-based expression evaluator
- [units.md](units.md) - Unit definitions and conversions
- [cli.md](cli.md) - Command-line interface
- [api.md](api.md) - Public API surface
- [primitives.md](primitives.md) - Unicode text primitives
- [unicode_tools.md](unicode_tools.md) - Script and confusable detection
- [confusables.md](confusables.md) - Homoglyph identification table
- [validate.md](validate.md) - Validation utilities
- [diff.md](diff.md) - String diffing algorithms
- [measure.md](measure.md) - Text measurement
- [synthesis.md](synthesis.md) - Text analysis synthesis
- [mcp_server.md](mcp_server.md) - MCP server implementation