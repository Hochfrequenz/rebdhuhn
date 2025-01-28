import pytest

from rebdhuhn import convert_graph_to_plantuml, convert_table_to_graph
from rebdhuhn.models import EbdTable
from rebdhuhn.models.errors import (
    EbdCrossReferenceNotSupportedError,
    EndeInWrongColumnError,
    GraphTooComplexForPlantumlError,
    NotExactlyTwoOutgoingEdgesError,
    OutcomeCodeAndFurtherStepError,
    PathsNotGreaterThanOneError,
)

from .e0266 import table_e0266
from .e0401 import e_0401
from .e0404 import e_0404
from .e0454 import table_e0454
from .e0459 import table_e0459
from .e0462 import table_e0462
from .e0529 import e_0529


class TestErrors:
    """
    Test cases for various exceptions being raised. This can be the basis for future fixes/workarounds
    """

    @pytest.mark.parametrize("table", [pytest.param(table_e0459)])
    def test_not_exactly_two_outgoing_edges_error(self, table: EbdTable) -> None:
        ebd_graph = convert_table_to_graph(table)
        with pytest.raises(NotExactlyTwoOutgoingEdgesError):
            _ = convert_graph_to_plantuml(ebd_graph)

    @pytest.mark.parametrize("table", [pytest.param(table_e0266)])
    def test_loops_in_the_tree_error(self, table: EbdTable) -> None:
        with pytest.raises(OutcomeCodeAndFurtherStepError):
            _ = convert_table_to_graph(table)

    @pytest.mark.parametrize("table", [pytest.param(table_e0454)])
    def test_too_complex_for_plantuml(self, table: EbdTable) -> None:
        ebd_graph = convert_table_to_graph(table)
        with pytest.raises(GraphTooComplexForPlantumlError):
            _ = convert_graph_to_plantuml(ebd_graph)

    @pytest.mark.snapshot
    @pytest.mark.parametrize("table", [pytest.param(e_0401)])
    def test_key_error_because_first_node_has_key_other_than_1(self, table: EbdTable) -> None:
        _ = convert_table_to_graph(table)  # must _not_ raise a key error anymore

    @pytest.mark.snapshot
    @pytest.mark.parametrize("table", [pytest.param(e_0529)])
    def test_backreference_to_missing_node_with_key_1(self, table: EbdTable) -> None:
        graph = convert_table_to_graph(table)
        _ = convert_graph_to_plantuml(graph)  # must _not_ raise an assertion error anymore

    @pytest.mark.parametrize("table", [pytest.param(e_0404)])
    def test_ende_in_wrong_column_error(self, table: EbdTable) -> None:
        with pytest.raises(EndeInWrongColumnError):
            _ = convert_table_to_graph(table)

    @pytest.mark.parametrize("table", [pytest.param(table_e0462)])
    def test_cross_reference_not_supported_error(self, table: EbdTable) -> None:
        with pytest.raises(EbdCrossReferenceNotSupportedError) as exc_info:
            _ = convert_table_to_graph(table)
        assert exc_info.value.cross_reference == "E_0402_Prüfen,"
