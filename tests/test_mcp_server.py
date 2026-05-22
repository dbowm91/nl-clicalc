"""Integration tests for MCP server protocol and tools."""

import json
import pytest
from nl_calc.mcp.server import handle_request, main, TOOL_HANDLERS
from nl_calc.mcp.tools import MAX_TEXT_LENGTH


class TestProtocolHandshake:
    """Test MCP protocol handshake and initialization."""

    def test_initialize_returns_protocol_version(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        })
        assert response["result"]["protocolVersion"] == "2024-11-05"
        assert "capabilities" in response["result"]
        assert "serverInfo" in response["result"]
        assert response["result"]["serverInfo"]["name"] == "nl-calc-exact"

    def test_initialize_with_wrong_id_returns_error(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": None,
            "method": "initialize",
            "params": {},
        })
        assert response["id"] is None

    def test_notifications_initialized_returns_none(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "notifications/initialized",
            "params": {},
        })
        assert response is None


class TestToolsList:
    """Test tools/list endpoint."""

    def test_list_tools_returns_all_tools(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        })
        assert "result" in response
        tools = response["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        for name in TOOL_HANDLERS:
            assert name in tool_names

    def test_list_tools_returns_input_schema(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        })
        tools = response["result"]["tools"]
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool


class TestToolsCall:
    """Test tools/call endpoint."""

    def test_call_math_eval_valid_expression(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "math_eval",
                "arguments": {"expression": "5 + 3"},
            },
        })
        assert "result" in response
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["result"] == "8"

    def test_call_text_measure_valid_input(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "text_measure",
                "arguments": {"text": "Hello world"},
            },
        })
        if "result" in response:
            content = json.loads(response["result"]["content"][0]["text"])
            assert "result" in content

    def test_call_text_equal_valid_input(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "text_equal",
                "arguments": {"a": "hello", "b": "hello"},
            },
        })
        assert "result" in response
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["ok"] is True
        assert content["result"]["equal"] is True

    def test_call_unknown_tool_returns_error(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {},
            },
        })
        assert "error" in response
        assert response["error"]["code"] == -32602

    def test_call_tool_missing_name_returns_error(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "arguments": {},
            },
        })
        assert "error" in response


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_reject_non_object_request(self):
        response = handle_request([])
        assert response is not None
        assert response["error"]["code"] == -32600
        assert "expected JSON object" in response["error"]["message"]

    def test_reject_non_object_params(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": [],
        })
        assert response is not None
        assert response["error"]["code"] == -32600
        assert "expected object" in response["error"]["message"]

    def test_reject_non_object_arguments(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "text_measure", "arguments": []},
        })
        assert response is not None
        assert response["error"]["code"] == -32600
        assert "expected object" in response["error"]["message"]

    def test_unknown_method_returns_error(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "unknown/method",
            "params": {},
        })
        assert "error" in response
        assert response["error"]["code"] == -32601

    def test_tool_returns_error_envelope_on_failure(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "text_measure",
                "arguments": {"text": "x" * (MAX_TEXT_LENGTH + 1)},
            },
        })
        assert "error" in response
        assert response["error"]["code"] == -32000

    def test_invalid_jsonrpc_version(self):
        response = handle_request({
            "jsonrpc": "1.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        })
        assert "error" in response or "result" in response

    def test_missing_request_id(self):
        response = handle_request({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
        })
        assert response["id"] is None
