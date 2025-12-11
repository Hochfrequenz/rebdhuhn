"""
contains the graph side of things
"""

from abc import ABC, abstractmethod
from typing import Annotated, List, Optional, Union

from networkx import DiGraph  # type:ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field

# pylint:disable=too-few-public-methods
from rebdhuhn.models.ebd_table import RESULT_CODE_REGEX, MultiStepInstruction

#: regex used to validate step numbers, e.g. '4' or '7*'
_STEP_NUMBER_REGEX = r"^\d+\*?$"

#: Annotated type for step numbers in graph nodes
GraphStepNumber = Annotated[str, Field(pattern=_STEP_NUMBER_REGEX)]

#: Annotated type for result codes in graph nodes
GraphResultCode = Annotated[str, Field(pattern=RESULT_CODE_REGEX)]

#: Annotated type for subsequent step numbers (digits only, no 'Ende')
SubsequentStepNumberDigitsOnly = Annotated[str, Field(pattern=r"^\d+$")]


class EbdGraphMetaData(BaseModel):
    """
    Metadata of an EBD graph
    """

    model_config = ConfigDict(extra="forbid")

    # This class is (as of now) identical to EbdTableMetaData,
    # but they should be independent/decoupled from each other (no inheritance)
    # pylint:disable=duplicate-code
    ebd_code: str
    """
    ID of the EBD; e.g. 'E_0053'
    """
    chapter: str
    """
    Chapter from the EDI@Energy Document
    e.g. MaBis
    """
    section: str
    """
    Section from the EDI@Energy Document
    e.g. '7.24 AD:  Übermittlung Datenstatus für die Bilanzierungsgebietssummenzeitreihe vom BIKO an ÜNB und NB'
    """
    ebd_name: str
    """
    EBD name from the EDI@Energy Document
    e.g. 'E_0003_Bestellung der Aggregationsebene RZ prüfen'
    """
    role: str
    """
    e.g. 'BIKO' for "Prüfende Rolle: 'BIKO'"
    """
    remark: Optional[str] = None
    """
    remark for empty ebd sections, e.g. 'Derzeit ist für diese Entscheidung kein Entscheidungsbaum notwendig,
    da keine Antwort gegeben wird und ausschließlich die Liste versandt wird.'
    """


