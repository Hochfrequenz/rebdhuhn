"""
contains the graph side of things
"""

from abc import ABC, abstractmethod
from typing import List, Optional

import attrs
from networkx import DiGraph  # type:ignore[import-untyped]

# pylint:disable=too-few-public-methods
from rebdhuhn.models.ebd_table import RESULT_CODE_REGEX, MultiStepInstruction


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
    e.g. MaBis
    """
    section: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    Section from the EDI@Energy Document
    e.g. '7.24 AD:  Übermittlung Datenstatus für die Bilanzierungsgebietssummenzeitreihe vom BIKO an ÜNB und NB'
    """
    ebd_name: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    EBD name from the EDI@Energy Document
    e.g. 'E_0003_Bestellung der Aggregationsebene RZ prüfen'
    """
    role: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    e.g. 'BIKO' for "Prüfende Rolle: 'BIKO'"
    """
    remark: Optional[str] = attrs.field(
        default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str))
    )
    """
    remark for empty ebd sections, e.g. 'Derzeit ist für diese Entscheidung kein Entscheidungsbaum notwendig,
    da keine Antwort gegeben wird und ausschließlich die Liste versandt wird.'
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

    def __str__(self) -> str:
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

    result_code: Optional[str] = attrs.field(
        default=None, validator=attrs.validators.optional(attrs.validators.matches_re(RESULT_CODE_REGEX))
    )
    """
    The outcome of the decision tree check; e.g. 'A55'
    """

    note: Optional[str] = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
    """
    An optional note for this outcome; e.g. 'Cluster:Ablehnung\nFristüberschreitung'
    """

    def get_key(self) -> str:
        if self.result_code is not None:
            return self.result_code
        assert self.note is not None
        return self.note


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


@attrs.define(auto_attribs=True, kw_only=True, frozen=True)  # networkx requirement: nodes are hashable (frozen=True)
class EmptyNode(EbdGraphNode):
    """
    This is a node which will contain the hints for the cases where a EBD key has no table.
    E.g. E_0534 -> Es ist das EBD E_0527 zu nutzen.
    """

    def get_key(self) -> str:
        return "Empty"


@attrs.define(auto_attribs=True, kw_only=True, frozen=True)
class TransitionNode(EbdGraphNode):
    """
    A transition node is a leaf of the Entscheidungsbaum tree.
    It has exactly one subsequent step and does neither contain a decision nor an outcome.
    Its fields are the same as the DecisionNode, but they are functionally different.
    It's related to an EbdCheckResult/SubRow which has a check_result.result None and only 1 subsequent step number.
    """

    step_number: str = attrs.field(validator=attrs.validators.matches_re(r"\d+\*?"))
    """
    number of the Prüfschritt, e.g. '105', '2' or '6*'
    """
    question: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    the questions which is asked at this node in the tree
    """
    note: Optional[str] = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
    """
    An optional note that explains the purpose, e.g.
    'Aufnahme von 0..n Treffern in die neue Trefferliste auf Basis von drei Kriterien'
    """

    def get_key(self) -> str:
        return self.step_number


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
class TransitionEdge(EbdGraphEdge):
    """
    an edge that connects a TransitionNode to the respective next step
    """

    source: TransitionNode = attrs.field(validator=attrs.validators.instance_of(TransitionNode))
    """
    ths source which refers to the next step
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
