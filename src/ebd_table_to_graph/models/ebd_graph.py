"""
contains the graph side of things
"""
import attrs
from networkx import DiGraph  # type:ignore[import]

from ebd_table_to_graph.models.ebd_table import EbdTableMetaData

# pylint:disable=too-few-public-methods


class EbdGraphMetaData(EbdTableMetaData):
    """
    Metadata of an EBD graph
    """

    # pylint:disable=fixme
    # todo: this class is (as of now) identical to EbdTableMetaData,
    # but in the long term they should be independent/decoupled from each other (no inheritance)


@attrs.define(auto_attribs=True, kw_only=True)
class EbdGraph:
    """
    EbdGraph is the structured representation of an Entscheidungsbaumdiagramm
    """

    metadata: EbdGraphMetaData = attrs.field()
    """
    meta data of the graph
    """

    graph: DiGraph = attrs.field(validator=attrs.validators.instance_of(DiGraph))
    """
    The networkx graph
    """

    # pylint:disable=fixme
    # todo @leon: fill it with all the things you need
