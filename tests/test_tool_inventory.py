"""Tests for MCP tool registry consistency.

Ensures that the canonical tool list, runtime handlers, and schemas
stay in sync. Fails fast if documented tool names diverge from the
actual registry.
"""

import json
import pathlib

from nl_calc.mcp.schemas import TOOL_SCHEMAS
from nl_calc.mcp.server import TOOL_HANDLERS

FIXTURES = pathlib.Path(__file__).parent / "fixtures"
EXPECTED_REGISTRY = json.loads((FIXTURES / "mcp_tool_registry_expected.json").read_text())
EXPECTED_TOOLS = sorted(EXPECTED_REGISTRY["tools"])


class TestToolRegistryFixture:
    """Verify the fixture itself is well-formed."""

    def test_fixture_has_tools_key(self):
        assert "tools" in EXPECTED_REGISTRY

    def test_fixture_has_at_least_one_tool(self):
        assert len(EXPECTED_TOOLS) > 0

    def test_fixture_tool_names_are_strings(self):
        for name in EXPECTED_TOOLS:
            assert isinstance(name, str)
            assert name  # non-empty


class TestRuntimeRegistry:
    """Ensure the runtime TOOL_HANDLERS matches the canonical list."""

    def test_handlers_match_expected_names(self):
        actual = sorted(TOOL_HANDLERS.keys())
        assert actual == EXPECTED_TOOLS, (
            f"TOOL_HANDLERS keys differ from fixture.\n"
            f"  Missing from handlers: {set(EXPECTED_TOOLS) - set(actual)}\n"
            f"  Extra in handlers:     {set(actual) - set(EXPECTED_TOOLS)}"
        )

    def test_every_expected_handler_is_callable(self):
        for name in EXPECTED_TOOLS:
            handler = TOOL_HANDLERS[name]
            assert callable(handler), f"Handler for '{name}' is not callable"


class TestSchemaConsistency:
    """Ensure every registered tool has a schema entry."""

    def test_every_handler_has_schema(self):
        schema_keys = set(TOOL_SCHEMAS.keys())
        missing = set(TOOL_HANDLERS.keys()) - schema_keys
        assert not missing, f"Handlers without schemas: {sorted(missing)}"

    def test_every_expected_tool_has_schema(self):
        schema_keys = set(TOOL_SCHEMAS.keys())
        missing = set(EXPECTED_TOOLS) - schema_keys
        assert not missing, f"Expected tools without schemas: {sorted(missing)}"

    def test_schemas_have_description(self):
        for name, schema in TOOL_SCHEMAS.items():
            assert "description" in schema, f"Schema for '{name}' missing 'description'"

    def test_schemas_have_input_schema(self):
        for name, schema in TOOL_SCHEMAS.items():
            assert "inputSchema" in schema, f"Schema for '{name}' missing 'inputSchema'"


class TestTierConsistency:
    """Verify tier values are valid integers."""

    def test_all_tiers_are_valid(self):
        for name, schema in TOOL_SCHEMAS.items():
            tier = schema.get("tier", 3)
            assert isinstance(tier, int), f"Tier for '{name}' is not int: {tier}"
            assert 0 <= tier <= 3, f"Tier for '{name}' out of range: {tier}"
