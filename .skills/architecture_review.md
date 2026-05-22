# Architecture Review Skill

## Purpose
Guide agents through systematic architecture document review against implementation code.

## When to Use
- Reviewing architecture documents (`.md` files in `architecture/`)
- Verifying implementation matches documentation
- Identifying bugs, inconsistencies, or missing features
- Writing improvement plans

## Review Process

### 1. Gather Information
```bash
# Read architecture document
cat architecture/<module>.md

# Read corresponding implementation
cat nl_calc/<module>.py  # or appropriate path

# List all architecture docs
ls architecture/
```

### 2. Create Review File
Write findings to `plans/<module>_review.md` following this structure:

```markdown
# <Module> Module Review

## Summary
Brief description of what the module does.

## Verified Claims
Table of claims from doc vs implementation status.

## Issues Found
### Issue N: [Title]
**Location:** file:line
**Problem:** Description
**Impact:** What breaks or is misleading

## Improvement Recommendations
### Priority: Description
**File:** path
**Fix:** Specific change needed
```

### 3. Focus Areas Checklist
For each module, examine:
1. **Completeness** - All documented features implemented?
2. **Correctness** - Implementation matches behavior?
3. **Consistency** - Doc and code contradict?
4. **Edge Cases** - Unhandled cases?
5. **Performance** - Efficiency concerns?
6. **Security** - Potential issues?
7. **Maintainability** - Code quality?
8. **Test Coverage** - Adequate tests?

### 4. Verification Steps
- Use `grep` to find specific function definitions
- Use `python -c "from module import function"` to verify exports
- Check `__all__` lists for public API consistency
- Run tests to verify functionality

### 5. Important Notes
- **Do NOT modify codebase** - only write reviews
- Use specific `file:line` references
- Distinguish between bugs (code wrong) vs doc issues (doc wrong)
- For bugs, verify the issue actually causes failure before documenting

## Output Location
All reviews go into `plans/<module>_review.md`

## Common Issues Found
- Functions in `__all__` but not exported
- Functions exported but not in `__all__`
- Documentation claims features not in code
- Code has features not documented
- Alias mappings that break functionality (e.g., prefixed units aliased to base)
- Precision errors in constants
- Missing CLI flags between built vs source versions