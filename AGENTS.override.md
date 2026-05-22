# AGENTS.override.md

## Session-Specific Overrides and Extensions

This file contains overrides and additions specific to this codebase. Items here take precedence over AGENTS.md.

### Verified/Corrected Information

The following items have been verified against the codebase and should be considered accurate:

1. **`evaluate_cached` in `__all__`** - Already present at `evaluator.py:34`
2. **`get_default_evaluator` in `__all__`** - Already present at `__init__.py:96`
3. **`mps` is in UNIT_CATEGORIES** - Already present at `units.py:1206` as `"m/s": "speed"` and aliases map `"mps"` to `"m/s"` at line 953

### Critical Bugs Requiring Fix

When implementing fixes, refer to `plans/plan.md` for detailed instructions. Key items:

**Wave 1 (Must fix sequentially):**
- **1.1 UNIT_ALIASES**: `"kN": "N"` should be `"kN": "kN"` (lines 900-931 in units.py)
- **1.2 Temperature offset**: `-17.777778` should be `-32.0/1.8` (line 1038 in units.py)
- **1.3 Newline detection**: `"\r" not in "\n"` is broken (lines 45-62 in measure.py)
- **1.4 RegexTestResult**: Missing `error` field (lines 50-53, 237-241 in validate.py)
- **1.5 CLI --mcp**: Missing from normalize.py argparse (lines 1215-1268)

**Wave 2 (Can parallelize with Wave 1):**
- **2.1 MCP double-wrapped response** in server.py
- **2.2 math_eval missing MAX_TEXT_LENGTH** in tools.py
- **2.4 invisibles_detected=False** hardcoded in synthesis.py:280
- **2.5 Space-separated unit conversion** broken in normalize.py

**Wave 3 (Exact module fixes):**
- **3.1 visible_repr() VS order** - check VS before combining marks (primitives.py:272-275)
- **3.2 visible_repr() missing WORD JOINER** - add case for U+2060 (primitives.py:269-285)
- **3.3 _get_script_heuristic needs @lru_cache** (unicode_tools.py:61-95)

### Implementation Guidance

When fixing the UNIT_ALIASES bug (1.1), each prefixed unit should map to itself, not the base unit:
```python
# Force
"kN": "kN",  # was "N"
"dyne": "dyne",  # was "N"
# Voltage
"kV": "kV",  # was "V"
"mV": "mV",  # was "V"
# Current
"mA": "mA",  # was "A"
```

For newline detection fix (1.3), the correct approach is to count standalone CR and LF:
```python
standalone_cr = s.count("\r") - s.count("\r\n")
standalone_lf = s.count("\n") - s.count("\r\n")
if standalone_cr > 0 and standalone_lf > 0:
    return "mixed"
```

For visibles_repr() fix (3.1), VS check must come BEFORE combining mark check:
```python
elif 0xfe00 <= ord(char) <= 0xfe0f:
    result.append("⟦VS⟧")
elif unicodedata.category(char).startswith("M"):
    result.append(f"◌{char}")
```

### Verification Commands

After implementing Wave 1 fixes:
```bash
python -c "from nl_calc.units import get_conversion_factor; print(get_conversion_factor('kN', 'N'))"  # Should be 1000.0
python -c "from nl_calc.units import convert_temperature; print(convert_temperature(32, 'F', 'C'))"  # Should be 0.0
python -c "from nl_calc.exact.measure import line_metrics; print(line_metrics('a\r\nb').newline_style)"  # Should be CRLF
python -m nl_calc --help | grep mcp  # Should show --mcp flag
```

### Known Resolved Items

These items from past discussions have been verified as already correct:
- `evaluate_cached` is exported in `__all__`
- `get_default_evaluator` is exported in `__all__`
- `mps` exists in UNIT_BASE and aliases to "m/s"
- `utf8_bytes()` correctly returns `bytes` object (not int count)