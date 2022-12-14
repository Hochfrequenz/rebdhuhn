from typing import List

import pytest  # type:ignore[import]
from networkx import DiGraph  # type:ignore[import]

from ebdtable2graph import (
    EbdGraph,
    EbdGraphMetaData,
    convert_graph_to_plantuml,
    convert_table_to_digraph,
    convert_table_to_graph,
    get_all_edges,
    get_all_nodes,
)
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
                    ),
                    ToNoEdge(
                        source=DecisionNode(
                            step_number="1", question="Erfolgt der Eingang der Bestellung fristgerecht?"
                        ),
                        target=OutcomeNode(result_code="A01", note="Fristüberschreitung"),
                    ),
                    ToYesEdge(
                        source=DecisionNode(
                            step_number="1", question="Erfolgt der Eingang der Bestellung fristgerecht?"
                        ),
                        target=DecisionNode(
                            step_number="2", question="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?"
                        ),
                    ),
                    ToNoEdge(
                        source=DecisionNode(
                            step_number="2", question="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?"
                        ),
                        target=OutcomeNode(result_code="A02", note="Gewählter Zeitpunkt nicht zulässig"),
                    ),
                    ToYesEdge(
                        source=DecisionNode(
                            step_number="2", question="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?"
                        ),
                        target=EndNode(),
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
                # 5 nodes = 2 decision nodes + ["A01", "A02", EndNode]
                # 4 edges = 2*Ja +2*Nein
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
        actual = convert_table_to_digraph(table)
        assert str(actual) == expected_description
        # return
        import matplotlib.pyplot as plt  # type:ignore[import]
        from networkx import draw_networkx  # type:ignore[import]
        from networkx import all_simple_paths

        ebd_graph = convert_table_to_graph(table)
        plantuml_code = convert_graph_to_plantuml(ebd_graph)
        draw_networkx(actual)
        # plt.show()

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
        try:
            actual = convert_table_to_graph(table)
        except NotImplementedError:
            pytest.skip("todo @leon")
        assert actual == expected_result
