"""
This module contains the logic to explain the outcomes of an EBD graph:
Backward, which steps were passed on the way to an outcome, and forward, which result codes are still reachable
after a given answer to a decision step.
"""

import re
from collections import defaultdict
from collections.abc import Mapping

import networkx as nx  # type: ignore[import-untyped]

from rebdhuhn.graph_conversion import _normalize_note_for_comparison, _notes_same_except_for_whitespace
from rebdhuhn.models import (
    AssumedAnswer,
    DecisionConsequence,
    DecisionNode,
    EbdGraph,
    EbdOutcomes,
    EndNode,
    OutcomeExplanation,
    OutcomeNode,
    PassedStep,
    Route,
    RouteStep,
    StartNode,
    StepDescription,
    ToNoEdge,
    ToYesEdge,
)
from rebdhuhn.models.ebd_graph import _WILDCARD_RESULT_CODE, EbdGraphNode, TransitionalOutcomeNode, TransitionNode

_START_KEY = StartNode().get_key()
#: key of the virtual sink; contains a NUL character, so it cannot collide with a real node key
_SINK_KEY = "\0sink"

#: edge key of edges that do not stand for the answer to a decision (None would make networkx generate a key)
_NO_ANSWER = "-"


def _step_sort_key(step_number: str) -> tuple[int, str]:
    """sorts step numbers by their numeric part, then by suffix; e.g. '6' < '6*' < '7'"""
    match = re.fullmatch(r"(\d+)(\*?)", step_number)
    assert match is not None, f"Unexpected step number {step_number}"
    return int(match.group(1)), match.group(2)


def _natural_key(key: str) -> tuple[list[tuple[int, int, str]], str]:
    """natural sort key: 'A99' < 'A100'; total and deterministic for any key (digits < text, then the raw key)"""
    parts = [
        (0, int(part), "") if re.fullmatch("[0-9]+", part) else (1, 0, part)
        for part in re.split("([0-9]+)", key)
        if part
    ]
    return parts, key


def _node(graph: nx.DiGraph, key: str) -> EbdGraphNode:
    node: EbdGraphNode = graph.nodes[key]["node"]
    return node


def _as_answer(edge_key: bool | str) -> bool | None:
    """the answer an edge of the answer graph stands for; None if it does not stand for an answer"""
    return edge_key if isinstance(edge_key, bool) else None


def _get_answer_graph(graph: nx.DiGraph) -> nx.MultiDiGraph:
    """
    Returns a graph with the same nodes whose edges are keyed by the answer given on the edge (None for edges that
    leave a node which is not a decision). Out edges are added in a stable order: "nein" before "ja".
    The DiGraph holds only one edge per pair of nodes. If both answers of a decision lead to the same node (e.g. both
    to 'Ende'), it contains only one edge, which stands for both answers. The multigraph restores both.
    """
    result: nx.MultiDiGraph = nx.MultiDiGraph()
    result.add_nodes_from(graph.nodes)
    for key in graph.nodes:
        node = _node(graph, key)
        successors = sorted(graph.successors(key))
        if not isinstance(node, DecisionNode):
            result.add_edges_from((key, successor, _NO_ANSWER) for successor in successors)
            continue
        answers: list[tuple[bool, str]] = []
        for successor in successors:
            edge = graph.edges[key, successor]["edge"]
            if isinstance(edge, ToNoEdge):
                answers.append((False, successor))
            elif isinstance(edge, ToYesEdge):
                answers.append((True, successor))
            else:  # pragma: no cover
                raise ValueError(f"Unexpected edge {type(edge)} leaving the decision {key}")
        if len(successors) == 1:
            # Relies on the conversion creating an edge for every decision sub-row (a decision always has a "ja" and a
            # "nein" sub-row): one successor means both answers lead there (the DiGraph merges the two edges).
            answers = [(False, successors[0]), (True, successors[0])]
        answers.sort(key=lambda answer: answer[0])
        result.add_edges_from((key, successor, answer) for answer, successor in answers)
    return result


