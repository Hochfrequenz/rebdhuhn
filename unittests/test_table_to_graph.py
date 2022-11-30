import pytest  # type:ignore[import]
from networkx import DiGraph

from ebd_table_to_graph import EbdGraph, table_to_graph
from ebd_table_to_graph.models.ebd_table import EbdTable
from unittests.examples import table_e0003, table_e0015, table_e0025, table_e0401


class TestEbdTableModels:
    @pytest.mark.parametrize(
        "table,expected_result",
        [
            pytest.param(table_e0003, EbdGraph(metadata=table_e0003.metadata, graph=DiGraph())),  # easy
            pytest.param(table_e0025, EbdGraph(metadata=table_e0025.metadata, graph=DiGraph())),  # easy-medium
            pytest.param(table_e0015, EbdGraph(metadata=table_e0015.metadata, graph=DiGraph())),  # medium
            pytest.param(
                table_e0401, EbdGraph(metadata=table_e0401.metadata, graph=DiGraph())
            ),  # hard (because it's not a tree but only a directed graph)
            # todo: add E_0462
        ],
    )
    def test_instantiation(self, table: EbdTable, expected_result: EbdGraph):
        try:
            actual = table_to_graph(table)
        except NotImplementedError:
            pytest.skip("todo @leon")
        assert actual == expected_result
