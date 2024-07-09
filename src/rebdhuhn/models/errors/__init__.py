"""
Specific error classes for errors that may occur in the data.
Using these exceptions allows to catch/filter more fine-grained.
"""

from typing import Optional

from rebdhuhn.models import DecisionNode, EbdTableRow, EbdTableSubRow, OutcomeNode


class NotExactlyTwoOutgoingEdgesError(NotImplementedError):
    """
    Raised if a decision node has more or less than 2 outgoing edges. This is not implemented in our logic yet.
    (Because it would be a multi-di-graph, not a di-graph.)
    See issue https://github.com/Hochfrequenz/rebdhuhn/issues/99 for a discussion on this topic.
    """

    def __init__(self, msg: str, decision_node_key: str, outgoing_edges: list[str]) -> None:
        """
        providing the keys allows to easily track down the exact cause of the error
        """
        super().__init__(msg)
        self.decision_node_key = decision_node_key
        self.outgoing_edges = outgoing_edges

    def __str__(self) -> str:
        return f"The node {self.decision_node_key} has more than 2 outgoing edges: {', '.join(self.outgoing_edges)}"


class PathsNotGreaterThanOneError(ValueError):
    """
    If indegree > 1, the number of paths should always be greater than 1 too.
    Typically, this is a symptom for loops in the graph (which makes them not a Directed Graph / tree anymore).
    """

    def __init__(self, node_key: str, indegree: int, number_of_paths: int) -> None:
        super().__init__(
            f"The indegree of node '{node_key}' is {indegree} > 1, but the number of paths is {number_of_paths} <= 1."
        )
        self.node_key = node_key
        self.indegree = indegree
        self.number_of_paths = number_of_paths


class GraphTooComplexForPlantumlError(Exception):
    """
    Exception raised when a Graph is too complex to convert with Plantuml.

    To understand what this means exactly, we first define the term "last common ancestor" (LCA in the following).
    Let V be an arbitrary node with indegree > 1.
    Define K_arr as the set of all possible paths K_i from the root node ("Start") to V.
    The LCA of V is the node in K_i which is the last common node (orientation is "Start" -> V)
    of all paths in K_arr. I.e. the node where the paths of K_arr split.

    The definition of the LCA is pictured in `src/last_common_ancestor.svg`.

    The graph is too complex for plantuml if there are multiple different nodes V with the same LCA.
    This is also pictured in `src/plantuml_not_convertable.svg`.

    Btw, the reason is the structure of the used Plantuml script language - as of now, maybe they change it in the
    future.
    """

    def __init__(
        self,
        message: str = "Plantuml conversion doesn't support multiple nodes for an ancestor node. The graph is too complex.",
    ) -> None:
        self.message = message
        super().__init__(self.message)


class EbdCrossReferenceNotSupportedError(NotImplementedError):
    """
    Raised when there is no outcome for a given sub row but a reference to another EBD key instead.
    See https://github.com/Hochfrequenz/rebdhuhn/issues/105 for an example / a discussion.
    """

    def __init__(self, decision_node: DecisionNode, row: EbdTableRow):
        cross_reference: Optional[str] = None
        for sub_row in row.sub_rows:
            if sub_row.note is not None and sub_row.note.startswith("EBD "):
                cross_reference = sub_row.note.split(" ")[1]
                break
        super().__init__(
            f"A cross reference from row {row} to {cross_reference} has been detected but is not supported"
        )
        self.row = row
        self.cross_reference = cross_reference
        self.decision_node = decision_node


class EndeInWrongColumnError(ValueError):
    """
    Raised when the subsequent step should be "Ende" but is not referenced in the respective column but as a note.
    This could be easily fixed but still, it needs to be done.
    I think this is more of a value error (because the raw source data are a mess) than a NotImplementedError.
    """

    def __init__(self, row: EbdTableRow):
        super().__init__(f"'Ende' in wrong column for row {row}")
        self.row = row


class OutcomeNodeCreationError(ValueError):
    """
    raised when the outcome node cannot be created from a sub row
    """

    def __init__(self, decision_node: DecisionNode, sub_row: EbdTableSubRow):
        super().__init__(f"Cannot create outcome node from sub row {sub_row} for DecisionNode {decision_node}.")
        self.sub_row = sub_row
        self.decision_node = decision_node


class OutcomeCodeAmbiguousError(ValueError):
    """
    Raised when the result nodes are ambiguous. This can be the case for "A**" results.
    """

    def __init__(self, outcome_node1: OutcomeNode, outcome_node2: OutcomeNode):
        super().__init__(f"Ambiguous result codes:  for [{outcome_node1, outcome_node2}].")
        self.outcome_nodes = [outcome_node1, outcome_node2]
