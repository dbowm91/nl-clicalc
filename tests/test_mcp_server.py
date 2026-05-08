"""Regression tests for MCP server request hardening."""

from nl_calc.mcp.server import handle_request


def test_handle_request_rejects_non_object_jsonrpc_request():
    response = handle_request([])
    assert response is not None
    assert response["error"]["code"] == -32600
    assert "expected JSON object" in response["error"]["message"]


def test_handle_request_rejects_non_object_params():
    response = handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": [],
        }
    )
    assert response is not None
    assert response["error"]["code"] == -32600
    assert "expected object" in response["error"]["message"]


def test_handle_request_rejects_non_object_arguments():
    response = handle_request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "text_measure", "arguments": []},
        }
    )
    assert response is not None
    assert response["error"]["code"] == -32600
    assert "expected object" in response["error"]["message"]
