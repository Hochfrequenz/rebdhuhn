import pytest  # type:ignore[import]

from ebdtable2graph import convert_graph_to_plantuml, convert_table_to_graph
from ebdtable2graph.models import EbdTable
from ebdtable2graph.models.errors import (
    EbdCrossReferenceNotSupportedError,
    EndeInWrongColumnError,
    GraphTooComplexForPlantumlError,
    NotExactlyTwoOutgoingEdgesError,
    PathsNotGreaterThanOneError,
)

from .e0266 import table_e0266
from .e0401 import e_0401
from .e0404 import e_0404
from .e0454 import table_e0454
from .e0459 import table_e0459
from .e0462 import table_e0462


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

    @pytest.mark.parametrize("table", [pytest.param(e_0401)])
    def test_key_error_because_first_node_has_key_other_than_1(self, table: EbdTable):
        _ = convert_table_to_graph(table)  # must _not_ raise a key error anymore

    @pytest.mark.parametrize("table", [pytest.param(e_0404)])
    def test_ende_in_wrong_column_error(self, table: EbdTable):
        with pytest.raises(EndeInWrongColumnError):
            _ = convert_table_to_graph(table)

    @pytest.mark.parametrize("table", [pytest.param(table_e0462)])
    def test_cross_reference_not_supported_error(self, table: EbdTable):
        with pytest.raises(EbdCrossReferenceNotSupportedError) as exc_info:
            _ = convert_table_to_graph(table)
        assert exc_info.value.cross_reference == "E_0402_Prüfen,"
