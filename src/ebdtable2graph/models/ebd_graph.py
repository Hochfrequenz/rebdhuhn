"""
contains the graph side of things
"""

from abc import ABC, abstractmethod
from typing import List, Optional

import attrs
from networkx import DiGraph  # type:ignore[import]

# pylint:disable=too-few-public-methods
from ebdtable2graph.models.ebd_table import RESULT_CODE_REGEX, MultiStepInstruction


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


class EbdGraphNode(ABC):
    """
    Abstract Base Class of all Nodes in the EBD Graph
    This class defines the methods the nodes have to implement.
    All inheriting classes should use frozen = True as attrs-argument.
    """

    @abstractmethod
    def get_key(self) -> str:
        """
        returns a key that is unique for this node in the entire graph
        """
        raise NotImplementedError("The child class has to implement this method")

    def __str__(self):
        return self.get_key()


@attrs.define(auto_attribs=True, kw_only=True, frozen=True)
class DecisionNode(EbdGraphNode):  # networkx requirement: nodes are hashable (frozen=True)
    """
    A decision node is a question that can be answered with "ja" or "nein"
    (e.g. "Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?")
    """

    step_number: str = attrs.field(validator=attrs.validators.matches_re(r"\d+\*?"))
    """
    number of the Prüfschritt, e.g. '1', '2' or '6*'
    """

    question: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    the questions which is asked at this node in the tree
    """

    def get_key(self) -> str:
        return self.step_number


@attrs.define(auto_attribs=True, kw_only=True, frozen=True)  # networkx requirement: nodes are hashable (frozen=True)
class OutcomeNode(EbdGraphNode):
    """
    An outcome node is a leaf of the Entscheidungsbaum tree. It has no subsequent steps.
    """

    result_code: str = attrs.field(validator=attrs.validators.matches_re(RESULT_CODE_REGEX))
    """
    The outcome of the decision tree check; e.g. 'A55'
    """

    note: Optional[str] = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
    """
    An optional note for this outcome; e.g. 'Cluster:Ablehnung\nFristüberschreitung'
    """

    def get_key(self) -> str:
        return self.result_code


@attrs.define(auto_attribs=True, kw_only=True, frozen=True)  # networkx requirement: nodes are hashable (frozen=True)
class EndNode(EbdGraphNode):
    """
    There is only one end node per graph. It is the "exit" of the decision tree.
    """

    def get_key(self) -> str:
        return "Ende"


@attrs.define(auto_attribs=True, kw_only=True, frozen=True)  # networkx requirement: nodes are hashable (frozen=True)
class StartNode(EbdGraphNode):
    """
    There is only one starting node per graph; e.g. 'E0401'. This starting node is always connected to a very first
    decision node by a "normal" edge.
    Note: The information 'E0401' is stored in the metadata instance not in the starting node.
    """

    def get_key(self) -> str:
        return "Start"


@attrs.define(auto_attribs=True, kw_only=True)
class EbdGraphEdge:
    """
    base class of all edges in an EBD Graph
    """

    source: EbdGraphNode = attrs.field()
    """
    the origin/source of the edge
    """
    target: EbdGraphNode = attrs.field()
    """
    the destination/target of the edge
    """
    note: Optional[str] = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
    """
    An optional note for this edge.
    If the note doesn't refer to a OutcomeNode - e.g. 'Cluster:Ablehnung\nFristüberschreitung' -
    the note will be a property of the edge.
    """


@attrs.define(auto_attribs=True, kw_only=True)
class ToYesEdge(EbdGraphEdge):
    """
    an edge that connects a DecisionNode with the positive next step
    """

    source: DecisionNode = attrs.field(validator=attrs.validators.instance_of(DecisionNode))
    """
    the source whose outcome is True ("Ja")
    """


@attrs.define(auto_attribs=True, kw_only=True)
class ToNoEdge(EbdGraphEdge):
    """
    an edge that connects a DecisionNode with the negative next step
    """

    source: DecisionNode = attrs.field(validator=attrs.validators.instance_of(DecisionNode))
    """
    ths source whose outcome is False ("Nein")
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

    # pylint: disable=duplicate-code
    multi_step_instructions: Optional[List[MultiStepInstruction]] = attrs.field(
        validator=attrs.validators.optional(
            attrs.validators.deep_iterable(  # type:ignore[arg-type]
                member_validator=attrs.validators.instance_of(MultiStepInstruction),
                iterable_validator=attrs.validators.min_len(1),  # if the list is not None, then it has to have entries
            )
        ),
        default=None,
    )
    """
    If this is not None, it means that from some point in the EBD onwards, the user is thought to obey additional
    instructions. There might be more than one of these instructions in one EBD table.
    """

    # pylint:disable=fixme
    # todo @leon: fill it with all the things you need
