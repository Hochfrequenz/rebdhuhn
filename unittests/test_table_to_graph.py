import pytest  # type:ignore[import]
from examples import table_e0003, table_e0015

from ebd_table_to_graph import EbdGraph, table_to_graph
from ebd_table_to_graph.models.ebd_table import EbdTable


class TestEbdTableModels:
    @pytest.mark.parametrize(
        "table,expected_result",
        [pytest.param(table_e0003, EbdGraph()), pytest.param(table_e0015, EbdGraph())],
    )
    def test_instantiation(self, table: EbdTable, expected_result: EbdGraph):
        pytest.skip("todo @leon")
        actual = table_to_graph(table)
        assert actual == expected_result
