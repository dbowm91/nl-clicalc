"""Tests for Unicode policy checks and canonicalization profiles."""

from egg_calc.exact.unicode_policy import (
    _VALID_POLICIES,
    _VALID_PROFILES,
    canonicalize_text,
    unicode_policy_check,
)


class TestUnicodePolicyCheck:
    """Test unicode_policy_check function."""

    def test_identifier_strict_clean_ascii(self):
        result = unicode_policy_check("hello_world", "identifier_strict")
        assert result["pass_"] is True
        assert result["policy"] == "identifier_strict"
        assert result["normalized_form"] == "hello_world"
        assert result["findings"] == []

    def test_identifier_strict_mixed_scripts(self):
        result = unicode_policy_check("hello\u0410", "identifier_strict")
        assert result["pass_"] is False
        rules = [f["rule"] for f in result["findings"]]
        assert "mixed_scripts" in rules

    def test_identifier_strict_bidi_controls(self):
        result = unicode_policy_check("hello\u202e", "identifier_strict")
        assert result["pass_"] is False
        rules = [f["rule"] for f in result["findings"]]
        assert "bidi_controls" in rules

    def test_identifier_strict_zero_width(self):
        result = unicode_policy_check("hel\u200blo", "identifier_strict")
        assert result["pass_"] is False
        rules = [f["rule"] for f in result["findings"]]
        assert "zero_width_characters" in rules

    def test_identifier_strict_confusables(self):
        # Cyrillic 'a' (U+0430) is confusable with Latin 'a'
        result = unicode_policy_check("\u0430", "identifier_strict")
        assert result["pass_"] is False
        rules = [f["rule"] for f in result["findings"]]
        assert "confusables" in rules

    def test_identifier_strict_normalization_instability(self):
        # e + combining acute is NFC-stable but NFD-different
        result = unicode_policy_check("e\u0301", "identifier_strict")
        assert result["pass_"] is True  # No errors, just warnings
        warnings = [f for f in result["findings"] if f["severity"] == "warning"]
        assert len(warnings) >= 1

    def test_identifier_strict_invisible_chars(self):
        result = unicode_policy_check("hello\ufeff", "identifier_strict")
        assert result["pass_"] is False
        rules = [f["rule"] for f in result["findings"]]
        assert "invisible_characters" in rules

    def test_filename_safe_clean(self):
        result = unicode_policy_check("readme.txt", "filename_safe")
        assert result["pass_"] is True

    def test_filename_safe_control_chars(self):
        result = unicode_policy_check("file\x00name", "filename_safe")
        assert result["pass_"] is False
        rules = [f["rule"] for f in result["findings"]]
        assert "control_characters" in rules

    def test_filename_safe_forbidden_chars(self):
        result = unicode_policy_check("file:name", "filename_safe")
        assert result["pass_"] is False
        rules = [f["rule"] for f in result["findings"]]
        assert "path_separators" in rules

    def test_filename_safe_bidi_controls(self):
        result = unicode_policy_check("file\u202ename", "filename_safe")
        assert result["pass_"] is False
        rules = [f["rule"] for f in result["findings"]]
        assert "bidi_controls" in rules

    def test_filename_safe_reserved_windows_name(self):
        result = unicode_policy_check("CON.txt", "filename_safe")
        assert result["pass_"] is False
        rules = [f["rule"] for f in result["findings"]]
        assert "reserved_windows_name" in rules

    def test_filename_safe_zero_width(self):
        result = unicode_policy_check("file\u200b.txt", "filename_safe")
        assert result["pass_"] is False
        rules = [f["rule"] for f in result["findings"]]
        assert "zero_width_characters" in rules

    def test_source_code_clean(self):
        result = unicode_policy_check("def foo(): pass", "source_code")
        assert result["pass_"] is True

    def test_source_code_bidi_controls(self):
        result = unicode_policy_check("def\u202e foo()", "source_code")
        assert result["pass_"] is False
        rules = [f["rule"] for f in result["findings"]]
        assert "bidi_controls" in rules

    def test_source_code_confusables_warning(self):
        # Cyrillic 'a' is confusable - warning level for source code
        result = unicode_policy_check("\u0430", "source_code")
        assert result["pass_"] is True  # Warning only
        warnings = [f for f in result["findings"] if f["severity"] == "warning"]
        assert any(f["rule"] == "confusables" for f in warnings)

    def test_human_text_warn_only(self):
        # Mixed scripts should be warning only for human text
        result = unicode_policy_check("hello\u0410world", "human_text")
        assert result["pass_"] is True  # No errors
        warnings = [f for f in result["findings"] if f["severity"] == "warning"]
        assert any(f["rule"] == "mixed_scripts" for f in warnings)

    def test_human_text_bidi_warning(self):
        result = unicode_policy_check("hello\u202e", "human_text")
        assert result["pass_"] is True  # Warning only
        warnings = [f for f in result["findings"] if f["severity"] == "warning"]
        assert any(f["rule"] == "bidi_controls" for f in warnings)

    def test_json_key_bidi_error(self):
        result = unicode_policy_check("key\u202e", "json_key")
        assert result["pass_"] is False

    def test_json_key_confusables_warning(self):
        result = unicode_policy_check("\u0430", "json_key")
        assert result["pass_"] is True  # Warning only
        warnings = [f for f in result["findings"] if f["severity"] == "warning"]
        assert any(f["rule"] == "confusables" for f in warnings)

    def test_domain_like_mixed_scripts_error(self):
        result = unicode_policy_check("hello\u0410", "domain_like")
        assert result["pass_"] is False

    def test_domain_like_confusables_error(self):
        result = unicode_policy_check("\u0430", "domain_like")
        assert result["pass_"] is False

    def test_invalid_policy(self):
        result = unicode_policy_check("hello", "invalid_policy")
        assert result["pass_"] is False
        assert result["findings"][0]["rule"] == "invalid_policy"

    def test_normalization_nfc(self):
        # e + combining acute → NFC should normalize to precomposed e-acute
        result = unicode_policy_check("e\u0301", "identifier_strict", normalization="NFC")
        assert result["normalized_form"] == "\u00e9"  # é

    def test_normalization_raw(self):
        result = unicode_policy_check("hello", "identifier_strict", normalization="raw")
        assert result["normalized_form"] == "hello"

    def test_invalid_normalization(self):
        result = unicode_policy_check("hello", "identifier_strict", normalization="INVALID")
        assert result["pass_"] is False
        assert result["findings"][0]["rule"] == "invalid_normalization"

    def test_summary_format_pass(self):
        result = unicode_policy_check("hello", "identifier_strict")
        assert "PASS" in result["summary"]
        assert "identifier_strict" in result["summary"]

    def test_summary_format_fail(self):
        result = unicode_policy_check("\u202e", "identifier_strict")
        assert "FAIL" in result["summary"]


