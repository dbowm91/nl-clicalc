# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-20

### Added
- New configuration constants for fine-tuned control:
  - `MAX_NESTING_DEPTH` - Maximum parentheses nesting depth
  - `MAX_FACTORIAL` - Maximum factorial input to prevent DoS
  - `MAX_RESULT_VALUE` - Maximum result value
  - `DEFAULT_CACHE_SIZE` - Default LRU cache size
- `FLOAT_EPSILON` constant in units.py for float comparisons
- Export of new constants in `__all__`
- Python 3.13 support in pyproject.toml

### Changed
- `factorial()` now has input bounds checking (max 1,000)
- `cbrt()` now correctly handles negative numbers
- Cache clearing now only happens on non-EvaluationError exceptions
- Nesting depth is now validated in normalize()
- Named constants used throughout instead of magic numbers

### Fixed
- Thread-safe access to user variables with lock in `visit_Name()`
- Float equality uses named `FLOAT_EPSILON` constant

### Security
- Added bounds checking for factorial to prevent DoS via large factorial inputs
- Fixed cbrt negative number handling
- Added nesting depth limits

## [1.0.0] - 2026-01-15

### Added
- Initial release
- Natural language expression parsing
- Unit conversions (length, time, data, mass, volume, pressure, energy, power)
- Scientific functions (trig, hyperbolic, log, exp)
- Physical constants
- Complex number support
- Bitwise operations
- Statistical functions
- Prime number utilities
- Memory registers and variables
- Webapp support with caching and async
- AST-based safe evaluation
- CLI with interactive REPL mode
