"""
Specific error classes for errors that may occur in the data.
Using these exceptions allows to catch/filter more fine-grained.
"""


class NotExactlyTwoOutgoingEdgesError(NotImplementedError):
    """
    Raised if a decision node has more or less than 2 outgoing edges. This is not implemented in our logic yet.
    (Because it would be a multi-di-graph, not a di-graph.)
    See issue https://github.com/Hochfrequenz/ebdtable2graph/issues/99 for a discussion on this topic.
    """

    def __init__(self, msg: str, decision_node_key, outgoing_edges: list[str]):
        """
        providing the keys allows to easily track down the exact cause of the error
        """
        super().__init__(msg)
        self.decision_node_key = decision_node_key
        self.outgoing_edges = outgoing_edges

    def __str__(self):
        return f"The node {self.decision_node_key} has more than 2 outgoing edges: {', '.join(self.outgoing_edges)}"


class PathsNotGreaterThanOneError(ValueError):
    """
    If indegree > 1, the number of paths should always be greater than 1 too.
    Typically, this is a symptom for loops in the graph (which makes them not a Directed Graph / tree anymore).
    """

    def __init__(self, node_key: str, indegree: int, number_of_paths: int):
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
        message="Plantuml conversion doesn't support multiple nodes for an ancestor node. The graph is too complex.",
    ):
        self.message = message
        super().__init__(self.message)
