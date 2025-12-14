"""
a test file just for the famous most requests E_0594 (the MaLo Ident EBD)
"""

import json
import os
from pathlib import Path

import pytest
from syrupy.assertion import SnapshotAssertion

from rebdhuhn import EbdTable, Kroki, convert_graph_to_dot, convert_table_to_graph

path_to_raw_table_json = Path(__file__).parent / "test_files" / "fv2504_ebd40b_e0610.json"
assert path_to_raw_table_json.exists()


@pytest.mark.snapshot
def test_e0610_svg_creation(kroki_client: Kroki, snapshot: SnapshotAssertion) -> None:
    with open(path_to_raw_table_json, "r", encoding="utf-8") as f:
        table_json = json.load(f)
    e_0610_table = EbdTable.model_validate(table_json)
    assert e_0610_table.metadata.ebd_code == "E_0610"
    graph = convert_table_to_graph(e_0610_table)
    dot_code = convert_graph_to_dot(graph)
    svg_code = kroki_client.convert_dot_to_svg(dot_code)
    target_dir = Path(__file__).parent / "output"
    os.makedirs(target_dir, exist_ok=True)
    with open(
        target_dir / f"table_dot_svg_malo_ident_{graph.metadata.ebd_code}.svg", "w+", encoding="utf-8"
    ) as svg_file:
        svg_file.write(svg_code)
    assert dot_code == snapshot(name=f"table_dot_svg_transitional_outcome_{graph.metadata.ebd_code}")


def test_e0610_dot_with_ebd_link_template() -> None:
    """
    Regression test: Verify that ebd_link_template works with TransitionalOutcomeNode.

    Previously, using ebd_link_template with EBDs containing TransitionalOutcomeNode
    caused AttributeError because TransitionalOutcomeNode doesn't have ebd_references.
    """
    with open(path_to_raw_table_json, "r", encoding="utf-8") as f:
        table_json = json.load(f)
    e_0610_table = EbdTable.model_validate(table_json)
    graph = convert_table_to_graph(e_0610_table)

    # This should not raise AttributeError
    dot_code = convert_graph_to_dot(graph, ebd_link_template="?ebd={ebd_code}")

    assert len(dot_code) > 0
    assert "digraph" in dot_code
