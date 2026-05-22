# evaluator.py Architecture Review

## Verified Claims

1. **Purpose**: AST-based evaluation without eval() - MATCHES (lines 1-7, 811-817)
2. **Evaluator class**: AST visitor pattern - MATCHES (line 811)
3. **Constants Registry**: Mathematical and physical constants - MATCHES (lines 820-873)
4. **Functions Registry**: All documented functions present - MATCHES (lines 876-994)
5. **Memory class**: Calculator memory registers - MATCHES (lines 664-756)
6. **PyCalcApp**: Thread-safe wrapper for webapps - MATCHES (lines 1353-1473)
7. **Node Validation (_validate_node)**: Blocks forbidden node types - MATCHES (lines 1205-1235)
8. **DoS Protection**: MAX_EXPONENT=10000, MAX_FACTORIAL=1000, MAX_NESTING_DEPTH=100, MAX_RESULT_VALUE=1e308 - ALL MATCH (lines 49-52)
9. **Complex Number Support (_complex_aware decorator)** - MATCHES (lines 614-656)
10. **Unit Handling in visit_BinOp()** - MATCHES (lines 1103-1144)
11. **Public API**: All documented functions exist - MATCHES

## Discrepancies

1. **Missing constants in documentation**:
   - `idealgasconstant` (line 835) not in arch doc
   - `avogadros` (line 832) not in arch doc
   - `echarge` (line 847) not in arch doc
   - `atomicmassunit` (line 853) not in arch doc
   - `vacuumpermittivity` (line 855) not in arch doc
   - `vacuumpermeability` (line 858) not in arch doc
   - `standardgravity` (line 860) not in arch doc
   - `gravitationalconstant` (line 863) not in arch doc
   - `rydbergconstant` (line 866) not in arch doc
   - `stefanboltzmann` (line 869) not in arch doc
   - `planckbar`/`hbar`/`reducedplanck` (lines 870-872) not in arch doc

2. **Missing functions in documentation**:
   - `degrees`, `radians` (lines 919-920) not in arch doc Functions list
   - `randrange`, `uniform` (lines 538-547) in code but not clearly documented as available

3. **Documentation structure issues**:
   - Arch doc shows constants under wrong labels (e.g., `bar` function not in code)
   - `DEFAULT_CACHE_SIZE = 1024` (line 53) not documented
   - `TimeoutError` class (line 1297) documented as exception but not as class
   - `PyCalcApp.cache_size` property (lines 1467-1473) not documented

4. **Constants values in arch doc may be outdated**:
   - `rydberg` shows 10973731.568160 but code shows 10973731.568160 (line 865) - appears correct

## Bugs Found

No bugs found. Code implementation matches documented behavior.

## Improvements

1. **High Priority**: Update architecture doc to include all constants from CONSTANTS dict
2. **High Priority**: Update architecture doc to include `degrees`, `radians`, `randrange`, `uniform` functions
3. **Medium Priority**: Add `DEFAULT_CACHE_SIZE` constant to documentation
4. **Medium Priority**: Add `TimeoutError` as a class and `PyCalcApp.cache_size` property to documentation
5. **Low Priority**: Remove erroneous `bar` function reference from architecture doc
6. **Low Priority**: Reorganize architecture doc to match actual code structure

## Priority

- **High**: Update architecture doc with missing constants and functions
- **Medium**: Add missing constant definitions and class documentation
- **Low**: Fix documentation structure issues