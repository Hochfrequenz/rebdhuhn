import pytest  # type:ignore[import]

from ebdtable2graph import convert_graph_to_plantuml, convert_table_to_graph
from ebdtable2graph.models import EbdTable
from ebdtable2graph.models.errors import (
    GraphTooComplexForPlantumlError,
    NotExactlyTwoOutgoingEdgesError,
    PathsNotGreaterThanOneError,
)

from .e0266 import table_e0266
from .e0454 import table_e0454
from .e0459 import table_e0459


class TestErrors:
    """
    Test cases for various exceptions being raised. This can be the basis for future fixes/workarounds
    """

    @pytest.mark.parametrize("table", [pytest.param(table_e0459)])
    def test_not_exactly_two_outgoing_edges_error(self, table: EbdTable):
        ebd_graph = convert_table_to_graph(table)
        with pytest.raises(NotExactlyTwoOutgoingEdgesError):
            _ = convert_graph_to_plantuml(ebd_graph)

    @pytest.mark.parametrize("table", [pytest.param(table_e0266)])
    def test_loops_in_the_tree_error(self, table: EbdTable):
        ebd_graph = convert_table_to_graph(table)
        with pytest.raises(PathsNotGreaterThanOneError):
            _ = convert_graph_to_plantuml(ebd_graph)

    @pytest.mark.parametrize("table", [pytest.param(table_e0454)])
    def test_too_complex_for_plantuml(self, table: EbdTable):
        ebd_graph = convert_table_to_graph(table)
        with pytest.raises(GraphTooComplexForPlantumlError):
            _ = convert_graph_to_plantuml(ebd_graph)
