"""Tests for shell and argv tools."""

from __future__ import annotations

from eggcalc.exact.shell import (
    argv_compare,
    shell_quote_join,
    shell_split,
)


class TestShellSplit:
    """Tests for shell_split."""

    def test_simple_command(self):
        result = shell_split("ls -la")
        assert result["parse_ok"] is True
        assert result["argv"] == ["ls", "-la"]
        assert result["argc"] == 2
        assert result["findings"] == []

    def test_quoted_spaces(self):
        result = shell_split('echo "hello world"')
        assert result["parse_ok"] is True
        assert result["argv"] == ["echo", "hello world"]
        assert result["argc"] == 2

    def test_single_quotes(self):
        result = shell_split("echo 'hello world'")
        assert result["parse_ok"] is True
        assert result["argv"] == ["echo", "hello world"]

    def test_unbalanced_quotes(self):
        result = shell_split('echo "hello world')
        assert result["parse_ok"] is False
        assert result["features"]["has_unbalanced_quotes"] is True

    def test_empty_command(self):
        result = shell_split("")
        assert result["parse_ok"] is True
        assert result["argv"] == []
        assert result["argc"] == 0
        assert "Empty command" in result["findings"]

    def test_whitespace_only(self):
        result = shell_split("   ")
        assert result["parse_ok"] is True
        assert result["argv"] == []

    def test_pipe_detection(self):
        result = shell_split("ls | grep foo")
        assert result["parse_ok"] is True
        assert result["argv"] == ["ls", "|", "grep", "foo"]
        assert result["features"]["has_pipe"] is True
        assert any("pipe" in f.lower() for f in result["findings"])

    def test_redirection_detection(self):
        result = shell_split("echo hello > out.txt")
        assert result["parse_ok"] is True
        assert result["features"]["has_redirection"] is True

    def test_input_redirection(self):
        result = shell_split("cat < input.txt")
        assert result["parse_ok"] is True
        assert result["features"]["has_redirection"] is True

    def test_command_substitution_dollar_paren(self):
        result = shell_split("echo $(whoami)")
        assert result["parse_ok"] is True
        assert result["features"]["has_command_substitution"] is True
        assert any("command substitution" in f.lower() for f in result["findings"])

    def test_command_substitution_backtick(self):
        result = shell_split("echo `whoami`")
        assert result["parse_ok"] is True
        assert result["features"]["has_command_substitution"] is True

    def test_variable_expansion_simple(self):
        result = shell_split("echo $HOME")
        assert result["parse_ok"] is True
        assert result["features"]["has_variable_expansion"] is True
        assert any("variable expansion" in f.lower() for f in result["findings"])

    def test_variable_expansion_braces(self):
        result = shell_split("echo ${USER}")
        assert result["parse_ok"] is True
        assert result["features"]["has_variable_expansion"] is True

    def test_glob_pattern_star(self):
        result = shell_split("ls *.py")
        assert result["parse_ok"] is True
        assert result["features"]["has_glob_pattern"] is True
        assert any("glob" in f.lower() for f in result["findings"])

    def test_glob_pattern_question(self):
        result = shell_split("ls file?.txt")
        assert result["parse_ok"] is True
        assert result["features"]["has_glob_pattern"] is True

    def test_glob_pattern_bracket(self):
        result = shell_split("ls file[12].txt")
        assert result["parse_ok"] is True
        assert result["features"]["has_glob_pattern"] is True

    def test_control_operator_semicolon(self):
        result = shell_split("echo a; echo b")
        assert result["parse_ok"] is True
        assert result["features"]["has_control_operator"] is True
        assert any("control operator" in f.lower() for f in result["findings"])

    def test_control_operator_ampersand(self):
        result = shell_split("echo a &")
        assert result["parse_ok"] is True
        assert result["features"]["has_control_operator"] is True

    def test_no_risky_features(self):
        result = shell_split("cargo test -- --nocapture", detect_risky_features=True)
        assert result["parse_ok"] is True
        assert result["argv"] == ["cargo", "test", "--", "--nocapture"]
        assert result["argc"] == 4
        assert result["features"]["has_pipe"] is False
        assert result["features"]["has_redirection"] is False
        assert result["features"]["has_command_substitution"] is False
        assert result["features"]["has_variable_expansion"] is False
        assert result["features"]["has_glob_pattern"] is False
        assert result["features"]["has_control_operator"] is False
        assert result["features"]["has_unbalanced_quotes"] is False

    def test_detect_risky_features_disabled(self):
        result = shell_split("ls | grep foo", detect_risky_features=False)
        assert result["parse_ok"] is True
        assert result["argv"] == ["ls", "|", "grep", "foo"]
        # Features should be empty when detection is disabled
        assert not result["features"]

    def test_unsupported_shell(self):
        result = shell_split("ls", shell="bash")
        assert result["parse_ok"] is False
        assert any("unsupported" in f.lower() for f in result["findings"])

    def test_complex_quoting(self):
        result = shell_split('cmd "arg with spaces" \'arg with more spaces\' plain')
        assert result["parse_ok"] is True
        assert result["argv"] == ["cmd", "arg with spaces", "arg with more spaces", "plain"]
        assert result["argc"] == 4

    def test_escape_in_quotes(self):
        result = shell_split('echo "hello \\"world\\""')
        assert result["parse_ok"] is True
        assert result["argv"] == ["echo", 'hello "world"']

    def test_dollar_not_variable_expansion(self):
        # A literal dollar sign in quotes is not variable expansion
        result = shell_split('echo "$5.00"')
        assert result["parse_ok"] is True
        # $5 is not a valid variable name (starts with digit)
        # shlex may or may not keep the $ - the key point is it doesn't fail
        assert "echo" in result["argv"]


