"""Integration tests for text_replace_check, line_range_extract, line_range_compare MCP tools."""

import json

from egg_calc.mcp.server import TOOL_HANDLERS, handle_request


class TestTextReplaceCheckMCP:
    """Test text_replace_check via MCP protocol."""

    def test_basic_replace_check(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "text_replace_check",
                "arguments": {"text": "hello world", "old": "world", "new": "earth"},
            },
        })
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["ok"] is True
        assert content["result"]["match_count"] == 1
        assert content["result"]["would_change"] is True

    def test_no_match(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "text_replace_check",
                "arguments": {"text": "hello", "old": "xyz", "new": "abc"},
            },
        })
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["ok"] is True
        assert content["result"]["match_count"] == 0
        assert content["result"]["would_change"] is False

    def test_casefold_mode(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "text_replace_check",
                "arguments": {"text": "Hello World", "old": "world", "new": "earth", "mode": "casefold"},
            },
        })
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["ok"] is True
        assert content["result"]["match_count"] == 1

    def test_ambiguous_replacement(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "text_replace_check",
                "arguments": {"text": "aaa bbb aaa", "old": "aaa", "new": "xxx", "allow_multiple": False},
            },
        })
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["ok"] is True
        assert content["result"]["match_count"] == 2
        assert any(f["kind"] == "ambiguous_replacement" for f in content["result"]["findings"])

    def test_preview(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "text_replace_check",
                "arguments": {"text": "hello world", "old": "world", "new": "earth", "return_preview": True},
            },
        })
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["ok"] is True
        assert content["result"]["preview_before"] == "hello world"
        assert content["result"]["preview_after"] == "hello earth"

    def test_invalid_mode(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "text_replace_check",
                "arguments": {"text": "hello", "old": "lo", "new": "x", "mode": "invalid"},
            },
        })
        assert "error" in response

    def test_input_too_large(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "text_replace_check",
                "arguments": {"text": "a" * 100001, "old": "a", "new": "b"},
            },
        })
        assert "error" in response


class TestLineRangeExtractMCP:
    """Test line_range_extract via MCP protocol."""

    def test_basic_extract(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "line_range_extract",
                "arguments": {"text": "line1\nline2\nline3", "start_line": 1, "end_line": 2},
            },
        })
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["ok"] is True
        assert content["result"]["text"] == "line1\nline2"
        assert content["result"]["line_count_total"] == 3
        assert content["result"]["valid_range"] is True

    def test_out_of_range(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "line_range_extract",
                "arguments": {"text": "line1\nline2", "start_line": 5, "end_line": 5},
            },
        })
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["ok"] is True
        assert content["result"]["valid_range"] is False

    def test_include_line_numbers(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "line_range_extract",
                "arguments": {"text": "aaa\nbbb\nccc", "start_line": 1, "end_line": 3, "include_line_numbers": True},
            },
        })
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["ok"] is True
        assert content["result"]["lines"][0]["line"] == 1
        assert content["result"]["lines"][2]["line"] == 3

    def test_invalid_range(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "line_range_extract",
                "arguments": {"text": "hello", "start_line": 3, "end_line": 1},
            },
        })
        assert "error" in response

    def test_input_too_large(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "line_range_extract",
                "arguments": {"text": "a" * 100001, "start_line": 1, "end_line": 1},
            },
        })
        assert "error" in response


class TestLineRangeCompareMCP:
    """Test line_range_compare via MCP protocol."""

    def test_equal_compare(self):
        text = "aaa\nbbb\nccc"
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "line_range_compare",
                "arguments": {"left_text": text, "right_text": text, "start_line": 1, "end_line": 2},
            },
        })
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["ok"] is True
        assert content["result"]["equal"] is True

    def test_different_compare(self):
        left = "aaa\nbbb\nccc"
        right = "aaa\nBBB\nccc"
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "line_range_compare",
                "arguments": {"left_text": left, "right_text": right, "start_line": 2, "end_line": 2},
            },
        })
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["ok"] is True
        assert content["result"]["equal"] is False
        assert content["result"]["first_difference"] is not None

    def test_trailing_whitespace_mode(self):
        left = "hello  \nworld"
        right = "hello\nworld"
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "line_range_compare",
                "arguments": {
                    "left_text": left,
                    "right_text": right,
                    "start_line": 1,
                    "end_line": 1,
                    "comparison_mode": "ignore_trailing_whitespace",
                },
            },
        })
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["ok"] is True
        assert content["result"]["equal"] is True

    def test_invalid_mode(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "line_range_compare",
                "arguments": {
                    "left_text": "a",
                    "right_text": "a",
                    "start_line": 1,
                    "end_line": 1,
                    "comparison_mode": "invalid",
                },
            },
        })
        assert "error" in response

    def test_input_too_large(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "line_range_compare",
                "arguments": {
                    "left_text": "a" * 100001,
                    "right_text": "a" * 100001,
                    "start_line": 1,
                    "end_line": 1,
                },
            },
        })
        assert "error" in response


class TestToolRegistry:
    """Verify new tools are in the registry."""

    def test_text_replace_check_in_handlers(self):
        assert "text_replace_check" in TOOL_HANDLERS

    def test_line_range_extract_in_handlers(self):
        assert "line_range_extract" in TOOL_HANDLERS

    def test_line_range_compare_in_handlers(self):
        assert "line_range_compare" in TOOL_HANDLERS

    def test_all_handlers_callable(self):
        for name in ["text_replace_check", "line_range_extract", "line_range_compare"]:
            assert callable(TOOL_HANDLERS[name])
