# confusables.py Architecture Review

## Verified Claims

1. **Purpose**: Contains confusables table from Unicode UTS #39 - MATCHES (lines 1-6)
2. **Data Structure**: `CONFUSABLES: dict[str, str]` with codepoint string keys and space-separated substitution values - MATCHES (lines 14+)
3. **Data Source**: Generated from official Unicode `confusables.txt` (line 4)
4. **Generating script**: `scripts/generate_confusables.py` exists at expected location
5. **How confusables work**: Maps confusable character to its equivalent(s) - MATCHES
6. **Security applications**: Homoglyph attacks, IDN homograph attacks, social engineering - MATCHES (lines 44-50)
7. **DO NOT EDIT notice**: Present in code (line 5) - MATCHES

## Discrepancies

1. **Documentation URL differs**: 
   - Architecture doc shows `https://www.unicode.org/Public/security/latest/confusables.txt`
   - This is acceptable as it points to the authoritative source

2. **Large file size not mentioned**: The file is ~6581 lines (180KB as mentioned in AGENTS.md). Documentation doesn't note this is auto-generated and large.

## Bugs Found

No bugs - this is a data file generated from authoritative source.

## Improvements

1. **Low Priority**: Update architecture doc to note file is auto-generated and large (~180KB)
2. **Low Priority**: Add comment noting this file should be regenerated when Unicode updates confusables.txt

## Priority

- **Low**: Documentation updates only
- **No code changes needed** - this is a data file