class TestShellQuoteJoin:
    """Tests for shell_quote_join."""

    def test_simple_args(self):
        result = shell_quote_join(["echo", "hello"])
        assert result["roundtrip_ok"] is True
        assert result["findings"] == []
        # Verify the command can be split back
        assert "echo" in result["command"]
        assert "hello" in result["command"]

    def test_args_with_spaces(self):
        result = shell_quote_join(["echo", "hello world"])
        assert result["roundtrip_ok"] is True
        split = shell_split(result["command"], detect_risky_features=False)
        assert split["argv"] == ["echo", "hello world"]

    def test_args_with_quotes(self):
        result = shell_quote_join(["echo", "it's a test"])
        assert result["roundtrip_ok"] is True
        split = shell_split(result["command"], detect_risky_features=False)
        assert split["argv"] == ["echo", "it's a test"]

    def test_empty_argv(self):
        result = shell_quote_join([])
        assert result["roundtrip_ok"] is True
        assert result["command"] == ""

    def test_single_arg(self):
        result = shell_quote_join(["ls"])
        assert result["roundtrip_ok"] is True
        split = shell_split(result["command"], detect_risky_features=False)
        assert split["argv"] == ["ls"]

    def test_special_chars(self):
        result = shell_quote_join(["echo", "hello|world; rm -rf /"])
        assert result["roundtrip_ok"] is True
        split = shell_split(result["command"], detect_risky_features=False)
        assert split["argv"] == ["echo", "hello|world; rm -rf /"]

    def test_unsupported_shell(self):
        result = shell_quote_join(["echo"], shell="bash")
        assert result["roundtrip_ok"] is False
        assert any("unsupported" in f.lower() for f in result["findings"])

    def test_glob_chars_preserved(self):
        result = shell_quote_join(["ls", "*.py", "file[12].txt"])
        assert result["roundtrip_ok"] is True
        split = shell_split(result["command"], detect_risky_features=False)
        assert split["argv"] == ["ls", "*.py", "file[12].txt"]

    def test_empty_string_arg(self):
        result = shell_quote_join(["echo", ""])
        assert result["roundtrip_ok"] is True
        split = shell_split(result["command"], detect_risky_features=False)
        assert split["argv"] == ["echo", ""]

    def test_backslash_in_arg(self):
        result = shell_quote_join(["echo", "path\\to\\file"])
        assert result["roundtrip_ok"] is True
        split = shell_split(result["command"], detect_risky_features=False)
        assert split["argv"] == ["echo", "path\\to\\file"]


