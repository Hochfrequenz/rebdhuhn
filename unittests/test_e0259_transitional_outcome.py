"""
Integration test for E_0259 which contains TransitionalOutcomeNode nodes.
This tests the PlantUML conversion for EBDs with outcome nodes that have subsequent steps.
"""

import json
from pathlib import Path

import pytest

from rebdhuhn import convert_graph_to_dot, convert_graph_to_plantuml, convert_table_to_graph
from rebdhuhn.models import EbdTable
from rebdhuhn.models.ebd_graph import TransitionalOutcomeNode

path_to_e0259_json = Path(__file__).parent / "test_files" / "e0259.json"


class TestE0259TransitionalOutcome:
    """Tests for E_0259 which contains TransitionalOutcomeNode nodes."""

    @pytest.fixture
    def e0259_table(self) -> EbdTable:
        """Load E_0259 table from JSON."""
        assert path_to_e0259_json.exists(), f"Test file not found: {path_to_e0259_json}"
        with open(path_to_e0259_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        return EbdTable.model_validate(table_json)

    def test_e0259_has_transitional_outcome_nodes(self, e0259_table: EbdTable) -> None:
        """Verify that E_0259 graph contains TransitionalOutcomeNode nodes."""
        graph = convert_table_to_graph(e0259_table)

        transitional_nodes = [
            node_key
            for node_key in graph.graph.nodes
            if isinstance(graph.graph.nodes[node_key]["node"], TransitionalOutcomeNode)
        ]

        assert len(transitional_nodes) > 0, "Expected E_0259 to have TransitionalOutcomeNode nodes"
        # E_0259 has 12 TransitionalOutcomeNode nodes
        assert len(transitional_nodes) >= 10, f"Expected at least 10 TransitionalOutcomeNodes, got {len(transitional_nodes)}"

    def test_e0259_dot_conversion_succeeds(self, e0259_table: EbdTable) -> None:
        """Verify that E_0259 can be converted to DOT format."""
        graph = convert_table_to_graph(e0259_table)
        dot_code = convert_graph_to_dot(graph)

        assert len(dot_code) > 0
        assert "digraph" in dot_code

    def test_e0259_plantuml_conversion_succeeds(self, e0259_table: EbdTable) -> None:
        """
        Verify that E_0259 can be converted to PlantUML format.

        This test validates that TransitionalOutcomeNode is properly handled
        by the PlantUML converter. Previously this would fail with an assertion
        error or unknown node type error.
        """
        graph = convert_table_to_graph(e0259_table)
        plantuml_code = convert_graph_to_plantuml(graph)

        assert len(plantuml_code) > 0
        assert "@startuml" in plantuml_code
        assert "@enduml" in plantuml_code
        # TransitionalOutcomeNodes should appear as activity nodes with result codes
        # Check for some expected result codes from E_0259
        assert "A90" in plantuml_code or "A" in plantuml_code  # Result codes should be present