def _group_outcome_nodes(graph: nx.DiGraph) -> dict[str, list[str]]:
    """
    groups the keys of all outcome nodes (incl. the end node) by the key of the outcome (in graph order)
    """
    groups: dict[str, list[str]] = defaultdict(list)
    for key in graph.nodes:
        node = _node(graph, key)
        if isinstance(node, (OutcomeNode, TransitionalOutcomeNode)) and node.result_code is not None:
            groups[node.result_code].append(key)
        elif isinstance(node, (OutcomeNode, EndNode)):
            groups[key].append(key)
    return groups


def _count_routes(route_graph: nx.MultiDiGraph, outcome_nodes: set[str]) -> int | None:
    """
    Counts the routes from the start to the outcome by dynamic programming over the nodes between start and outcome
    (networkx has no path counting). Parallel edges (both answers to the same node) count twice.
    Returns None if these nodes contain a cycle.
    """
    if not nx.is_directed_acyclic_graph(route_graph):
        return None
    counts: dict[str, int] = defaultdict(int)
    counts[_START_KEY] = 1
    total = 0
    for key in nx.topological_sort(route_graph):
        count = counts[key]
        if key in outcome_nodes:
            total += count
            continue
        for _, successor in route_graph.out_edges(key):
            counts[successor] += count
    return total


def _enumerate_routes(graph: nx.DiGraph, route_graph: nx.MultiDiGraph, outcome_nodes: set[str]) -> list[Route]:
    """
    Lists all routes from the start to the outcome. Only call this if the route graph is acyclic and has few routes.
    """
    routes: list[Route] = []
    for edge_path in nx.all_simple_edge_paths(route_graph, _START_KEY, outcome_nodes):
        steps: list[RouteStep] = []
        for source, _, answer in edge_path:
            node = _node(graph, source)
            if isinstance(node, (DecisionNode, TransitionNode)):
                steps.append(RouteStep(step_number=node.step_number, answer=_as_answer(answer)))
        routes.append(Route(steps=steps))
    return routes


def _explain_outcome(  # pylint:disable=too-many-locals
    graph: nx.DiGraph,
    answer_graph: nx.MultiDiGraph,
    outcome_key: str,
    outcome_keys: list[str],
    max_routes: int,
) -> OutcomeExplanation:
    outcome_nodes = set(outcome_keys)
    nodes = [_node(graph, key) for key in outcome_keys]
    result_code: str | None = None
    notes: list[str] = []
    for node in nodes:
        if isinstance(node, (OutcomeNode, TransitionalOutcomeNode)):
            result_code = node.result_code or result_code
            if node.note is not None and not any(
                _notes_same_except_for_whitespace(
                    _normalize_note_for_comparison(node.note), _normalize_note_for_comparison(known)
                )
                for known in notes
            ):
                notes.append(node.note)

    # graph in which every route ends at its first node of the outcome, plus the virtual sink
    cut: nx.MultiDiGraph = answer_graph.copy()
    cut.remove_edges_from(list(cut.out_edges(outcome_keys, keys=True)))
    cut.add_edges_from((key, _SINK_KEY, _NO_ANSWER) for key in outcome_keys)
    reachable_from_start = nx.descendants(cut, _START_KEY)
    on_a_route: set[str] = set()
    certain_keys: list[str] = []
    if _SINK_KEY in reachable_from_start:
        on_a_route = (reachable_from_start | {_START_KEY}) & nx.ancestors(cut, _SINK_KEY)
        dominators = nx.immediate_dominators(cut, _START_KEY)
        dominator = dominators[_SINK_KEY]
        while dominator != _START_KEY:
            certain_keys.append(dominator)
            dominator = dominators[dominator]
        certain_keys.reverse()
    on_a_route.discard(_SINK_KEY)
    route_graph = cut.subgraph(on_a_route).copy()

    # answers = the answer given the last time the step is passed: the target must reach the outcome without passing
    # the step again. That can only make a difference for steps on a cycle.
    with_sink: nx.DiGraph = nx.DiGraph(cut.subgraph(on_a_route | {_SINK_KEY}))
    on_a_cycle = {
        key
        for component in nx.strongly_connected_components(with_sink)
        for key in component
        if len(component) > 1 or with_sink.has_edge(key, key)
    }

    def answers_of(key: str) -> list[bool]:
        candidates = [(_as_answer(answer), target) for _, target, answer in route_graph.out_edges(key, keys=True)]
        if key in on_a_cycle and len({answer for answer, _ in candidates}) > 1:
            # (at least one answer always remains: the last passing of a step on a route)
            removed_edges = [*with_sink.in_edges(key), *with_sink.out_edges(key)]
            with_sink.remove_node(key)
            reaching = nx.ancestors(with_sink, _SINK_KEY)  # a target equal to `key` is gone, so it never counts
            with_sink.add_node(key)
            with_sink.add_edges_from(removed_edges)
            candidates = [(answer, target) for answer, target in candidates if target in reaching]
        return sorted({answer for answer, _ in candidates if answer is not None})

    def passed_step(key: str) -> PassedStep | None:
        node = _node(graph, key)
        if isinstance(node, DecisionNode):
            return PassedStep(step_number=node.step_number, answers=answers_of(key))
        if isinstance(node, TransitionNode):
            return PassedStep(step_number=node.step_number, answers=[])
        return None

    certain = [step for step in (passed_step(key) for key in certain_keys) if step is not None]
    certain_numbers = {step.step_number for step in certain}
    possible = [
        step
        for step in (passed_step(key) for key in on_a_route)
        if step is not None and step.step_number not in certain_numbers
    ]
    possible.sort(key=lambda step: _step_sort_key(step.step_number))

    route_count: int | None = 0
    if on_a_route:
        route_count = _count_routes(route_graph, outcome_nodes)
    routes: list[Route] | None = None
    if route_count == 0 and max_routes > 0:
        routes = []  # unreachable outcome
    elif route_count is not None and 0 < max_routes and route_count <= max_routes:
        routes = _enumerate_routes(graph, route_graph, outcome_nodes)
    return OutcomeExplanation(
        key=outcome_key,
        result_code=result_code,
        notes=notes,
        has_subsequent_steps=any(isinstance(node, TransitionalOutcomeNode) for node in nodes),
        certain_steps=certain,
        possible_steps=possible,
        route_count=route_count,
        routes=routes,
    )


