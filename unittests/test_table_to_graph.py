from typing import List

import pytest  # type:ignore[import]
from networkx import DiGraph  # type:ignore[import]

from ebd_table_to_graph import EbdGraph, EbdGraphMetaData, convert_table_to_graph, get_all_nodes
from ebd_table_to_graph.models.ebd_graph import DecisionNode, EbdGraphNodes, OutcomeNode
from ebd_table_to_graph.models.ebd_table import EbdTable
from unittests.examples import table_e0003, table_e0015, table_e0025, table_e0401


class TestEbdTableModels:
    @pytest.mark.parametrize(
        "table,expected_result",
        [
            pytest.param(
                table_e0003,
                [
                    DecisionNode(step_number="1", question="Erfolgt der Eingang der Bestellung fristgerecht?"),
                    OutcomeNode(result_code="A01", note="Fristüberschreitung"),
                    DecisionNode(step_number="2", question="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?"),
                    OutcomeNode(result_code="A02", note="Gewählter Zeitpunkt nicht zulässig"),
                ],
            )
        ],
    )
    def test_get_all_nodes(self, table: EbdTable, expected_result: List[EbdGraphNodes]):
        actual = get_all_nodes(table)
        assert actual == expected_result

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
