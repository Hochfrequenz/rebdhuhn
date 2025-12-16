"""
Test for E_0055 EBD table to graph conversion.

This EBD has a special case: result_code "A**" appears twice (in steps 1 and 2)
with different notes. This tests that multiple A** nodes with different notes
are correctly handled as separate nodes in the graph.
"""

import json
import os
from pathlib import Path

import pytest
from syrupy.assertion import SnapshotAssertion

from rebdhuhn import DecisionNode, EbdTable, Kroki, OutcomeNode, convert_graph_to_dot, convert_table_to_graph
from rebdhuhn.graphviz import convert_dot_to_svg_kroki

path_to_raw_table_json = Path(__file__).parent / "test_files" / "e0055.json"


class TestE0055:
    def test_e0055_table_loads_from_json(self) -> None:
        """Test that the JSON can be loaded and structured into an EbdTable."""
        with open(path_to_raw_table_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        e_0055_table = EbdTable.model_validate(table_json)

        assert e_0055_table.metadata.ebd_code == "E_0055"
        assert e_0055_table.metadata.chapter == "MaBiS"
        assert e_0055_table.metadata.role == "BIKO"
        assert len(e_0055_table.rows) == 3

    def test_e0055_converts_to_graph_with_multiple_a_star_star_nodes(self) -> None:
        """
        Test that E_0055 can be converted to a graph.

        E_0055 has result_code "A**" in both step 1 and step 2, but with different notes.
        These should be handled as separate outcome nodes in the graph.
        """
        with open(path_to_raw_table_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        e_0055_table = EbdTable.model_validate(table_json)

        graph = convert_table_to_graph(e_0055_table)

        # Verify the graph was created successfully
        assert graph is not None
        assert graph.metadata.ebd_code == "E_0055"

        # The graph should have:
        # - 1 Start node
        # - 3 Decision nodes (steps 1, 2, 3)
        # - 2 A** outcome nodes (from steps 1 and 2, with different notes)
        # - 2 outcome nodes (A01 and A04 from step 3)
        # Total: 8 nodes
        assert graph.graph.number_of_nodes() == 8

        # Verify the graph has the correct number of edges:
        # - Start -> 1
        # - 1 -> A** (nein), 1 -> 2 (ja)
        # - 2 -> A** (nein), 2 -> 3 (ja)
        # - 3 -> A01 (ja), 3 -> A04 (nein)
        # Total: 7 edges
        assert graph.graph.number_of_edges() == 7

        # Verify we have the expected decision nodes
        decision_nodes = [
            data["node"] for _, data in graph.graph.nodes(data=True) if isinstance(data["node"], DecisionNode)
        ]
        assert len(decision_nodes) == 3

        # Verify we have the A** outcome nodes (should be 2 distinct nodes)
        a_star_star_nodes = [
            data["node"]
            for _, data in graph.graph.nodes(data=True)
            if isinstance(data["node"], OutcomeNode) and data["node"].result_code == "A**"
        ]
        assert len(a_star_star_nodes) == 2

        # Verify the two A** nodes have different notes
        notes = {node.note for node in a_star_star_nodes}
        assert len(notes) == 2  # Two different notes

    @pytest.mark.snapshot
    def test_e0055_svg_creation(self, kroki_client: Kroki, snapshot: SnapshotAssertion) -> None:
        """
        Test that E_0055 can be converted to SVG via Kroki.
        The DOT code is snapshot-tested to ensure stable output.
        """
        with open(path_to_raw_table_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        e_0055_table = EbdTable.model_validate(table_json)

        graph = convert_table_to_graph(e_0055_table)
        dot_code = convert_graph_to_dot(graph)
        svg_code = convert_dot_to_svg_kroki(
            dot_code,
            kroki_client,
            add_watermark=False,
            add_background=False,
            release_info=graph.metadata.release_information,
        )

        # Save SVG to output folder for manual inspection
        target_dir = Path(__file__).parent / "output"
        os.makedirs(target_dir, exist_ok=True)
        with open(target_dir / f"{graph.metadata.ebd_code}.dot.svg", "w+", encoding="utf-8") as svg_file:
            svg_file.write(svg_code)

        assert dot_code == snapshot(name="e0055_dot_code")
