"""
Test for E_0256 EBD table which has outcome nodes with notes differing only by trailing punctuation.

E_0256 has result code A11 appearing twice with nearly identical notes
(differing only by a trailing period). The graph conversion should handle this
by normalizing notes before comparison.
"""

import json
from pathlib import Path

from rebdhuhn import convert_table_to_graph
from rebdhuhn.models import EbdTable

path_to_json = Path(__file__).parent / "test_files" / "e0256_ambiguous_outcome.json"


class TestE0256AmbiguousOutcome:
    def test_e0256_loads_from_json(self) -> None:
        """Test that the JSON can be loaded and structured into an EbdTable."""
        with open(path_to_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        table = EbdTable.model_validate(table_json)

        assert table.metadata.ebd_code == "E_0256"
        assert table.metadata.chapter == "WiM Strom"
        assert table.metadata.role == "MSB"
        assert len(table.rows) == 11

    def test_e0256_handles_trailing_punctuation_difference(self) -> None:
        """
        Test that E_0256 converts successfully despite A11 appearing twice with different punctuation.

        E_0256 has A11 appearing in both:
        - Step 10: "Cluster: Zustimmung\\nBestellung ist angenommen" (no period)
        - Step 11: "Cluster: Zustimmung\\nBestellung ist angenommen." (with period)

        These differ only by a trailing period but should be treated as the same outcome node.
        The BDEW apparently couldn't be bothered to use consistent punctuation in their
        official regulatory documents.
        """
        with open(path_to_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        table = EbdTable.model_validate(table_json)

        # Should not raise OutcomeCodeAmbiguousError anymore
        graph = convert_table_to_graph(table)

        # Verify the graph was created successfully
        assert graph.metadata.ebd_code == "E_0256"
        # Verify A11 outcome node exists (check the underlying networkx graph)
        a11_nodes = [
            data["node"]
            for _, data in graph.graph.nodes(data=True)
            if hasattr(data.get("node"), "result_code") and data["node"].result_code == "A11"
        ]
        assert len(a11_nodes) == 1  # Should be exactly one A11 node, not two
