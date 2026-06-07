"""Tests for MCP tool registry consistency.

Ensures that the canonical tool list, runtime handlers, and schemas
stay in sync. Fails fast if documented tool names diverge from the
actual registry.
"""

import json
import pathlib
import re

from eggcalc.mcp.schemas import TOOL_SCHEMAS, TOOL_METADATA
from eggcalc.mcp.server import TOOL_HANDLERS

FIXTURES = pathlib.Path(__file__).parent / "fixtures"
EXPECTED_REGISTRY = json.loads((FIXTURES / "mcp_tool_registry_expected.json").read_text())
EXPECTED_TOOLS = sorted(EXPECTED_REGISTRY["tools"])

# Paths to all relevant registries
_INVENTORY_DOC = FIXTURES.parent.parent / "docs" / "tool_inventory.md"
_MCP_DOC = FIXTURES.parent.parent / "docs" / "mcp.md"


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


class TestSourceOfTruthConsistency:
    """Verify that TOOL_HANDLERS, TOOL_SCHEMAS, and fixture agree on tool names."""

    def test_handlers_and_schemas_match(self):
        handler_keys = set(TOOL_HANDLERS.keys())
        schema_keys = set(TOOL_SCHEMAS.keys())
        assert handler_keys == schema_keys, (
            f"TOOL_HANDLERS and TOOL_SCHEMAS disagree.\n"
            f"  In handlers only: {sorted(handler_keys - schema_keys)}\n"
            f"  In schemas only:  {sorted(schema_keys - handler_keys)}"
        )

    def test_fixture_matches_handlers(self):
        fixture_set = set(EXPECTED_TOOLS)
        handler_set = set(TOOL_HANDLERS.keys())
        assert fixture_set == handler_set, (
            f"Fixture and TOOL_HANDLERS disagree.\n"
            f"  In fixture only:  {sorted(fixture_set - handler_set)}\n"
            f"  In handlers only: {sorted(handler_set - fixture_set)}"
        )

    def test_fixture_matches_schemas(self):
        fixture_set = set(EXPECTED_TOOLS)
        schema_set = set(TOOL_SCHEMAS.keys())
        assert fixture_set == schema_set, (
            f"Fixture and TOOL_SCHEMAS disagree.\n"
            f"  In fixture only: {sorted(fixture_set - schema_set)}\n"
            f"  In schemas only: {sorted(schema_set - fixture_set)}"
        )

    def test_fixture_is_alphabetically_sorted(self):
        assert EXPECTED_TOOLS == sorted(EXPECTED_TOOLS), (
            "Fixture tools list is not alphabetically sorted"
        )

    def test_fixture_count_matches_handlers(self):
        assert len(EXPECTED_TOOLS) == len(TOOL_HANDLERS), (
            f"Fixture has {len(EXPECTED_TOOLS)} tools, handlers has {len(TOOL_HANDLERS)}"
        )

    def test_fixture_count_matches_schemas(self):
        assert len(EXPECTED_TOOLS) == len(TOOL_SCHEMAS), (
            f"Fixture has {len(EXPECTED_TOOLS)} tools, schemas has {len(TOOL_SCHEMAS)}"
        )

    def test_inventory_doc_tool_count_matches(self):
        """Verify the inventory doc's total count matches the actual count."""
        if not _INVENTORY_DOC.exists():
            return
        content = _INVENTORY_DOC.read_text()
        match = re.search(r"\*\*Total:\s*(\d+)\s*tools\*\*", content)
        assert match, "Could not find total tool count in inventory doc"
        doc_count = int(match.group(1))
        assert doc_count == len(TOOL_HANDLERS), (
            f"Inventory doc says {doc_count} tools, but TOOL_HANDLERS has {len(TOOL_HANDLERS)}"
        )

    def test_inventory_doc_table_row_count_matches(self):
        """Verify the number of rows in the inventory table matches the tool count."""
        if not _INVENTORY_DOC.exists():
            return
        content = _INVENTORY_DOC.read_text()
        # Count rows that start with | and have a tool name
        rows = re.findall(r"^\|\s*\d+\s*\|", content, re.MULTILINE)
        assert len(rows) == len(TOOL_HANDLERS), (
            f"Inventory table has {len(rows)} rows, but TOOL_HANDLERS has {len(TOOL_HANDLERS)}"
        )


