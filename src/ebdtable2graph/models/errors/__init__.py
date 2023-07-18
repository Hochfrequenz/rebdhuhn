"""
Specific error classes for errors that may occur in the data.
Using these exceptions allows to catch/filter more fine-grained.
"""


class NotExactlyTwoOutgoingEdgesError(ValueError):
    """
    Raised if a decision node has more or less than 2 outgoing edges
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
