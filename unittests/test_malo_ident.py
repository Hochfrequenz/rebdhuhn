"""
a test file just for the famous most requests E_0594 (the MaLo Ident EBD)
"""

import json
import os
from pathlib import Path

import pytest
from syrupy.assertion import SnapshotAssertion

from rebdhuhn import convert_graph_to_dot, convert_table_to_graph
from rebdhuhn.kroki import Kroki
from rebdhuhn.models import EbdTable

path_to_raw_table_json = Path(__file__).parent / "test_files" / "fv2504_ebd40b_e0594.json"
assert path_to_raw_table_json.exists()


@pytest.mark.snapshot
def test_e0594_svg_creation(kroki_client: Kroki, snapshot: SnapshotAssertion) -> None:
    with open(path_to_raw_table_json, "r", encoding="utf-8") as f:
        table_json = json.load(f)
    e_0594_table = EbdTable.model_validate(table_json)
    assert e_0594_table.metadata.ebd_code == "E_0594"
    graph = convert_table_to_graph(e_0594_table)
    dot_code = convert_graph_to_dot(graph)
    svg_code = kroki_client.convert_dot_to_svg(dot_code)
    target_dir = Path(__file__).parent / "output"
    os.makedirs(target_dir, exist_ok=True)
    with open(
        target_dir / f"table_dot_svg_malo_ident_{graph.metadata.ebd_code}.svg", "w+", encoding="utf-8"
    ) as svg_file:
        svg_file.write(svg_code)
    assert dot_code == snapshot(name=f"table_dot_svg_malo_ident_{graph.metadata.ebd_code}")
