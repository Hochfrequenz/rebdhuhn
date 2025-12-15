"""
contains the graph side of things
"""

import re
from abc import ABC, abstractmethod
from typing import Annotated, List, Optional, Union

from networkx import DiGraph  # type:ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field, model_validator

# pylint:disable=too-few-public-methods
from rebdhuhn.models.ebd_table import (
    EBD_REFERENCE_REGEX,
    RESULT_CODE_REGEX,
    EbdDocumentReleaseInformation,
    MultiStepInstruction,
)


class InstructionScope(BaseModel):
    """
    Represents the scope of a multi-step instruction within an EBD graph.

    The scope defines which steps are affected by the instruction, from start_step
    until end_step (inclusive), or until the end of the graph if end_step is None.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    instruction: MultiStepInstruction
    """The multi-step instruction."""

    start_step: str
    """The first step number affected (from instruction.first_step_number_affected)."""

    end_step: str | None
    """
    The last step number affected (inclusive), or None if this is the last instruction
    (meaning it extends to the end of the graph).

    When end_step is set to a value less than start_step (e.g., start_step - 1),
    it indicates an empty range with no steps.
    """

    @model_validator(mode="after")
    def validate_start_step_matches_instruction(self) -> "InstructionScope":
        """Validate that start_step matches the instruction's first_step_number_affected."""
        if self.start_step != self.instruction.first_step_number_affected:
            raise ValueError(
                f"start_step ({self.start_step}) must match "
                f"instruction.first_step_number_affected ({self.instruction.first_step_number_affected})"
            )
        return self


#: Wildcard result code "A**" used in EBDs when the actual code is determined dynamically at runtime.
#: This code can appear multiple times in an EBD with different notes explaining which codes it represents.
#: Example: In E_0055, "A**" appears in steps 1 and 2 with different possible replacement codes.
#: To handle this, OutcomeNode.get_key() generates unique keys for A** nodes by combining code and note.
_WILDCARD_RESULT_CODE = "A**"

#: regex used to validate step numbers, e.g. '4' or '7*'
_STEP_NUMBER_REGEX = r"^\d+\*?$"

#: Annotated type for step numbers in graph nodes
GraphStepNumber = Annotated[str, Field(pattern=_STEP_NUMBER_REGEX)]

#: Annotated type for result codes in graph nodes
GraphResultCode = Annotated[str, Field(pattern=RESULT_CODE_REGEX)]

#: Annotated type for subsequent step numbers (digits only, no 'Ende')
SubsequentStepNumberDigitsOnly = Annotated[str, Field(pattern=r"^\d+$")]

#: regex used to validate EBD codes, e.g. 'E_0621'
_EBD_CODE_REGEX = r"^E_\d{4}$"

#: Annotated type for EBD codes (e.g., 'E_0621')
GraphEbdCode = Annotated[str, Field(pattern=_EBD_CODE_REGEX)]


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

    release_information: Optional[EbdDocumentReleaseInformation] = None
    """
    metadata of the entire EBD document (not the single EBD table)
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

    ebd_references: list[GraphEbdCode] = Field(default_factory=list)
    """
    EBD codes referenced in the note field, e.g., ["E_0621"].
    Automatically extracted from note using EBD_REFERENCE_REGEX.
    """

    @model_validator(mode="before")
    @classmethod
    def extract_ebd_references(cls, data: dict) -> dict:  # type: ignore[type-arg]
        """Extract EBD references from note using regex."""
        if isinstance(data, dict) and data.get("note"):
            data["ebd_references"] = re.findall(EBD_REFERENCE_REGEX, data["note"])
        return data

    def get_key(self) -> str:
        if self.result_code is not None:
            if self.result_code == _WILDCARD_RESULT_CODE and self.note is not None:
                # Use both code and note to create a unique key
                return f"{_WILDCARD_RESULT_CODE}: {self.note}"
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
    The number of the subsequent step, e.g. '2' or '110'. Needed for key generation.
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

    def get_all_step_numbers(self) -> set[str]:
        """Returns all step numbers from nodes that have a step_number attribute."""
        step_numbers: set[str] = set()
        for node_key in self.graph.nodes:
            node = self.graph.nodes[node_key]["node"]
            if hasattr(node, "step_number"):
                step_numbers.add(str(node.step_number))
        return step_numbers

    def get_instruction_scopes(self) -> list[InstructionScope]:
        """
        Determines which steps each multi-step instruction affects.

        Instructions are sorted by first_step_number_affected. Each instruction's scope
        extends from its start step until the step before the next instruction begins.
        The last instruction's scope extends to the end of the graph (end_step=None).

        Step numbers are compared as integers, so "100" < "205" < "305".
        """
        if not self.multi_step_instructions:
            return []

        all_step_numbers = self.get_all_step_numbers()
        by_start_step = sorted(self.multi_step_instructions, key=lambda x: int(x.first_step_number_affected))
        scopes: list[InstructionScope] = []

        for i, instruction in enumerate(by_start_step):
            start_step = instruction.first_step_number_affected
            is_last_instruction = i + 1 >= len(by_start_step)

            if is_last_instruction:
                end_step = None
            else:
                next_instruction_start = int(by_start_step[i + 1].first_step_number_affected)
                end_step = self._find_max_step_in_range(all_step_numbers, int(start_step), next_instruction_start)
                if end_step is None:
                    # No steps in range: create empty scope by setting end < start
                    end_step = str(int(start_step) - 1)

            scopes.append(InstructionScope(instruction=instruction, start_step=start_step, end_step=end_step))

        return scopes

    @staticmethod
    def _find_max_step_in_range(all_step_numbers: set[str], start: int, end_exclusive: int) -> str | None:
        """Returns the highest step number in [start, end_exclusive), or None if empty."""
        max_step: str | None = None
        max_value = -1
        for step in all_step_numbers:
            step_value = int(step)
            if start <= step_value < end_exclusive and step_value > max_value:
                max_value = step_value
                max_step = step
        return max_step

    # pylint:disable=fixme
    # todo @leon: fill it with all the things you need
