"""
The models sub-package contains the data models used:
1. a representation of the scraped EBD tables
2. the data model for the result of the conversion
"""

from rebdhuhn.models.ebd_graph import (
    DecisionNode,
    EbdGraph,
    EbdGraphEdge,
    EbdGraphMetaData,
    EbdGraphNode,
    EndNode,
    InstructionScope,
    OutcomeNode,
    StartNode,
    ToNoEdge,
    ToYesEdge,
)
from rebdhuhn.models.ebd_outcomes import (
    DecisionConsequence,
    EbdOutcomes,
    OutcomeExplanation,
    PassedStep,
    Route,
    RouteStep,
)
from rebdhuhn.models.ebd_table import (
    STEP_NUMBER_REGEX,
    EbdCheckResult,
    EbdDocumentReleaseInformation,
    EbdPruefidentifikator,
    EbdTable,
    EbdTableMetaData,
    EbdTableRow,
    EbdTableSubRow,
    MultiStepInstruction,
    Pruefidentifikator,
)

__all__ = [
    # ebd_graph models
    "DecisionNode",
    "EbdGraph",
    "EbdGraphEdge",
    "EbdGraphMetaData",
    "EbdGraphNode",
    "EndNode",
    "InstructionScope",
    "OutcomeNode",
    "StartNode",
    "ToNoEdge",
    "ToYesEdge",
    # ebd_outcomes models
    "DecisionConsequence",
    "EbdOutcomes",
    "OutcomeExplanation",
    "PassedStep",
    "Route",
    "RouteStep",
    # ebd_table models
    "STEP_NUMBER_REGEX",
    "EbdCheckResult",
    "EbdDocumentReleaseInformation",
    "EbdTable",
    "EbdTableMetaData",
    "EbdTableRow",
    "EbdTableSubRow",
    "MultiStepInstruction",
    "EbdPruefidentifikator",
    "Pruefidentifikator",
]