class TestArgvCompare:
    """Tests for argv_compare."""

    def test_identical_commands(self):
        result = argv_compare(
            left_command="ls -la",
            right_command="ls -la",
        )
        assert result["argv_equal"] is True
        assert result["first_difference"] is None
        assert result["findings"] == []

    def test_different_commands(self):
        result = argv_compare(
            left_command="ls -la",
            right_command="ls -l",
        )
        assert result["argv_equal"] is False
        assert result["first_difference"] == 1
        assert len(result["findings"]) > 0

    def test_same_args_different_order(self):
        result = argv_compare(
            left_command="echo hello world",
            right_command="echo world hello",
        )
        assert result["argv_equal"] is False
        assert result["first_difference"] == 1

    def test_raw_vs_preparsed_argv(self):
        result = argv_compare(
            left_command="cargo test -- --nocapture",
            right_argv=["cargo", "test", "--", "--nocapture"],
        )
        assert result["argv_equal"] is True
        assert result["left_argv"] == ["cargo", "test", "--", "--nocapture"]
        assert result["right_argv"] == ["cargo", "test", "--", "--nocapture"]

    def test_both_argv_lists(self):
        result = argv_compare(
            left_argv=["cargo", "test"],
            right_argv=["cargo", "test"],
        )
        assert result["argv_equal"] is True

    def test_different_length_argv(self):
        result = argv_compare(
            left_argv=["cargo", "test", "--nocapture"],
            right_argv=["cargo", "test"],
        )
        assert result["argv_equal"] is False
        assert result["first_difference"] == 2

    def test_left_longer(self):
        result = argv_compare(
            left_argv=["cargo", "test", "--nocapture"],
            right_argv=["cargo", "test", "--nocapture", "extra"],
        )
        assert result["argv_equal"] is False
        assert result["first_difference"] == 3
        assert any("right has" in f.lower() or "extra" in f.lower() for f in result["findings"])

    def test_quoted_spaces_equal(self):
        result = argv_compare(
            left_command='echo "hello world"',
            right_command="echo 'hello world'",
        )
        assert result["argv_equal"] is True

    def test_empty_commands(self):
        result = argv_compare(
            left_command="",
            right_command="",
        )
        assert result["argv_equal"] is True
        assert result["left_argv"] == []
        assert result["right_argv"] == []

    def test_one_empty_one_not(self):
        result = argv_compare(
            left_command="echo hello",
            right_command="",
        )
        assert result["argv_equal"] is False

    def test_parse_failure_left(self):
        result = argv_compare(
            left_command='echo "unterminated',
            right_command="echo hello",
        )
        assert result["argv_equal"] is False
        assert any("parse" in f.lower() for f in result["findings"])

    def test_parse_failure_right(self):
        result = argv_compare(
            left_command="echo hello",
            right_command='echo "unterminated',
        )
        assert result["argv_equal"] is False
        assert any("parse" in f.lower() for f in result["findings"])

    def test_unsupported_shell(self):
        result = argv_compare(
            left_command="ls",
            right_command="ls",
            shell="bash",
        )
        assert result["argv_equal"] is False
        assert any("unsupported" in f.lower() for f in result["findings"])

    def test_command_vs_argv_mismatch(self):
        result = argv_compare(
            left_command="echo hello",
            left_argv=["echo", "world"],
            right_argv=["echo", "world"],
        )
        assert result["argv_equal"] is False
        assert any("differs from provided left_argv" in f for f in result["findings"])

    def test_complex_command_comparison(self):
        result = argv_compare(
            left_command="cargo test -- --nocapture 2>&1 | tee output.log",
            right_command="cargo test -- --nocapture 2>&1 | tee output.log",
        )
        assert result["argv_equal"] is True
