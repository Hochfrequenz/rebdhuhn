"""
contains the models for the outcome lookup, i.e. the answer to "what does a result code imply?"
"""

from pydantic import BaseModel, ConfigDict

from rebdhuhn.models.ebd_graph import EbdGraphMetaData
from rebdhuhn.models.ebd_table import MultiStepInstruction


class StepDescription(BaseModel):
    """
    The description of one step (a decision or a transition); the legend of an outcomes file.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_number: str
    """
    number of the Prüfschritt, e.g. '1', '2' or '6*'
    """

    question: str
    """
    the question of the DecisionNode or TransitionNode
    """

    note: str | None = None
    """
    The note of a transition step, which explains what the step does (e.g. how a list of hits is filled).
    None for decision steps and for transition steps without note.
    """


class PassedStep(BaseModel):
    """
    A step that was passed on the way to an outcome.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_number: str
    """
    number of the Prüfschritt, e.g. '1', '2' or '6*'; the question is found in EbdOutcomes.steps
    """

    answers: list[bool]
    """
    The answers that can lead to the outcome. In EBDs with loops a step can be passed more than once; an answer
    counts if the outcome can be reached after it without passing this step again (the answer given the last time).
    On EBDs without loops this is simply every answer that can lead to the outcome.
    [] means this is a transition step (no decision), [True] means "ja", [False] means "nein"
    and [False, True] means that either answer can lead to the outcome.
    """


class RouteStep(BaseModel):
    """
    One step of one concrete route from the start to an outcome.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_number: str
    """
    number of the Prüfschritt, e.g. '1', '2' or '6*'
    """

    answer: bool | None
    """
    the answer given in this step on this route; None for transition steps
    """


class Route(BaseModel):
    """
    One concrete route from the start to an outcome.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    steps: list[RouteStep]
    """
    the steps of the route in order of traversal
    """


class OutcomeExplanation(BaseModel):
    """
    Explains which steps were passed on the way to an outcome.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    key: str
    """
    The result code if there is one; 'Ende' for the EndNode; otherwise the key of the outcome node (its note).
    'Ende' means "the check ran to a bare Ende": routes that passed a transitional outcome (a result code with
    subsequent steps) earlier count like any other route.
    """

    result_code: str | None
    """
    The result code of the outcome, e.g. 'A55'. None for the EndNode and for outcomes without result code.
    Result codes are grouped literally: this explanation covers only nodes that carry exactly this code. If the EBD
    has a wildcard outcome 'A**' (see EbdOutcomes.has_wildcard_outcome), a received code may also come from that
    outcome, so read its notes and steps as well.
    """

    notes: list[str]
    """
    The distinct notes of all nodes that carry this outcome, in graph order. Notes that differ only in whitespace
    (or trailing punctuation) are the same note.
    """

    has_subsequent_steps: bool
    """
    True if at least one occurrence of this outcome is a TransitionalOutcomeNode.
    """

    certain_steps: list[PassedStep]
    """
    Steps that lie on every route from the start to this outcome, in order of traversal.
    Limitation: a transitional outcome on the way to a different outcome is not reported as a step.
    """

    possible_steps: list[PassedStep]
    """
    Steps that lie on at least one but not on every route to this outcome, sorted by step number.
    In EBDs with loops this includes steps that are only passed by going round a loop.
    """

    route_count: int | None
    """
    The number of distinct routes from the start to this outcome. None if routes to this outcome can loop (the steps
    between the start and this outcome contain a cycle). 0 if the outcome cannot be reached.
    """

    routes: list[Route] | None
    """
    All routes from the start to this outcome. None if there are more than max_routes of them,
    if the route count is unknown or if max_routes is 0.
    """


class DecisionConsequence(BaseModel):
    """
    The forward direction: which result codes are still reachable after a given answer to a decision step.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_number: str
    """
    number of the decision step, e.g. '1', '2' or '6*'; the question is found in EbdOutcomes.steps
    """

    answer: bool
    """
    the answer given
    """

    reachable_result_codes: list[str]
    """
    sorted, distinct result codes that are reachable after this answer
    """

    can_reach_end_without_result_code: bool
    """
    True if an EndNode or an outcome node that itself carries no result code is reachable after this answer
    (result codes with subsequent steps may have been produced on the way)
    """


class EbdOutcomes(BaseModel):
    """
    The outcome lookup of one EBD.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    metadata: EbdGraphMetaData
    """
    meta data of the EBD
    """

    steps: list[StepDescription]
    """
    every decision and transition step of the EBD exactly once (also steps that cannot be reached), sorted by step
    number (numeric part, then suffix). This is the only place of the question texts; the other parts of the file
    refer to a step by its step_number.
    """

    multi_step_instructions: list[MultiStepInstruction] | None = None
    """
    The multi-step instructions of the EBD, copied unchanged from the graph (None if there are none). They can change
    how the following steps are to be read (checks per item, collecting several codes). They are passed through but
    NOT evaluated: routes and step implications are derived from the graph structure only.
    """

    has_wildcard_outcome: bool
    """
    True if the EBD has an outcome with the wildcard result code 'A**'. Such an outcome stands for "some code, see
    note", so a received code may also stem from it, although the explanation of that code does not cover it.
    """

    outcomes: list[OutcomeExplanation]
    """
    one explanation per outcome, in natural order of the key (A01 < A99 < A100)
    """

    decisions: list[DecisionConsequence]
    """
    one entry per decision step and answer; sorted by step number (numeric part, then suffix), "nein" before "ja"
    """
