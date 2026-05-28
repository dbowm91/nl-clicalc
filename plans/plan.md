# nl-clicalc Implementation Plan

## Status: COMPLETED

All waves 1-7 implemented. All deferred items resolved or properly deferred.

---

## Completed Items (Historical)

### Wave 1: Critical Bugs
- Fixed `split_at_operators` multi-word number combining
- Fixed `combine_number_parts` logic

### Wave 2-7
All verified complete. See git log for details.

### Deferred Items (Resolved 2026-05-28)

| Item | Description | Resolution |
|------|-------------|------------|
| D1 | Reverse confusable lookup | **Implemented** - `reverse_confusables()` in unicode_tools.py with cached inverted index |
| D2 | `unicode_normalization_only` unreachable | **Not a bug** - Reachable in `_classify_difference()` when NFC equal but raw bytes differ and casefold equal |
| D3 | Dead `include_codepoints` in MCP text_measure | **Fixed** - Removed dead parameter from schema and tool function |
| D5 | Performance review for confusables_count | **Deferred** - O(n) with O(1) lookups is optimal; no action needed |
| D6 | Reorganize documentation | **Deferred** - Low priority; current structure is functional |
| D7 | Docstrings on ConfusableInfo | **Complete** - All fields have comment-based docstrings |
| D8 | `normalize()` vs `normalize_expression()` | **Complete** - Already documented in architecture/normalize.md |
| D9 | Input size limits for validate functions | **Fixed** - Added MAX_INPUT_LENGTH = 100_000 to check_brackets() and validate_json() |
| D10 | CLI entry description | **Complete** - Current description is functional |
| D11 | normalize.py dependencies | **Complete** - Documented in architecture/normalize.md |
| D12 | `__all__` for diff.py | **Fixed** - Added __all__ list |

### Remaining Deferred Item

| Item | Description | Status |
|------|-------------|--------|
| D4 | Add `normalize_text` parameter to `inspect_text()` | **Deferred** - Overlaps with existing `normalize_unicode()` + `inspect_text()` workflow; design review needed |

---

## Verification

```bash
python3 -m pytest tests/
```

All 350 tests pass.