def _apply_assumptions(
    graph: nx.DiGraph, answer_graph: nx.MultiDiGraph, assume: Mapping[str, bool], ebd_code: str | None
) -> list[AssumedAnswer]:
    """
    Validates the assumed answers and removes (in place) every edge that stands for the excluded answer.
    Raises a ValueError for steps that do not exist or are no decision steps.
    """
    for step in assume:
        if step not in graph:
            raise ValueError(f"Step {step!r} does not exist in {ebd_code}")
        if not isinstance(_node(graph, step), DecisionNode):
            raise ValueError(f"Step {step!r} is no decision step (only decision steps have answers) in {ebd_code}")
        if not isinstance(assume[step], bool):
            raise ValueError(f"The answer assumed for step {step!r} must be True or False, not {assume[step]!r}")
    answer_graph.remove_edges_from(
        [
            (key, target, excluded)
            for key, answer in assume.items()
            for _, target, excluded in answer_graph.out_edges(key, keys=True)
            if excluded is not answer
        ]
    )
    return sorted(
        (AssumedAnswer(step_number=step, answer=answer) for step, answer in assume.items()),
        key=lambda assumed: _step_sort_key(assumed.step_number),
    )


def _explain_decisions(graph: nx.DiGraph, answer_graph: nx.MultiDiGraph) -> list[DecisionConsequence]:
    """
    the forward direction: which result codes are reachable after which answer
    """
    cache: dict[str, tuple[list[str], bool]] = {}

    def reachable(key: str) -> tuple[list[str], bool]:
        if key not in cache:
            codes: set[str] = set()
            reaches_end = False
            for reached_key in nx.descendants(answer_graph, key) | {key}:
                node = _node(graph, reached_key)
                if isinstance(node, (OutcomeNode, TransitionalOutcomeNode)) and node.result_code is not None:
                    codes.add(node.result_code)
                elif isinstance(node, (OutcomeNode, EndNode)):
                    reaches_end = True
            cache[key] = (sorted(codes), reaches_end)
        return cache[key]

    decisions: list[DecisionConsequence] = []
    for key, successor, answer in answer_graph.edges(keys=True):
        node = _node(graph, key)
        if not isinstance(node, DecisionNode):
            continue
        codes, reaches_end = reachable(successor)
        decisions.append(
            DecisionConsequence(
                step_number=node.step_number,
                answer=bool(answer),
                reachable_result_codes=codes,
                can_reach_end_without_result_code=reaches_end,
            )
        )
    decisions.sort(key=lambda decision: (_step_sort_key(decision.step_number), decision.answer))
    return decisions