class TestToolMetadata:
    """Verify TOOL_METADATA is complete and consistent."""

    VALID_CATEGORIES = {
        "math", "text", "json", "toml", "config", "regex", "path", "shell",
        "patch", "identifier", "markdown", "version", "cargo", "list", "validation", "unicode",
    }
    VALID_TIERS = {0, 1, 2, 3}
    VALID_LLM_EXPOSURE = {"default", "contextual", "expert_only", "harness_only", "hidden"}
    VALID_COST = {"cheap", "moderate", "heavy"}
    VALID_STABILITY = {"stable", "experimental", "deprecated"}

    def test_metadata_covers_all_handlers(self):
        handler_keys = set(TOOL_HANDLERS.keys())
        metadata_keys = set(TOOL_METADATA.keys())
        missing = handler_keys - metadata_keys
        assert not missing, f"Handlers without metadata: {sorted(missing)}"

    def test_metadata_covers_all_schemas(self):
        schema_keys = set(TOOL_SCHEMAS.keys())
        metadata_keys = set(TOOL_METADATA.keys())
        missing = schema_keys - metadata_keys
        assert not missing, f"Schemas without metadata: {sorted(missing)}"

    def test_metadata_no_extra_keys(self):
        metadata_keys = set(TOOL_METADATA.keys())
        handler_keys = set(TOOL_HANDLERS.keys())
        extra = metadata_keys - handler_keys
        assert not extra, f"Metadata for non-existent tools: {sorted(extra)}"

    def test_metadata_tiers_match_schemas(self):
        for name, meta in TOOL_METADATA.items():
            schema_tier = TOOL_SCHEMAS.get(name, {}).get("tier")
            if schema_tier is not None:
                assert meta["tier"] == schema_tier, (
                    f"Tier mismatch for '{name}': metadata={meta['tier']}, schema={schema_tier}"
                )

    def test_metadata_categories_are_valid(self):
        for name, meta in TOOL_METADATA.items():
            assert meta["category"] in self.VALID_CATEGORIES, (
                f"Invalid category '{meta['category']}' for tool '{name}'"
            )

    def test_metadata_tiers_are_valid(self):
        for name, meta in TOOL_METADATA.items():
            assert meta["tier"] in self.VALID_TIERS, (
                f"Invalid tier {meta['tier']} for tool '{name}'"
            )

    def test_metadata_llm_exposure_is_valid(self):
        for name, meta in TOOL_METADATA.items():
            assert meta["llm_exposure"] in self.VALID_LLM_EXPOSURE, (
                f"Invalid llm_exposure '{meta['llm_exposure']}' for tool '{name}'"
            )

    def test_metadata_cost_is_valid(self):
        for name, meta in TOOL_METADATA.items():
            assert meta["cost"] in self.VALID_COST, (
                f"Invalid cost '{meta['cost']}' for tool '{name}'"
            )

    def test_metadata_stability_is_valid(self):
        for name, meta in TOOL_METADATA.items():
            assert meta["stability"] in self.VALID_STABILITY, (
                f"Invalid stability '{meta['stability']}' for tool '{name}'"
            )

    def test_metadata_profiles_are_lists(self):
        for name, meta in TOOL_METADATA.items():
            assert isinstance(meta["profiles"], list), (
                f"Profiles for '{name}' must be a list"
            )

    def test_metadata_aliases_are_lists(self):
        for name, meta in TOOL_METADATA.items():
            assert isinstance(meta["aliases"], list), (
                f"Aliases for '{name}' must be a list"
            )

    def test_metadata_harness_use_are_lists(self):
        for name, meta in TOOL_METADATA.items():
            assert isinstance(meta["harness_use"], list), (
                f"harness_use for '{name}' must be a list"
            )

    def test_metadata_composite_is_bool(self):
        for name, meta in TOOL_METADATA.items():
            assert isinstance(meta["composite"], bool), (
                f"composite for '{name}' must be bool"
            )


class TestToolProfiles:
    """Verify TOOL_PROFILES is complete and consistent."""

    def test_profiles_dict_exists(self):
        from eggcalc.mcp.schemas import TOOL_PROFILES
        assert isinstance(TOOL_PROFILES, dict)
        assert len(TOOL_PROFILES) > 0

    def test_all_metadata_profile_names_exist_in_profiles_dict(self):
        from eggcalc.mcp.schemas import TOOL_PROFILES
        all_profile_names = set()
        for meta in TOOL_METADATA.values():
            all_profile_names.update(meta.get("profiles", []))
        for name in all_profile_names:
            assert name in TOOL_PROFILES, f"Profile '{name}' referenced in metadata but not in TOOL_PROFILES"

    def test_profile_tool_lists_are_sorted(self):
        from eggcalc.mcp.schemas import TOOL_PROFILES
        for profile_name, tool_list in TOOL_PROFILES.items():
            assert tool_list == sorted(tool_list), (
                f"Profile '{profile_name}' tool list is not sorted"
            )

    def test_profile_tool_lists_only_contain_known_tools(self):
        from eggcalc.mcp.schemas import TOOL_PROFILES
        known_tools = set(TOOL_HANDLERS.keys())
        for profile_name, tool_list in TOOL_PROFILES.items():
            unknown = set(tool_list) - known_tools
            assert not unknown, (
                f"Profile '{profile_name}' contains unknown tools: {sorted(unknown)}"
            )

    def test_full_profile_contains_all_non_hidden_tools(self):
        from eggcalc.mcp.schemas import TOOL_PROFILES
        full_tools = set(TOOL_PROFILES.get("full", []))
        expected = {
            name for name, meta in TOOL_METADATA.items()
            if meta.get("llm_exposure") != "hidden"
        }
        assert full_tools == expected, (
            f"Full profile mismatch.\n"
            f"  Missing: {sorted(expected - full_tools)}\n"
            f"  Extra:   {sorted(full_tools - expected)}"
        )

    def test_codegg_core_min_is_subset_of_codegg_core(self):
        from eggcalc.mcp.schemas import TOOL_PROFILES
        core_min = set(TOOL_PROFILES.get("codegg_core_min", []))
        core = set(TOOL_PROFILES.get("codegg_core", []))
        assert core_min.issubset(core), (
            f"codegg_core_min is not a subset of codegg_core.\n"
            f"  In core_min but not core: {sorted(core_min - core)}"
        )

    def test_profile_names_constant(self):
        from eggcalc.mcp.schemas import PROFILE_NAMES
        assert isinstance(PROFILE_NAMES, list)
        assert len(PROFILE_NAMES) > 0
        # All names should be in TOOL_PROFILES
        from eggcalc.mcp.schemas import TOOL_PROFILES
        for name in PROFILE_NAMES:
            assert name in TOOL_PROFILES, f"PROFILE_NAMES contains '{name}' not in TOOL_PROFILES"
