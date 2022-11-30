"""
contains the graph side of things
"""
from typing import Optional, Union

import attrs
from networkx import DiGraph  # type:ignore[import]

# pylint:disable=too-few-public-methods


@attrs.define(auto_attribs=True, kw_only=True)
class EbdGraphMetaData:
    """
    Metadata of an EBD graph
    """

    # This class is (as of now) identical to EbdTableMetaData,
    # but they should be independent/decoupled from each other (no inheritance)
    # pylint:disable=duplicate-code
    ebd_code: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    ID of the EBD; e.g. 'E_0053'
    """
    chapter: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    Chapter from the EDI@Energy Document
    e.g. '7.24 AD:  Übermittlung Datenstatus für die Bilanzierungsgebietssummenzeitreihe vom BIKO an ÜNB und NB'
    """
    sub_chapter: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    Sub Chapter from the EDI@Energy Document
    e.g. '7.24.1 Datenstatus nach erfolgter Bilanzkreisabrechnung vergeben'
    """
    role: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    e.g. 'BIKO' for "Prüfende Rolle: 'BIKO'"
    """


@attrs.define(auto_attribs=True, kw_only=True)
class DecisionNode:
    """
    A decision node is a question that can be answered with "ja" or "nein"
    (e.g. "Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?")
    """

    question: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    the questions which is asked at this node in the tree
    """


@attrs.define(auto_attribs=True, kw_only=True)
class OutcomeNode:
    """
    An outcome node is a leaf of the Entscheidungsbaum tree. It has no subsequent steps.
    """

    result_code: Optional[str] = attrs.field(
        validator=attrs.validators.optional(attrs.validators.matches_re(r"^[A-Z]\d+$"))
    )
    """
    The outcome of the decision tree check; e.g. 'A55'
    """

    note: Optional[str] = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
    """
    An optional note for this outcome; e.g. 'Cluster:Ablehnung\nFristüberschreitung'
    """


EbdGraphNodes = Union[DecisionNode, OutcomeNode]
"""
a union type hint for all possible nodes within an EBD Graph
"""


@attrs.define(auto_attribs=True, kw_only=True)
class EbdGraph:
    """
    EbdGraph is the structured representation of an Entscheidungsbaumdiagramm
    """

    metadata: EbdGraphMetaData = attrs.field(validator=attrs.validators.instance_of(EbdGraphMetaData))
    """
    meta data of the graph
    """

    graph: DiGraph = attrs.field(validator=attrs.validators.instance_of(DiGraph))
    """
    The networkx graph
    """

    # pylint:disable=fixme
    # todo @leon: fill it with all the things you need