def _describe_steps(graph: nx.DiGraph) -> list[StepDescription]:
    """the legend: every decision and transition step exactly once"""
    steps = [
        StepDescription(
            step_number=node.step_number,
            question=node.question,
            note=node.note if isinstance(node, TransitionNode) else None,
        )
        for _, node in graph.nodes(data="node")
        if isinstance(node, (DecisionNode, TransitionNode))
    ]
    steps.sort(key=lambda step: _step_sort_key(step.step_number))
    return steps


def _unreachable_steps(graph: nx.DiGraph, answer_graph: nx.MultiDiGraph) -> list[str]:
    """the numbers of the decision and transition steps that cannot be reached from the start"""
    reachable = nx.descendants(answer_graph, _START_KEY) | {_START_KEY}
    numbers = [
        node.step_number
        for key, node in graph.nodes(data="node")
        if isinstance(node, (DecisionNode, TransitionNode)) and key not in reachable
    ]
    return sorted(numbers, key=_step_sort_key)


def explain_outcomes(graph: EbdGraph, max_routes: int = 20, *, assume: Mapping[str, bool] | None = None) -> EbdOutcomes:
    """
    Explains the outcomes of the given EBD graph.

    For each outcome (all nodes with the same result code, or the end node) it tells which steps were passed with which
    answers (backward), for each decision and answer it tells which result codes can still be reached (forward).
    Routes are only enumerated if there are at most `max_routes` of them for an outcome (0 disables route lists).
    The route count is None if routes to an outcome can loop.
    The outcome 'Ende' (the EndNode) has no special rule: it means "the check ran to a bare Ende"; routes that passed
    a transitional outcome earlier count like any other route.
    Multi-step instructions of the graph are passed through to the result but NOT evaluated: routes and step
    implications are derived from the graph structure only. Result codes are grouped literally; see
    `EbdOutcomes.has_wildcard_outcome` for the wildcard code 'A**'.
    With `assume` (step number of a decision step -> answer, True = "ja") the analysis is done under the assumption
    that these steps are always answered so (on every pass of a loop). Steps that then cannot be reached are listed in
    `unreachable_steps`, an outcome that cannot be produced any more has `route_count == 0`. Unknown steps and steps
    that are no decision steps (transition steps, outcome keys, ...) raise a ValueError.
    """
    digraph: nx.DiGraph = graph.graph
    assume = assume or {}
    if _START_KEY not in digraph:  # e.g. the empty EBD
        if assume:
            raise ValueError(f"Step {next(iter(assume))!r} does not exist in {graph.metadata.ebd_code}")
        return EbdOutcomes(
            metadata=graph.metadata,
            steps=[],
            multi_step_instructions=graph.multi_step_instructions,
            has_wildcard_outcome=False,
            outcomes=[],
            decisions=[],
        )
    answer_graph = _get_answer_graph(digraph)
    assumed_answers = _apply_assumptions(digraph, answer_graph, assume, graph.metadata.ebd_code)
    outcomes = [
        _explain_outcome(digraph, answer_graph, outcome_key, outcome_keys, max_routes)
        for outcome_key, outcome_keys in _group_outcome_nodes(digraph).items()
    ]
    outcomes.sort(key=lambda outcome: _natural_key(outcome.key))
    return EbdOutcomes(
        metadata=graph.metadata,
        steps=_describe_steps(digraph),
        multi_step_instructions=graph.multi_step_instructions,
        assumed_answers=assumed_answers,
        unreachable_steps=_unreachable_steps(digraph, answer_graph),
        has_wildcard_outcome=any(outcome.result_code == _WILDCARD_RESULT_CODE for outcome in outcomes),
        outcomes=outcomes,
        decisions=_explain_decisions(digraph, answer_graph),
    )
