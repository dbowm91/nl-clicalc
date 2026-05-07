"""Integration tests for CLI text commands (inspect, count, regex).

These tests exercise the CLI layer through subprocess to ensure
the commands work correctly from the command line.
"""

import subprocess
import sys


def run_calc(args: list[str]) -> tuple[int, str, str]:
    """Run calc command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "nl_calc.py"] + args,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


class TestCLIInspect:
    """Tests for calc inspect command."""

    def test_inspect_clean_text(self):
        """Clean text should show no hidden characters."""
        code, stdout, stderr = run_calc(["inspect", "hello"])
        assert code == 0
        assert "No hidden characters" in stdout
        assert "\u2713" in stdout  # checkmark

    def test_inspect_clean_text_unicode(self):
        """Clean Unicode text should pass inspection."""
        code, stdout, stderr = run_calc(["inspect", "héllo"])
        assert code == 0
        assert "No hidden characters" in stdout

    def test_inspect_confusable(self):
        """Confusable characters should be detected."""
        # Cyrillic 'а' (U+0430) looks like Latin 'a' (U+0061)
        code, stdout, stderr = run_calc(["inspect", "аbc"])
        assert code == 0
        assert "CONFUSABLE" in stdout

    def test_inspect_zero_width_space(self):
        """Zero-width space should be detected."""
        # Use actual zero-width space character
        code, stdout, stderr = run_calc(["inspect", "hello\u200bworld"])
        assert code == 0
        assert "INVISIBLE_CHARACTER" in stdout or "ZERO WIDTH" in stdout

    def test_inspect_missing_text(self):
        """Missing text argument should error."""
        code, stdout, stderr = run_calc(["inspect"])
        assert code == 1
        assert "Usage" in stderr


class TestCLICount:
    """Tests for calc count command."""

    def test_count_single_char(self):
        """Count single character."""
        code, stdout, stderr = run_calc(["count", "hello"])
        assert code == 0
        assert "5" in stdout

    def test_count_specific_char(self):
        """Count specific character occurrence."""
        code, stdout, stderr = run_calc(["count", "hello", "l"])
        assert code == 0
        assert "2" in stdout
        assert "'l'" in stdout

    def test_count_multiple_words(self):
        """Count with frequency table for multiple words."""
        code, stdout, stderr = run_calc(["count", "hello world"])
        assert code == 0
        assert "11" in stdout  # total characters

    def test_count_space_char(self):
        """Count space character."""
        code, stdout, stderr = run_calc(["count", "hello world", " "])
        assert code == 0
        assert "1" in stdout

    def test_count_missing_text(self):
        """Missing text argument should error."""
        code, stdout, stderr = run_calc(["count"])
        assert code == 1
        assert "Usage" in stderr


class TestCLIRegex:
    """Tests for calc regex command."""

    def test_regex_match(self):
        """Match should succeed."""
        code, stdout, stderr = run_calc(["regex", r"^\d+$", "12345"])
        assert code == 0
        assert "Match" in stdout
        assert "\u2713" in stdout

    def test_regex_no_match(self):
        """No match should be reported."""
        code, stdout, stderr = run_calc(["regex", r"^hello", "world"])
        assert code == 0
        assert "No match" in stdout
        assert "\u2717" in stdout

    def test_regex_with_groups(self):
        """Capture groups should be displayed."""
        code, stdout, stderr = run_calc(["regex", r"(\d+)-(\d+)", "555-1234"])
        assert code == 0
        assert "Match" in stdout
        assert "555" in stdout

    def test_regex_invalid_pattern(self):
        """Invalid pattern should error."""
        code, stdout, stderr = run_calc(["regex", r"[invalid", "test"])
        assert code == 1

    def test_regex_missing_args(self):
        """Missing arguments should error."""
        code, stdout, stderr = run_calc(["regex", "pattern"])
        assert code == 1
        assert "Usage" in stderr


class TestCLIMathStillWorks:
    """Ensure math expressions still work alongside text commands."""

    def test_basic_math(self):
        """Basic math should still work."""
        code, stdout, stderr = run_calc(["5", "+", "3"])
        assert code == 0
        assert "8" in stdout

    def test_natural_language_math(self):
        """Natural language math should work."""
        code, stdout, stderr = run_calc(["five", "plus", "three"])
        assert code == 0
        assert "8" in stdout

    def test_unit_conversion(self):
        """Unit conversions should work."""
        code, stdout, stderr = run_calc(["30m", "+", "100ft"])
        assert code == 0
        # Should have result with meters


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
