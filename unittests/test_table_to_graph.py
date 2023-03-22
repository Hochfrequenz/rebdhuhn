import os
from pathlib import Path
from typing import List

import pytest  # type:ignore[import]
from networkx import DiGraph  # type:ignore[import]

from ebdtable2graph import (
    convert_graph_to_plantuml,
    convert_plantuml_to_svg_kroki,
    convert_table_to_digraph,
    convert_table_to_graph,
)
from ebdtable2graph.add_watermark import add_watermark
from ebdtable2graph.graph_conversion import get_all_edges, get_all_nodes
from ebdtable2graph.graphviz import convert_dot_to_svg_kroki, convert_graph_to_dot
from ebdtable2graph.models import EbdGraph, EbdGraphMetaData
from ebdtable2graph.models.ebd_graph import (
    DecisionNode,
    EbdGraphEdge,
    EbdGraphNode,
    EndNode,
    OutcomeNode,
    StartNode,
    ToNoEdge,
    ToYesEdge,
)
from ebdtable2graph.models.ebd_table import EbdTable
from unittests.examples import table_e0003, table_e0015, table_e0025, table_e0401


class TestEbdTableModels:
    @pytest.mark.parametrize(
        "table,expected_result",
        [
            pytest.param(
                table_e0003,
                [
                    StartNode(),
                    DecisionNode(step_number="1", question="Erfolgt der Eingang der Bestellung fristgerecht?"),
                    OutcomeNode(result_code="A01", note="Fristüberschreitung"),
                    DecisionNode(step_number="2", question="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?"),
                    OutcomeNode(result_code="A02", note="Gewählter Zeitpunkt nicht zulässig"),
                    EndNode(),
                ],
            )
        ],
    )
    def test_get_all_nodes(self, table: EbdTable, expected_result: List[EbdGraphNode]):
        actual = get_all_nodes(table)
        assert actual == expected_result

    @pytest.mark.parametrize(
        "table,expected_result",
        [
            pytest.param(
                table_e0003,
                [
                    EbdGraphEdge(
                        source=StartNode(),
                        target=DecisionNode(
                            step_number="1", question="Erfolgt der Eingang der Bestellung fristgerecht?"
                        ),
                        note=None,
                    ),
                    ToNoEdge(
                        source=DecisionNode(
                            step_number="1", question="Erfolgt der Eingang der Bestellung fristgerecht?"
                        ),
                        target=OutcomeNode(result_code="A01", note="Fristüberschreitung"),
                        note=None,
                    ),
                    ToYesEdge(
                        source=DecisionNode(
                            step_number="1", question="Erfolgt der Eingang der Bestellung fristgerecht?"
                        ),
                        target=DecisionNode(
                            step_number="2", question="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?"
                        ),
                        note=None,
                    ),
                    ToNoEdge(
                        source=DecisionNode(
                            step_number="2", question="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?"
                        ),
                        target=OutcomeNode(result_code="A02", note="Gewählter Zeitpunkt nicht zulässig"),
                        note=None,
                    ),
                    ToYesEdge(
                        source=DecisionNode(
                            step_number="2", question="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?"
                        ),
                        target=EndNode(),
                        note=None,
                    ),
                ],
            )
        ],
    )
    def test_get_all_edges(self, table: EbdTable, expected_result: List[EbdGraphEdge]):
        actual = get_all_edges(table)
        assert actual == expected_result

    @pytest.mark.parametrize(
        "table,expected_description",
        [
            pytest.param(
                table_e0003,
                "DiGraph with 6 nodes and 5 edges",
            ),
            pytest.param(
                table_e0015,
                "DiGraph with 22 nodes and 21 edges",
                # todo: check if result is ok
            ),
            pytest.param(
                table_e0025,
                "DiGraph with 10 nodes and 11 edges",
                # todo: check if result is ok
            ),
        ],
    )
    def test_table_to_digraph(self, table: EbdTable, expected_description: str):
        """
        Test the conversion pipeline. The results are stored in `unittests/output` for you to inspect the result
        manually. The test only checks if the svg can be built.
        """
        ebd_graph = convert_table_to_graph(table)
        assert str(ebd_graph.graph) == expected_description

        plantuml_code = convert_graph_to_plantuml(ebd_graph)
        with open(
            Path(__file__).parent / "output" / f"{ebd_graph.metadata.ebd_code}.puml", "w+", encoding="utf-8"
        ) as uml_file:
            uml_file.write(plantuml_code)
        svg_code = convert_plantuml_to_svg_kroki(plantuml_code)  # Raises an error if conversion fails
        os.makedirs(Path(__file__).parent / "output", exist_ok=True)
        with open(
            Path(__file__).parent / "output" / f"{ebd_graph.metadata.ebd_code}.puml.svg", "w+", encoding="utf-8"
        ) as svg_file:
            svg_file.write(svg_code)

    @pytest.mark.parametrize(
        "table,expected_description",
        [
            pytest.param(
                table_e0003,
                "DiGraph with 6 nodes and 5 edges",
            ),
            pytest.param(
                table_e0015,
                "DiGraph with 22 nodes and 21 edges",
                # todo: check if result is ok
            ),
            pytest.param(
                table_e0025,
                "DiGraph with 10 nodes and 11 edges",
                # todo: check if result is ok
            ),
            pytest.param(
                table_e0401,
                "DiGraph with 23 nodes and 27 edges",
                # todo: check if result is ok
            ),
        ],
    )
    def test_table_to_digraph_dot(self, table: EbdTable, expected_description: str):
        """
        Test the conversion pipeline. The results are stored in `unittests/output` for you to inspect the result
        manually. The test only checks if the svg can be built.
        """
        ebd_graph = convert_table_to_graph(table)
        assert str(ebd_graph.graph) == expected_description

        dot_code = convert_graph_to_dot(ebd_graph)
        with open(
            Path(__file__).parent / "output" / f"{ebd_graph.metadata.ebd_code}.dot", "w+", encoding="utf-8"
        ) as uml_file:
            uml_file.write(dot_code)
        svg_code = convert_dot_to_svg_kroki(dot_code)  # Raises an error if conversion fails
        os.makedirs(Path(__file__).parent / "output", exist_ok=True)
        with open(
            Path(__file__).parent / "output" / f"{ebd_graph.metadata.ebd_code}.dot.svg", "w+", encoding="utf-8"
        ) as svg_file:
            svg_file.write(svg_code)

    def test_table_to_digraph_dot_with_watermark(self):
        ebd_graph = convert_table_to_graph(table_e0003)
        dot_code = convert_graph_to_dot(ebd_graph)
        svg_code = convert_dot_to_svg_kroki(dot_code, add_watermark=False)  # Raises an error if conversion fails
        os.makedirs(Path(__file__).parent / "output", exist_ok=True)

        with open(
            Path(__file__).parent / "output" / f"{ebd_graph.metadata.ebd_code}_without_watermark.dot.svg",
            "w+",
            encoding="utf-8",
        ) as svg_file:
            svg_file.write(svg_code)

        svg_without_watermark = svg_code.encode("utf-8")

        svg_with_watermark = add_watermark(svg_without_watermark)

        file_path2 = Path(__file__).parent / "output" / f"{ebd_graph.metadata.ebd_code}_with_watermark.dot.svg"
        with open(file_path2, "w", encoding="utf-8") as ebd_svg:
            ebd_svg.write(svg_with_watermark.decode())

    def test_table_e0401_too_complex_for_plantuml(self):
        """
        Test the conversion pipeline for E_0401. In this case the plantuml conversion should fail because the graph is
        too complex for this implementation.
        """
        with pytest.raises(AssertionError) as exc:
            _ = convert_graph_to_plantuml(convert_table_to_graph(table_e0401))

        assert "graph is too complex" in str(exc.value)

    @pytest.mark.parametrize(
        "table,expected_result",
        [
            pytest.param(
                table_e0003,
                EbdGraph(
                    metadata=EbdGraphMetaData(
                        ebd_code=table_e0003.metadata.ebd_code,
                        chapter=table_e0003.metadata.chapter,
                        sub_chapter=table_e0003.metadata.sub_chapter,
                        role=table_e0003.metadata.role,
                    ),
                    graph=DiGraph(),
                ),
                id="E0003 (easy)",
            ),
            pytest.param(
                table_e0025,
                EbdGraph(
                    metadata=EbdGraphMetaData(
                        ebd_code=table_e0025.metadata.ebd_code,
                        chapter=table_e0025.metadata.chapter,
                        sub_chapter=table_e0025.metadata.sub_chapter,
                        role=table_e0025.metadata.role,
                    ),
                    graph=DiGraph(),
                ),
                id="E0025 (easy-medium)",
            ),
            pytest.param(
                table_e0015,
                EbdGraph(
                    metadata=EbdGraphMetaData(
                        ebd_code=table_e0015.metadata.ebd_code,
                        chapter=table_e0015.metadata.chapter,
                        sub_chapter=table_e0015.metadata.sub_chapter,
                        role=table_e0015.metadata.role,
                    ),
                    graph=DiGraph(),
                ),
                id="E0015 (medium)",
            ),
            pytest.param(
                table_e0401,
                EbdGraph(
                    metadata=EbdGraphMetaData(
                        ebd_code=table_e0401.metadata.ebd_code,
                        chapter=table_e0401.metadata.chapter,
                        sub_chapter=table_e0401.metadata.sub_chapter,
                        role=table_e0401.metadata.role,
                    ),
                    graph=DiGraph(),
                ),
                id="E0401 (hard)",
            ),  # hard (because it's not a tree but only a directed graph)
            # todo: add E_0462
        ],
    )
    def test_table_to_graph(self, table: EbdTable, expected_result: EbdGraph):
        actual = convert_table_to_graph(table)
        pytest.skip("todo @leon - wird später in den examples.py ergänzt")
        assert actual == expected_result