class TestCanonicalizeText:
    """Test canonicalize_text function."""

    def test_source_file_identity_no_change(self):
        result = canonicalize_text("hello\n", "source_file_identity")
        assert result["changed"] is False
        assert result["operations_applied"] == []

    def test_source_file_identity_nfc(self):
        # e + combining acute → NFC
        result = canonicalize_text("e\u0301", "source_file_identity")
        assert result["changed"] is True
        assert "NFC" in result["operations_applied"]
        # source_file_identity adds final newline
        assert result["text"] == "\u00e9\n"

    def test_source_file_identity_crlf_to_lf(self):
        result = canonicalize_text("hello\r\n", "source_file_identity")
        assert result["changed"] is True
        assert "LF_newlines" in result["operations_applied"]

    def test_source_file_identity_strip_trailing_whitespace(self):
        result = canonicalize_text("hello   \n", "source_file_identity")
        assert result["changed"] is True
        assert "strip_trailing_whitespace" in result["operations_applied"]

    def test_source_file_identity_ensure_final_newline(self):
        result = canonicalize_text("hello", "source_file_identity")
        assert result["changed"] is True
        assert "ensure_final_newline" in result["operations_applied"]
        assert result["text"].endswith("\n")

    def test_identifier_compare_no_change(self):
        result = canonicalize_text("hello", "identifier_compare")
        assert result["changed"] is False

    def test_identifier_compare_nfc_and_casefold(self):
        # Use ß (German sharp s) which casefolds to "ss" - actually changes
        # And uppercase É which casefolds to é
        result = canonicalize_text("É", "identifier_compare")
        assert result["changed"] is True
        assert "casefold" in result["operations_applied"]
        assert result["text"] == "é"

    def test_identifier_compare_nfc_normalization(self):
        # e + combining acute → NFC normalizes to precomposed é
        result = canonicalize_text("e\u0301", "identifier_compare")
        assert result["changed"] is True
        assert "NFC" in result["operations_applied"]
        assert result["text"] == "\u00e9"

    def test_identifier_compare_casefold_only(self):
        # HELLO is already NFC, so only casefold is applied
        result = canonicalize_text("HELLO", "identifier_compare")
        assert result["changed"] is True
        assert "casefold" in result["operations_applied"]
        assert result["text"] == "hello"

    def test_human_label_compare_whitespace_collapse(self):
        result = canonicalize_text("  hello   world  ", "human_label_compare")
        assert result["changed"] is True
        assert "collapse_whitespace" in result["operations_applied"]
        assert result["text"] == "hello world"
        assert len(result["findings"]) >= 1

    def test_json_key_compare(self):
        result = canonicalize_text("KEY", "json_key_compare")
        assert result["changed"] is True
        assert "casefold" in result["operations_applied"]
        assert result["text"] == "key"

    def test_path_segment_compare(self):
        result = canonicalize_text("PATH/Segment", "path_segment_compare")
        assert result["changed"] is True
        assert "lowercase" in result["operations_applied"]
        assert result["text"] == "path/segment"

    def test_invalid_profile(self):
        result = canonicalize_text("hello", "invalid_profile")
        assert result["changed"] is False
        assert len(result["findings"]) == 1
        assert "Invalid profile" in result["findings"][0]

    def test_fingerprints_differ_when_changed(self):
        result = canonicalize_text("HELLO", "identifier_compare")
        assert result["changed"] is True
        assert result["fingerprint_before"] != result["fingerprint_after"]

    def test_fingerprints_same_when_unchanged(self):
        result = canonicalize_text("hello", "identifier_compare")
        assert result["changed"] is False
        assert result["fingerprint_before"] == result["fingerprint_after"]

    def test_return_mapping_true(self):
        result = canonicalize_text("HELLO", "identifier_compare", return_mapping=True)
        assert result["mapping"] is not None
        assert len(result["mapping"]) > 0

    def test_return_mapping_false(self):
        result = canonicalize_text("HELLO", "identifier_compare", return_mapping=False)
        assert result["mapping"] is None

    def test_return_mapping_no_change(self):
        result = canonicalize_text("hello", "identifier_compare", return_mapping=True)
        assert result["changed"] is False
        # mapping may be None or empty when nothing changed
        assert result["mapping"] is None

    def test_operations_applied_list(self):
        result = canonicalize_text("e\u0301", "source_file_identity")
        assert isinstance(result["operations_applied"], list)


class TestPolicyAndProfileLists:
    """Test that all policies and profiles are valid."""

    def test_all_policies_are_valid(self):
        assert _VALID_POLICIES == {
            "identifier_strict",
            "filename_safe",
            "source_code",
            "human_text",
            "json_key",
            "domain_like",
        }

    def test_all_profiles_are_valid(self):
        assert _VALID_PROFILES == {
            "source_file_identity",
            "identifier_compare",
            "human_label_compare",
            "json_key_compare",
            "path_segment_compare",
        }
