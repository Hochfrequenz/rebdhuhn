"""
Test for E_0256 EBD table which has ambiguous outcome nodes.

E_0256 has result code A11 appearing twice with nearly identical notes
(differing only by a trailing period). This should be handled correctly.
"""

import json
from pathlib import Path

import cattrs
import pytest

from rebdhuhn import convert_table_to_graph
from rebdhuhn.models import EbdTable
from rebdhuhn.models.errors import OutcomeCodeAmbiguousError

path_to_json = Path(__file__).parent / "test_files" / "e0256_ambiguous_outcome.json"


class TestE0256AmbiguousOutcome:
    def test_e0256_loads_from_json(self) -> None:
        """Test that the JSON can be loaded and structured into an EbdTable."""
        with open(path_to_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        table = cattrs.structure(table_json, EbdTable)

        assert table.metadata.ebd_code == "E_0256"
        assert table.metadata.chapter == "WiM Strom"
        assert table.metadata.role == "MSB"
        assert len(table.rows) == 11

    def test_e0256_has_ambiguous_a11_outcome(self) -> None:
        """
        Test that E_0256 currently raises OutcomeCodeAmbiguousError.

        E_0256 has A11 appearing in both:
        - Step 10: "Cluster: Zustimmung\\nBestellung ist angenommen" (no period)
        - Step 11: "Cluster: Zustimmung\\nBestellung ist angenommen." (with period)

        These differ only by a trailing period but are treated as different nodes,
        leading to the ambiguity error.
        """
        with open(path_to_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        table = cattrs.structure(table_json, EbdTable)

        with pytest.raises(OutcomeCodeAmbiguousError) as exc_info:
            convert_table_to_graph(table)

        assert "A11" in str(exc_info.value)
        # The notes differ only by a trailing period
        assert "Bestellung ist angenommen" in str(exc_info.value)
