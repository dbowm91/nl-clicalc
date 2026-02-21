# Welcome to nl-clicalc

A natural language math expression calculator that converts spoken expressions into mathematical operations.

## Features

- **Natural Language Input**: Write math expressions in plain English
- **Unit Conversions**: Seamlessly convert between metric and imperial units
- **Scientific Functions**: Support for trigonometric, logarithmic, and other mathematical functions
- **Physical Constants**: Built-in scientific constants (Avogadro, Planck, Boltzmann, etc.)
- **Safe Evaluation**: Uses AST-based parsing instead of `eval()` for security
- **Pure Python**: No external dependencies - uses only the standard library
- **Webapp Ready**: Thread-safe with caching, async support, and optimized performance

## Quick Example

```bash
$ calc "five plus two"
5+2 -> 7

$ calc "30m + 100ft"
30*m+100*ft -> 60.48 m

$ calc "sin of pi"
math.sin(pi) -> 0.0
```

## Installation

```bash
pip install nl-clicalc
```

## Next Steps

- [Quick Start](quickstart.md) - Get up and running quickly
- [CLI Usage](cli.md) - Learn all command-line options
- [Python API](api.md) - Use nl-clicalc in your Python code
- [Functions](functions.md) - Explore available functions
- [Units](units.md) - See supported units and conversions
