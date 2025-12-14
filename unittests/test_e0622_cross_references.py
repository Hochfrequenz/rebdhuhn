"""
Integration test for E_0622 which contains multiple EBD E_0621 cross-references.
This tests the full pipeline from JSON -> EbdTable -> EbdGraph -> DOT -> SVG.
"""

import json
import os
from pathlib import Path

import pytest
from syrupy.assertion import SnapshotAssertion

from rebdhuhn import EbdTable, Kroki, OutcomeNode, convert_graph_to_dot, convert_table_to_graph

path_to_e0622_json = Path(__file__).parent / "test_files" / "e0622.json"
assert path_to_e0622_json.exists()


class TestE0622CrossReferences:
    """Tests for E_0622 which contains multiple EBD E_0621 cross-references."""

    def test_e0622_ebd_references_extracted(self) -> None:
        """Verify that EBD E_0621 references are extracted from E_0622 table."""
        with open(path_to_e0622_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        e_0622_table = EbdTable.model_validate(table_json)
        assert e_0622_table.metadata.ebd_code == "E_0622"

        # Count sub_rows with E_0621 references
        sub_rows_with_refs = [sr for row in e_0622_table.rows for sr in row.sub_rows if any(sr.ebd_references)]
        # E_0622 has multiple references to E_0621 (steps 70, 406, 430, 440, 610, 630, 806, 830)
        assert len(sub_rows_with_refs) >= 8, f"Expected at least 8 sub_rows with refs, got {len(sub_rows_with_refs)}"
        assert all("E_0621" in sr.ebd_references for sr in sub_rows_with_refs)

    def test_e0622_graph_has_outcome_nodes_with_references(self) -> None:
        """Verify that graph conversion preserves ebd_references on OutcomeNodes."""
        with open(path_to_e0622_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        e_0622_table = EbdTable.model_validate(table_json)
        graph = convert_table_to_graph(e_0622_table)

        # Find all OutcomeNodes with ebd_references
        outcome_nodes_with_refs: list[OutcomeNode] = []
        for node_key in graph.graph.nodes:
            node = graph.graph.nodes[node_key]["node"]
            if isinstance(node, OutcomeNode) and any(node.ebd_references):
                outcome_nodes_with_refs.append(node)

        assert len(outcome_nodes_with_refs) >= 1, "Expected at least one OutcomeNode with ebd_references"
        assert all("E_0621" in node.ebd_references for node in outcome_nodes_with_refs)

    def test_e0622_dot_output_has_styled_links(self) -> None:
        """Verify that DOT output with ebd_link_template styles EBD references as links."""
        with open(path_to_e0622_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        e_0622_table = EbdTable.model_validate(table_json)
        graph = convert_table_to_graph(e_0622_table)

        # Without template - plain text
        dot_without_links = convert_graph_to_dot(graph)
        assert "EBD E_0621" in dot_without_links
        assert 'href="?ebd=' not in dot_without_links
        assert "<U>EBD E_0621</U>" not in dot_without_links

        # With template - has styled links and href attributes
        dot_with_links = convert_graph_to_dot(graph, ebd_link_template="?ebd={ebd_code}")
        # Check for styled EBD reference text (underlined, blue)
        assert '<FONT COLOR="#0066cc"><U>EBD E_0621</U></FONT>' in dot_with_links
        # Check for href attribute on nodes with single EBD reference
        assert 'href="?ebd=E_0621"' in dot_with_links

    @pytest.mark.snapshot
    def test_e0622_full_svg_pipeline(self, kroki_client: Kroki, snapshot: SnapshotAssertion) -> None:
        """
        Full integration test: JSON -> Table -> Graph -> DOT -> SVG.
        This test creates the SVG and compares DOT output against snapshot.
        """
        with open(path_to_e0622_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        e_0622_table = EbdTable.model_validate(table_json)
        assert e_0622_table.metadata.ebd_code == "E_0622"

        graph = convert_table_to_graph(e_0622_table)
        dot_code = convert_graph_to_dot(graph, ebd_link_template="?ebd={ebd_code}")

        # Convert to SVG to verify the DOT code is valid
        svg_code = kroki_client.convert_dot_to_svg(dot_code)

        # Save output for manual inspection
        target_dir = Path(__file__).parent / "output"
        os.makedirs(target_dir, exist_ok=True)
        with open(target_dir / "e0622_with_links.dot.svg", "w+", encoding="utf-8") as svg_file:
            svg_file.write(svg_code)

        # Verify SVG contains the clickable link (href attribute becomes xlink:href in SVG)
        assert "?ebd=E_0621" in svg_code

        # Snapshot the DOT code
        assert dot_code == snapshot(name="e0622_with_ebd_links")
