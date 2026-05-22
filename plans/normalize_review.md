# normalize.py Architecture Review

## Verified Claims

| Claim | Status |
|-------|--------|
| Module entry point for NL input | ✓ Verified |
| Number word conversion ("five" → 5) | ✓ Verified |
| Operator word conversion ("plus" → +) | ✓ Verified |
| Function name normalization ("square root" → sqrt) | ✓ Verified |
| Physical constant words ("avogadro" → 6.022e23) | ✓ Verified |
| Unit suffix parsing ("30m" → number 30 with unit m) | ✓ Verified |
| Filler phrase stripping | ✓ Verified |
| AST-based evaluation (no eval) | ✓ Verified |
| Input length limits (MAX_INPUT_LENGTH=10000) | ✓ Verified |
| Nesting depth limits (MAX_NESTING_DEPTH=100) | ✓ Verified |
| `run()` calls `normalize()` then `evaluate()` | ✓ Verified |
| `_build_config()` sorts by length descending | ✓ Verified |

## Discrepancies

### 1. Architecture文档声明 `check_if_number()` 返回 `tuple[str, bool, type]`，但实际返回 `dict`

**文档 (architecture/normalize.md:136-146):**
```python
{
    "bool": True/False,
    "converted": parsed_number_or_original,
    "type": type(token)
}
```
**实现 (normalize.py:388-472):** 确实返回同样的 dict 结构

**结论:** 文档与实现一致，但文档声明的是"Returns:"格式而非具体dict格式

### 2. STRIPPED_PHRASES 文档示例不完整

**文档 (normalize.md:94-108):** 只显示了部分短语
**实现 (normalize.py:264-276):** 包含 "tell me", "give me", "the " 等文档未列出的短语

**结论:** 实现比文档更完整，文档需要更新

### 3. OPERATOR_CONVERSIONS 文档示例有误

**文档 (normalize.md:35-46):**
```python
"**": ["^", "raised to", "to the power of"],
```
**实现 (normalize.py:106):**
```python
"**": ["^", "raised to", "raised to the power", "to the power of"],
```
**实现多了 "raised to the power"**

**结论:** 文档遗漏了一个变体

### 4. Module Dependencies 文档 (normalize.md:225-232) 声称导入

**文档列出的导出 (normalize.md:18-29):**
```python
from nl_calc.normalize import (
    evaluate,        # ❌ 不在 normalize.py - 在 evaluator.py
    EvaluationError, # ❌ 不在 normalize.py - 在 evaluator.py
    UnitValue,       # ❌ 不在 normalize.py - 在 units.py
    run,
    ...
)
```

**实际 `__all__` (normalize.py:27-40):**
```python
__all__ = [
    "evaluate",        # ✓ 重新导出 from evaluator
    "EvaluationError", # ✓ 重新导出 from evaluator  
    "UnitValue",       # ✓ 重新导出 from units
    "run",
    ...
]
```

**结论:** 虽然这些来自子模块，但 `normalize.py` 确实通过重新导出提供了它们

## Bugs Found

### BUG 1: `combine_number_parts()` 对 10-19 的处理逻辑错误 (High)

**位置:** normalize.py:493-521

**问题:** 当处理 "ten six" (10 + 6) 时，逻辑产生错误结果:
- i=0: part=10, 检查 i+1=6 (不是10), part!=10 → append "10"
- i=1: part=6, 检查 i+1 不存在... 但 part < 10 且 number_parts[i-1]=10 not < 10

对于 "ten six":
- 第一部分 10，第二部分 6
- 结果应该是 "10+6" 但逻辑可能产生意外结果

**根本原因:** 函数设计用于处理 "three hundred twenty two" (322) 类型的组合，但对简单数字序列处理不当

### BUG 2: `_handle_negative_token()` 在边界情况下可能越界 (Medium)

**位置:** normalize.py:650-660

**问题:** 函数直接访问 `tokens[index-2]` 和 `tokens[index-1]`，但调用处的检查 `index >= 2` 是必要的但可能不足

```python
def _handle_negative_token(tokens: list, index: int, patterns: ...) -> tuple[list, list]:
    temp = tokens[index].split("-")
    tokens[index - 2] = f"{tokens[index - 2]}.{temp[0]}"  # 无边界检查
    tokens[index - 1] = ""  # 无边界检查
    tokens[index] = f"-{temp[1]}"
    return tokens, [index - 1]
```

如果 `index < 2` 但前序检查通过，可能导致 IndexError

### BUG 3: `_should_handle_inline_negative()` 检查逻辑可能产生误判 (Medium)

**位置:** normalize.py:668-677

**问题:** `patterns["inline_negative"].match(tokens[index])` 要求整个 token 匹配 `^[a-zA-Z]+-[a-zA-Z]+$`，但后续检查 `tokens[index-1]` 是 "."，这在合理输入下几乎不可能同时满足

### BUG 4: `convert_numbers()` 返回类型不一致 (Low)

**位置:** normalize.py:524-551

**问题:** 
- 成功时返回 `str(evaluate(...))` 或 `str(result.value)` (字符串)
- 失败时返回原始 token `number_info[0]` (可能是字符串或带 "@" 的部分替换)
- 无效时返回空字符串 `""`

这导致调用处处理复杂

## Improvements

### IMPROVEMENT 1: 文档与实现同步 (High)

**优先级:** High

**建议:** 更新 `architecture/normalize.md`:
1. 补充完整的 `STRIPPED_PHRASES` 列表
2. 修正 `OPERATOR_CONVERSIONS` 中的 `"raised to the power"` 变体
3. 添加 `__all__` 重新导出子模块 exports 的说明

### IMPROVEMENT 2: 改进 `combine_number_parts()` 的边界情况处理 (High)

**优先级:** High

**建议:** 函数应明确处理:
- 只有单个数字
- 数字序列 "X Y Z" 全部 < 10
- "ten" 后面跟其他数字的特殊情况

### IMPROVEMENT 3: 添加类型注解到 `check_if_number()` 返回值 (Medium)

**优先级:** Medium

**建议:** 使用 TypedDict 使返回类型更明确:
```python
class NumberCheckResult(TypedDict):
    bool: bool
    converted: Any
    type: type
```

### IMPROVEMENT 4: `_handle_negative_token()` 添加边界保护 (Medium)

**优先级:** Medium

**建议:** 在函数内部添加断言或边界检查:
```python
def _handle_negative_token(tokens: list, index: int, patterns: ...) -> tuple[list, list]:
    assert index >= 2, "index must be >= 2"
    ...
```

### IMPROVEMENT 5: 简化 `_should_handle_inline_negative()` 逻辑 (Low)

**优先级:** Low

**建议:** 删除或重写这个函数的检查，因为它匹配的条件在实践中很少见

### IMPROVEMENT 6: 添加单元测试覆盖边界情况 (Medium)

**优先级:** Medium

**建议:** 为以下场景添加测试:
- "ten six" → 16
- "five minus ten" → -5
- "one hundred ten" → 110
- 嵌套括号边界 "((((1+1))))"