"""Tests for path_scope_check tool."""

from __future__ import annotations

from egg_calc.exact.path_tools import path_scope_check


class TestPathScopeCheckBasic:
    def test_inside_root(self):
        result = path_scope_check("/home/user", "/home/user/docs/file.txt")
        assert result["inside_root"] is True
        assert result["relative_path"] == "docs/file.txt"

    def test_outside_root(self):
        result = path_scope_check("/home/user", "/etc/passwd")
        assert result["inside_root"] is False

    def test_same_path(self):
        result = path_scope_check("/home/user", "/home/user")
        assert result["inside_root"] is True
        assert result["relative_path"] == "."

    def test_relative_target_inside_relative_root(self):
        result = path_scope_check("src", "src/main.rs")
        assert result["inside_root"] is True

    def test_relative_target_outside_relative_root(self):
        result = path_scope_check("src", "../lib/main.rs")
        assert result["inside_root"] is False


class TestPathScopeCheckTraversal:
    def test_dotdot_traversal(self):
        result = path_scope_check("/home/user", "/home/user/../etc/passwd")
        assert result["inside_root"] is False
        assert result["escapes_via_dotdot"] is True

    def test_dotdot_stays_inside(self):
        result = path_scope_check("/home/user/projects", "/home/user/projects/foo/../bar")
        assert result["inside_root"] is True
        assert result["escapes_via_dotdot"] is True

    def test_no_dotdot(self):
        result = path_scope_check("/home/user", "/home/user/docs")
        assert result["escapes_via_dotdot"] is False


class TestPathScopeCheckAbsoluteTarget:
    def test_absolute_target_resolved(self):
        result = path_scope_check("/home/user", "docs/file.txt")
        assert result["inside_root"] is True
        assert result["absolute_target"] == "/home/user/docs/file.txt"

    def test_absolute_target_relative_root(self):
        result = path_scope_check("base", "sub/file.txt")
        assert result["inside_root"] is True


class TestPathScopeCheckCaseInsensitive:
    def test_case_sensitive_default(self):
        result = path_scope_check("/Home/User", "/home/user/docs")
        assert result["inside_root"] is False

    def test_case_insensitive(self):
        result = path_scope_check("/Home/User", "/home/user/docs", case_sensitive=False)
        assert result["inside_root"] is True


class TestPathScopeCheckWindows:
    def test_windows_platform(self):
        result = path_scope_check("C:\\Users\\test", "C:\\Users\\test\\docs", platform="windows")
        assert result["inside_root"] is True

    def test_windows_backslash_normalization(self):
        result = path_scope_check("C:/Users/test", "C:\\Users\\test\\docs", platform="windows")
        assert result["inside_root"] is True

    def test_windows_outside_root(self):
        result = path_scope_check("C:\\Users\\test", "D:\\Other\\file.txt", platform="windows")
        assert result["inside_root"] is False


class TestPathScopeCheckFindings:
    def test_absolute_target_relative_root_finding(self):
        result = path_scope_check("base", "sub/file.txt")
        assert any("relative" in f.lower() for f in result["findings"])

    def test_dotdot_finding(self):
        result = path_scope_check("/a/b", "/a/b/../c")
        assert any("traversal" in f.lower() for f in result["findings"])

    def test_case_insensitive_finding(self):
        result = path_scope_check("/a/b", "/A/B", case_sensitive=False)
        assert any("case" in f.lower() for f in result["findings"])


class TestPathScopeCheckNormalizedPaths:
    def test_root_normalized(self):
        result = path_scope_check("/home/user/", "/home/user/file.txt")
        assert result["root_normalized"] == "/home/user"

    def test_target_normalized(self):
        result = path_scope_check("/home/user", "/home/user/./file.txt")
        assert result["target_normalized"] == "/home/user/file.txt"