class EbdGraphNode(BaseModel, ABC):
    """
    Abstract Base Class of all Nodes in the EBD Graph
    This class defines the methods the nodes have to implement.
    All inheriting classes should use frozen = True.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    @abstractmethod
    def get_key(self) -> str:
        """
        returns a key that is unique for this node in the entire graph
        """
        raise NotImplementedError("The child class has to implement this method")

    def __str__(self) -> str:
        return self.get_key()

    def __hash__(self) -> int:
        # Required for networkx - frozen pydantic models are hashable
        return hash(self.get_key())


class DecisionNode(EbdGraphNode):  # networkx requirement: nodes are hashable (frozen=True)
    """
    A decision node is a question that can be answered with "ja" or "nein"
    (e.g. "Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?")
    """

    step_number: GraphStepNumber
    """
    number of the Prüfschritt, e.g. '1', '2' or '6*'
    """

    question: str
    """
    the questions which is asked at this node in the tree
    """

    def get_key(self) -> str:
        return self.step_number


class OutcomeNode(EbdGraphNode):  # networkx requirement: nodes are hashable (frozen=True)
    """
    An outcome node is a leaf of the Entscheidungsbaum tree. It has no subsequent steps.
    """

    result_code: Optional[GraphResultCode] = None
    """
    The outcome of the decision tree check; e.g. 'A55'
    """

    note: Optional[str] = None
    """
    An optional note for this outcome; e.g. 'Cluster:Ablehnung\nFristüberschreitung'
    """

    def get_key(self) -> str:
        if self.result_code is not None:
            return self.result_code
        assert self.note is not None
        return self.note


class EndNode(EbdGraphNode):  # networkx requirement: nodes are hashable (frozen=True)
    """
    There is only one end node per graph. It is the "exit" of the decision tree.
    """

    def get_key(self) -> str:
        return "Ende"


class StartNode(EbdGraphNode):  # networkx requirement: nodes are hashable (frozen=True)
    """
    There is only one starting node per graph; e.g. 'E0401'. This starting node is always connected to a very first
    decision node by a "normal" edge.
    Note: The information 'E0401' is stored in the metadata instance not in the starting node.
    """

    def get_key(self) -> str:
        return "Start"


class EmptyNode(EbdGraphNode):  # networkx requirement: nodes are hashable (frozen=True)
    """
    This is a node which will contain the hints for the cases where a EBD key has no table.
    E.g. E_0534 -> Es ist das EBD E_0527 zu nutzen.
    """

    def get_key(self) -> str:
        return "Empty"


class TransitionalOutcomeNode(EbdGraphNode):  # networkx requirement: nodes are hashable (frozen=True)
    """
    An outcome node with subsequent steps.
    """

    result_code: GraphResultCode
    """
    The outcome of the decision tree check; e.g. 'A55'
    """
    subsequent_step_number: SubsequentStepNumberDigitsOnly
    """
    The number of the subsequent step, e.g. '2' or 'Ende'. Needed for key generation.
    """

    note: Optional[str] = None
    """
    An optional note for this outcome; e.g. 'Cluster:Ablehnung\nFristüberschreitung'
    """

    def get_key(self) -> str:
        return self.result_code + "_" + self.subsequent_step_number


class TransitionNode(EbdGraphNode):
    """
    A transition node is a leaf of the Entscheidungsbaum tree.
    It has exactly one subsequent step and does neither contain a decision nor an outcome.
    Its fields are the same as the DecisionNode, but they are functionally different.
    It's related to an EbdCheckResult/SubRow which has a check_result.result None and only 1 subsequent step number.
    """

    step_number: GraphStepNumber
    """
    number of the Prüfschritt, e.g. '105', '2' or '6*'
    """
    question: str
    """
    the questions which is asked at this node in the tree
    """
    note: Optional[str] = None
    """
    An optional note that explains the purpose, e.g.
    'Aufnahme von 0..n Treffern in die neue Trefferliste auf Basis von drei Kriterien'
    """

    def get_key(self) -> str:
        return self.step_number


class EbdGraphEdge(BaseModel):
    """
    base class of all edges in an EBD Graph
    """

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    source: EbdGraphNode
    """
    the origin/source of the edge
    """
    target: EbdGraphNode
    """
    the destination/target of the edge
    """
    note: Optional[str] = None
    """
    An optional note for this edge.
    If the note doesn't refer to a OutcomeNode - e.g. 'Cluster:Ablehnung\nFristüberschreitung' -
    the note will be a property of the edge.
    """


class ToYesEdge(EbdGraphEdge):
    """
    an edge that connects a DecisionNode with the positive next step
    """

    source: DecisionNode
    """
    the source whose outcome is True ("Ja")
    """


class ToNoEdge(EbdGraphEdge):
    """
    an edge that connects a DecisionNode with the negative next step
    """

    source: DecisionNode
    """
    ths source whose outcome is False ("Nein")
    """


class TransitionEdge(EbdGraphEdge):
    """
    an edge that connects a TransitionNode to the respective next step
    """

    source: TransitionNode
    """
    ths source which refers to the next step
    """


class TransitionalOutcomeEdge(EbdGraphEdge):
    """
    an edge that connects a transitional outcome node from the last or to the respective next step
    """

    source: Union[DecisionNode, TransitionalOutcomeNode]
    """
    ths source which refers to the next step
    """


class EbdGraph(BaseModel):
    """
    EbdGraph is the structured representation of an Entscheidungsbaumdiagramm
    """

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    metadata: EbdGraphMetaData
    """
    meta data of the graph
    """

    graph: DiGraph
    """
    The networkx graph
    """

    # pylint: disable=duplicate-code
    multi_step_instructions: Optional[List[MultiStepInstruction]] = None
    """
    If this is not None, it means that from some point in the EBD onwards, the user is thought to obey additional
    instructions. There might be more than one of these instructions in one EBD table.
    """

    # pylint:disable=fixme
    # todo @leon: fill it with all the things you need
