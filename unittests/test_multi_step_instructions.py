"""
Tests for multi_step_instructions handling in EBD graph conversion and rendering.

Multi-step instructions are contextual notes that apply to multiple steps in an EBD,
starting from a specified step number onwards.
"""

import json
from pathlib import Path

import pytest

from rebdhuhn import convert_graph_to_dot, convert_table_to_graph
from rebdhuhn.models import EbdTable

path_to_e0594_json = Path(__file__).parent / "test_files" / "fv2504_ebd40b_e0594.json"


class TestMultiStepInstructions:
    """Tests for multi_step_instructions handling."""

    def test_e0594_has_multi_step_instructions(self) -> None:
        """E_0594 should have 4 multi-step instructions."""
        with open(path_to_e0594_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        table = EbdTable.model_validate(table_json)

        assert table.multi_step_instructions is not None
        assert len(table.multi_step_instructions) == 4

        # Verify the step numbers
        step_numbers = [inst.first_step_number_affected for inst in table.multi_step_instructions]
        assert step_numbers == ["100", "205", "305", "400"]

    def test_multi_step_instructions_passed_to_graph(self) -> None:
        """Multi-step instructions should be passed through to the EbdGraph."""
        with open(path_to_e0594_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        table = EbdTable.model_validate(table_json)

        graph = convert_table_to_graph(table)

        assert graph.multi_step_instructions is not None
        assert len(graph.multi_step_instructions) == 4
        assert graph.multi_step_instructions == table.multi_step_instructions

    def test_graph_to_dot_with_multi_step_instructions(self) -> None:
        """Converting a graph with multi-step instructions to DOT should not fail."""
        with open(path_to_e0594_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        table = EbdTable.model_validate(table_json)

        graph = convert_table_to_graph(table)
        dot_code = convert_graph_to_dot(graph)

        assert dot_code is not None
        assert "digraph" in dot_code
        assert graph.metadata.ebd_code in dot_code

    def test_dot_output_contains_instruction_nodes(self) -> None:
        """DOT output should contain msi_* nodes for each multi-step instruction."""
        with open(path_to_e0594_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        table = EbdTable.model_validate(table_json)

        graph = convert_table_to_graph(table)
        dot_code = convert_graph_to_dot(graph)

        # Verify instruction nodes exist with correct node keys
        assert '"msi_100"' in dot_code
        assert '"msi_205"' in dot_code
        assert '"msi_305"' in dot_code
        assert '"msi_400"' in dot_code

    def test_dot_output_instruction_node_style(self) -> None:
        """DOT instruction nodes should have light blue fill and note shape."""
        with open(path_to_e0594_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        table = EbdTable.model_validate(table_json)

        graph = convert_table_to_graph(table)
        dot_code = convert_graph_to_dot(graph)

        # Verify styling: light blue background, note shape
        assert 'fillcolor="#e6f3ff"' in dot_code
        assert "shape=note" in dot_code

    def test_dot_output_contains_clusters(self) -> None:
        """DOT output should contain clusters grouping instruction nodes with affected steps."""
        with open(path_to_e0594_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        table = EbdTable.model_validate(table_json)

        graph = convert_table_to_graph(table)
        dot_code = convert_graph_to_dot(graph)

        # Verify clusters exist for each instruction
        assert 'subgraph "cluster_msi_100"' in dot_code
        assert 'subgraph "cluster_msi_205"' in dot_code
        assert 'subgraph "cluster_msi_305"' in dot_code
        assert 'subgraph "cluster_msi_400"' in dot_code

        # Verify cluster styling: dashed border, light blue background
        assert 'style="dashed,rounded"' in dot_code
        assert 'bgcolor="#f0f7ff"' in dot_code
        assert 'color="#888888"' in dot_code

    @pytest.mark.parametrize(
        "step_number,expected_instruction_start",
        [
            pytest.param(
                "100",
                "Die nachfolgenden Prüfungen erfolgen auf Basis der Identifikationskriterien aus der Anfrage und dem gesamten Datenbestand",
                id="step_100",
            ),
            pytest.param(
                "205",
                "Die nachfolgenden Prüfungen erfolgen auf Basis der Identifikationskriterien aus der Anfrage und der Trefferliste auf Basis eines Kriteriums",
                id="step_205",
            ),
            pytest.param(
                "305",
                "Die nachfolgenden Prüfungen erfolgen auf Basis der Identifikationskriterien aus der Anfrage und der Trefferliste auf Basis von zwei Kriterien",
                id="step_305",
            ),
            pytest.param(
                "400",
                "Die nachfolgenden Prüfungen erfolgen auf Basis der Identifikationskriterien aus der Anfrage und der Trefferliste auf Basis von drei Kriterien",
                id="step_400",
            ),
        ],
    )
    def test_multi_step_instruction_content(self, step_number: str, expected_instruction_start: str) -> None:
        """Verify the content of each multi-step instruction."""
        with open(path_to_e0594_json, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        table = EbdTable.model_validate(table_json)

        assert table.multi_step_instructions is not None
        instruction = next(
            inst for inst in table.multi_step_instructions if inst.first_step_number_affected == step_number
        )
        assert instruction.instruction_text.startswith(expected_instruction_start)
