import pytest

from ebdtable2graph import convert_graph_to_plantuml, convert_table_to_graph
from ebdtable2graph.models import EbdTable
from ebdtable2graph.models.errors import NotExactlyTwoOutgoingEdgesError

from .e0459 import table_e0459


class TestErrors:
    """
    Test cases for various exceptions being raised. This can be the basis for future fixes/workarounds
    """

    @pytest.mark.parametrize("table", [pytest.param(table_e0459)])
    def test_not_exactly_two_outgoing_edges_error(self, table: EbdTable):
        """
        Test the NotExactlyTwoOutgoingEdgesError
        """
        ebd_graph = convert_table_to_graph(table)
        with pytest.raises(NotExactlyTwoOutgoingEdgesError):
            _ = convert_graph_to_plantuml(ebd_graph)
