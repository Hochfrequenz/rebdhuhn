import pytest  # type:ignore[import]

from ebd_table_to_graph import EbdGraph, table_to_graph
from ebd_table_to_graph.models.ebd_table import EbdTable
from unittests.examples import table_e0003, table_e0015, table_e0025, table_e0401


class TestEbdTableModels:
    @pytest.mark.parametrize(
        "table,expected_result",
        [
            pytest.param(table_e0003, EbdGraph()),  # easy
            pytest.param(table_e0025, EbdGraph()),  # easy-medium
            pytest.param(table_e0015, EbdGraph()),  # medium
            pytest.param(table_e0401, EbdGraph()),  # hard
        ],
    )
    def test_instantiation(self, table: EbdTable, expected_result: EbdGraph):
        pytest.skip("todo @leon")
        actual = table_to_graph(table)
        assert actual == expected_result
