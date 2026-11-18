"""
Tests for the outcome lookup (explain_outcomes)
"""

import json
import time
from pathlib import Path
from typing import Any, Literal

import pytest
from pydantic import BaseModel, ValidationError
from syrupy.assertion import SnapshotAssertion

from rebdhuhn import EbdGraph, EbdOutcomes, EbdTable, convert_table_to_graph, explain_outcomes
from rebdhuhn.models import (
    DecisionNode,
    EbdCheckResult,
    EbdTableMetaData,
    EbdTableRow,
    EbdTableSubRow,
    OutcomeExplanation,
    OutcomeNode,
    Route,
    RouteStep,
    StepDescription,
    ToNoEdge,
    ToYesEdge,
)
from rebdhuhn.models.ebd_graph import TransitionalOutcomeNode
from unittests.e0266 import table_e0266
from unittests.e0454 import table_e0454
from unittests.e0459 import table_e0459
from unittests.e0462 import table_e0462
from unittests.e0487 import table_e0487
from unittests.examples import table_e0003, table_e0015, table_e0025, table_e0401
from unittests.table_with_transition_node import table_0594_partly

_test_files = Path(__file__).parent / "test_files"


def _load(file_name: str) -> EbdTable:
    with open(_test_files / file_name, encoding="utf-8") as f:
        return EbdTable.model_validate(json.load(f))


def _sub_row(result: bool, next_step: str | None, code: str | None = None, note: str | None = None) -> EbdTableSubRow:
    return EbdTableSubRow(
        check_result=EbdCheckResult(result=result, subsequent_step_number=next_step), result_code=code, note=note
    )


def _table(rows: list[EbdTableRow]) -> EbdTable:
    return EbdTable(
        metadata=EbdTableMetaData(ebd_code="E_9999", chapter="c", section="s", ebd_name="E_9999_test", role="r"),
        rows=rows,
    )


#: 1 ja -> 2, 1 nein -> 3; 2 ja -> A05, 2 nein -> 3; 3 ja -> A05, 3 nein -> A06
_diamond = _table(
    [
        EbdTableRow(step_number="1", description="eins?", sub_rows=[_sub_row(True, "2"), _sub_row(False, "3")]),
        EbdTableRow(
            step_number="2", description="zwei?", sub_rows=[_sub_row(True, None, "A05", "fuenf"), _sub_row(False, "3")]
        ),
        EbdTableRow(
            step_number="3",
            description="drei?",
            sub_rows=[_sub_row(True, None, "A05", "fuenf"), _sub_row(False, None, "A06", "sechs")],
        ),
    ]
)

#: 1 nein -> A01 and then step 2 (transitional outcome), 1 ja -> 2; 2 nein -> A02; 2 ja -> Ende
_transitional = _table(
    [
        EbdTableRow(
            step_number="1", description="eins?", sub_rows=[_sub_row(True, "2"), _sub_row(False, "2", "A01", "weiter")]
        ),
        EbdTableRow(
            step_number="2",
            description="zwei?",
            sub_rows=[_sub_row(True, "Ende"), _sub_row(False, None, "A02", "zwei")],
        ),
    ]
)

#: both answers of step 2 lead to the same node
_same_target = _table(
    [
        EbdTableRow(step_number="1", description="eins?", sub_rows=[_sub_row(True, "2"), _sub_row(False, None, "A01")]),
        EbdTableRow(step_number="2", description="zwei?", sub_rows=[_sub_row(True, "Ende"), _sub_row(False, "Ende")]),
    ]
)


def _by_key(outcomes: EbdOutcomes) -> dict[str, OutcomeExplanation]:
    return {outcome.key: outcome for outcome in outcomes.outcomes}


def _steps(outcome: OutcomeExplanation, certain: bool = True) -> list[tuple[str, list[bool]]]:
    return [(s.step_number, s.answers) for s in (outcome.certain_steps if certain else outcome.possible_steps)]


class TestSteps:
    """the legend: every step exactly once, with its question"""

    def test_steps_of_hand_made_tables(self) -> None:
        assert explain_outcomes(convert_table_to_graph(_diamond)).steps == [
            StepDescription(step_number="1", question="eins?"),
            StepDescription(step_number="2", question="zwei?"),
            StepDescription(step_number="3", question="drei?"),
        ]
        assert explain_outcomes(convert_table_to_graph(table_e0003)).steps == [
            StepDescription(step_number="1", question="Erfolgt der Eingang der Bestellung fristgerecht?"),
            StepDescription(step_number="2", question="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?"),
        ]

    def test_transition_step_is_in_the_legend(self) -> None:
        steps = explain_outcomes(convert_table_to_graph(table_0594_partly)).steps
        assert [step.step_number for step in steps] == ["270", "275", "280"]
        assert steps[1].question == "Vollständige [Adressprüfung]"
        assert [step.note for step in steps] == [
            None,
            "Aufnahme von 0..n Treffern in die Trefferliste auf Basis der alleinigen Adressprüfung",
            None,
        ]  # only transition steps have a note

    def test_unreachable_step_is_in_the_legend_and_steps_are_sorted(self) -> None:
        graph = convert_table_to_graph(_diamond)
        nine = DecisionNode(step_number="10", question="zehn?")
        graph.graph.add_node("10", node=nine)
        assert [step.step_number for step in explain_outcomes(graph).steps] == ["1", "2", "3", "10"]

    def test_multi_step_instructions_are_passed_through(self) -> None:
        graph = _all_tables["e0594_fv2504"]
        assert graph.multi_step_instructions is not None
        result = explain_outcomes(graph)
        assert result.multi_step_instructions == graph.multi_step_instructions
        assert [i.first_step_number_affected for i in result.multi_step_instructions or []] == [
            "100",
            "205",
            "305",
            "400",
        ]
        assert EbdOutcomes.model_validate_json(result.model_dump_json()).multi_step_instructions == (
            graph.multi_step_instructions
        )
        assert explain_outcomes(convert_table_to_graph(table_e0003)).multi_step_instructions is None
        assert list(EbdOutcomes.model_fields)[:3] == ["metadata", "steps", "multi_step_instructions"]

    def test_wildcard_flag(self) -> None:
        assert explain_outcomes(_all_tables["e0055"]).has_wildcard_outcome
        assert not explain_outcomes(convert_table_to_graph(table_e0003)).has_wildcard_outcome
        assert not explain_outcomes(convert_table_to_graph(_diamond)).has_wildcard_outcome

    def test_empty_ebd_has_no_steps(self) -> None:
        assert explain_outcomes(convert_table_to_graph(_load("e0452_empty_remark.json"))).steps == []

    def test_steps_come_before_the_outcomes_in_the_json(self) -> None:
        assert list(EbdOutcomes.model_fields) == [
            "metadata",
            "steps",
            "multi_step_instructions",
            "has_wildcard_outcome",
            "outcomes",
            "decisions",
        ]


class TestLinear:
    """E_0003 is linear and can be checked by hand"""

    def test_e0003(self) -> None:
        result = explain_outcomes(convert_table_to_graph(table_e0003))
        outcomes = _by_key(result)
        assert list(outcomes) == ["A01", "A02", "Ende"]  # sorted by key
        a01 = outcomes["A01"]
        assert a01.result_code == "A01"
        assert a01.notes == ["Fristüberschreitung"]
        assert not a01.has_subsequent_steps
        assert _steps(a01) == [("1", [False])]
        assert a01.possible_steps == []
        assert a01.route_count == 1
        assert a01.routes == [Route(steps=[RouteStep(step_number="1", answer=False)])]
        assert _steps(outcomes["A02"]) == [("1", [True]), ("2", [False])]
        ende = outcomes["Ende"]
        assert ende.result_code is None
        assert ende.notes == []
        assert _steps(ende) == [("1", [True]), ("2", [True])]

    def test_decisions(self) -> None:
        result = explain_outcomes(convert_table_to_graph(table_e0003))
        assert [
            (d.step_number, d.answer, d.reachable_result_codes, d.can_reach_end_without_result_code)
            for d in result.decisions
        ] == [
            ("1", False, ["A01"], False),
            ("1", True, ["A02"], True),
            ("2", False, ["A02"], False),
            ("2", True, [], True),
        ]


class TestDiamond:
    """two routes (actually three) reach the same code"""

    def test_a05(self) -> None:
        a05 = _by_key(explain_outcomes(convert_table_to_graph(_diamond)))["A05"]
        assert _steps(a05) == [("1", [False, True])]
        assert _steps(a05, certain=False) == [("2", [False, True]), ("3", [True])]
        assert a05.route_count == 3
        assert a05.routes is not None
        assert sorted(tuple((s.step_number, s.answer) for s in r.steps) for r in a05.routes) == [
            (("1", False), ("3", True)),
            (("1", True), ("2", False), ("3", True)),
            (("1", True), ("2", True)),
        ]

    def test_a06(self) -> None:
        a06 = _by_key(explain_outcomes(convert_table_to_graph(_diamond)))["A06"]
        assert _steps(a06) == [("1", [False, True]), ("3", [False])]
        assert _steps(a06, certain=False) == [("2", [False])]
        assert a06.route_count == 2

    @pytest.mark.parametrize(
        "max_routes, has_routes",
        [pytest.param(3, True, id="equal"), pytest.param(2, False, id="below"), pytest.param(0, False, id="zero")],
    )
    def test_max_routes_boundary(self, max_routes: int, has_routes: bool) -> None:
        a05 = _by_key(explain_outcomes(convert_table_to_graph(_diamond), max_routes=max_routes))["A05"]
        assert a05.route_count == 3  # the count does not depend on max_routes
        assert (a05.routes is not None) == has_routes
        assert _steps(a05) == [("1", [False, True])]  # nor do the steps

    def test_forward(self) -> None:
        decisions = explain_outcomes(convert_table_to_graph(_diamond)).decisions
        assert [(d.step_number, d.answer, d.reachable_result_codes) for d in decisions] == [
            ("1", False, ["A05", "A06"]),
            ("1", True, ["A05", "A06"]),
            ("2", False, ["A05", "A06"]),
            ("2", True, ["A05"]),
            ("3", False, ["A06"]),
            ("3", True, ["A05"]),
        ]


class TestTransitionNode:
    """a transition step has no answer"""

    def test_transition_step(self) -> None:
        a02 = _by_key(explain_outcomes(convert_table_to_graph(table_0594_partly)))["A02"]
        assert _steps(a02) == [("270", [False, True]), ("280", [False])]
        assert _steps(a02, certain=False) == [("275", [])]
        assert a02.route_count == 2
        assert a02.routes is not None
        assert [[(s.step_number, s.answer) for s in r.steps] for r in a02.routes] == [
            [("270", False), ("280", False)],
            [("270", True), ("275", None), ("280", False)],
        ]


class TestTransitionalOutcome:
    """outcomes with subsequent steps"""

    def test_hand_made(self) -> None:
        outcomes = _by_key(explain_outcomes(convert_table_to_graph(_transitional)))
        a01 = outcomes["A01"]
        assert a01.has_subsequent_steps
        assert a01.notes == ["weiter"]
        assert _steps(a01) == [("1", [False])]
        assert a01.route_count == 1
        # the transitional node of A01 is not a step on the way to A02
        a02 = outcomes["A02"]
        assert not a02.has_subsequent_steps
        assert _steps(a02) == [("1", [False, True]), ("2", [False])]
        assert a02.route_count == 2
        # Ende has no special rule: the route 1 nein -> A01 (transitional) -> 2 -> Ende counts like any other
        ende = outcomes["Ende"]
        assert _steps(ende) == [("1", [False, True]), ("2", [True])]
        assert _steps(ende, certain=False) == []
        assert ende.route_count == 2
        assert ende.routes == [
            Route(steps=[RouteStep(step_number="1", answer=False), RouteStep(step_number="2", answer=True)]),
            Route(steps=[RouteStep(step_number="1", answer=True), RouteStep(step_number="2", answer=True)]),
        ]

    def test_end_after_transitional_result_code_backward_and_forward_agree(self) -> None:
        result = explain_outcomes(convert_table_to_graph(_transitional))
        ende = _by_key(result)["Ende"]
        assert ende.routes is not None
        # backward: Ende can be reached after answering step 1 with "nein" (which produces the code A01 on the way)
        assert any(route.steps[0] == RouteStep(step_number="1", answer=False) for route in ende.routes)
        # forward: the same answer can reach the end and the code A01
        nein = next(d for d in result.decisions if d.step_number == "1" and not d.answer)
        assert nein.can_reach_end_without_result_code
        assert "A01" in nein.reachable_result_codes

    def test_e0259_loop(self) -> None:
        outcomes = _by_key(explain_outcomes(convert_table_to_graph(_load("e0259.json"))))
        # route counts are decided per outcome: A01 is reached by 10 nein, no matter that there is a loop further down
        a01 = outcomes["A01"]
        assert a01.route_count == 1
        assert a01.routes == [Route(steps=[RouteStep(step_number="10", answer=False)])]
        a12 = outcomes["A12"]
        assert a12.has_subsequent_steps
        assert a12.route_count is None and a12.routes is None  # the loop 300 .. 380 lies on the way to A12
        # A12 can only be reached via step 310; steps 10..130 and 300 were certainly passed
        assert [s.step_number for s in a12.certain_steps] == [
            "10",
            "20",
            "30",
            "40",
            "50",
            "60",
            "70",
            "80",
            "90",
            "100",
            "130",
            "300",
            "310",
        ]
        # answers = answer given the last time the step is passed. 310 nein leads to A12. 310 ja leads to 320 and
        # only back to A12 by passing 310 again (380 ja -> 300 ja -> 310), so it does not count.
        assert a12.certain_steps[-1].answers == [False]
        # A13 follows A12 via 320, so passing the transitional A12 node ends the route to A12, but not to A13
        a13 = outcomes["A13"]
        # 300 nein skips step 310, so 310 is only a possible step on the way to A13 (which is reached via 320)
        assert "300" in {s.step_number for s in a13.certain_steps}
        assert "310" not in {s.step_number for s in a13.certain_steps}
        assert "310" in {s.step_number for s in a13.possible_steps}


class TestDegenerate:
    """empty EBDs and both answers to the same node"""

    def test_empty(self) -> None:
        table = _load("e0452_empty_remark.json")
        result = explain_outcomes(convert_table_to_graph(table))
        assert result.outcomes == []
        assert result.decisions == []
        assert result.metadata.ebd_code == table.metadata.ebd_code

    def test_both_answers_to_same_node(self) -> None:
        result = explain_outcomes(convert_table_to_graph(_same_target))
        ende = _by_key(result)["Ende"]
        assert ende.route_count == 2
        assert _steps(ende) == [("1", [True]), ("2", [False, True])]
        assert [(d.step_number, d.answer) for d in result.decisions] == [
            ("1", False),
            ("1", True),
            ("2", False),
            ("2", True),
        ]


_all_tables: dict[str, EbdGraph] = {
    name: convert_table_to_graph(table)
    for name, table in {
        "e0003": table_e0003,
        "e0015": table_e0015,
        "e0025": table_e0025,
        "e0266": table_e0266,
        "e0401": table_e0401,
        "e0454": table_e0454,
        "e0459": table_e0459,
        "e0462": table_e0462,
        "e0487": table_e0487,
        "diamond": _diamond,
        "transitional": _transitional,
        "same_target": _same_target,
        "e0594_partly": table_0594_partly,
        "e0055": _load("e0055.json"),
        "e0259": _load("e0259.json"),
        "e0594_fv2504": _load("fv2504_ebd40b_e0594.json"),
        "e0610_fv2504": _load("fv2504_ebd40b_e0610.json"),
    }.items()
}


#: examples without any outcome that has a known route count (the loops lie on the way to every outcome)
_no_route_lists = {"e0610_fv2504"}


@pytest.mark.parametrize("name", list(_all_tables))
def test_certain_and_possible_agree_with_routes(name: str) -> None:
    """certain = intersection of all routes, possible = union minus intersection"""
    checked = 0
    for outcome in explain_outcomes(_all_tables[name], max_routes=1000).outcomes:
        if outcome.routes is None:
            continue
        checked += 1
        assert outcome.route_count == len(outcome.routes)
        assert len({tuple((s.step_number, s.answer) for s in route.steps) for route in outcome.routes}) == len(
            outcome.routes
        )
        step_sets = [{s.step_number for s in route.steps} for route in outcome.routes]
        intersection = set.intersection(*step_sets) if step_sets else set()
        union = set.union(*step_sets) if step_sets else set()
        assert {s.step_number for s in outcome.certain_steps} == intersection
        assert {s.step_number for s in outcome.possible_steps} == union - intersection
        for step in outcome.certain_steps + outcome.possible_steps:
            answers_on_routes = {
                r_step.answer
                for route in outcome.routes
                for r_step in route.steps
                if r_step.step_number == step.step_number
            }
            assert set(step.answers) == (answers_on_routes - {None})
        # certain steps are in the order of traversal on every route
        for route in outcome.routes:
            order = [s.step_number for s in route.steps if s.step_number in intersection]
            assert order == [s.step_number for s in outcome.certain_steps]
        numbers = [s.step_number for s in outcome.possible_steps]
        assert numbers == sorted(numbers, key=lambda n: (int(n.rstrip("*")), n.endswith("*")))
    assert checked > 0 or name in _no_route_lists


@pytest.mark.parametrize("name", list(_all_tables))
def test_every_step_used_is_in_the_legend(name: str) -> None:
    graph = _all_tables[name]
    result = explain_outcomes(graph, max_routes=1000)
    numbers = [step.step_number for step in result.steps]
    assert len(numbers) == len(set(numbers))
    expected = {str(node.step_number) for _, node in graph.graph.nodes(data="node") if hasattr(node, "step_number")}
    assert set(numbers) == expected
    assert numbers == sorted(numbers, key=lambda n: (int(n.rstrip("*")), n.endswith("*")))
    used = {d.step_number for d in result.decisions}
    for outcome in result.outcomes:
        used |= {s.step_number for s in outcome.certain_steps + outcome.possible_steps}
        used |= {s.step_number for route in outcome.routes or [] for s in route.steps}
    assert used <= set(numbers)


def _with_pinned_versions(graph: EbdGraph) -> EbdGraph:
    """
    Returns the graph with fixed versions in its release information (if it has any).
    The versions default to the installed package versions, which are not always valid semantic versions (e.g.
    'v0.1.dev1+g...' in a shallow checkout, where the version is derived from git). Defaults are not validated, but the
    JSON round trip validates, so the tests must not depend on the version that happens to be installed.
    """
    release_information = graph.metadata.release_information
    if release_information is None:
        return graph
    pinned = release_information.model_copy(update={"rebdhuhn_version": "v1.2.3", "ebdamame_version": "v1.2.3"})
    return graph.model_copy(update={"metadata": graph.metadata.model_copy(update={"release_information": pinned})})


@pytest.mark.parametrize("name", list(_all_tables))
def test_json_round_trip_and_determinism(name: str) -> None:
    graph = _with_pinned_versions(_all_tables[name])
    result = explain_outcomes(graph)
    assert EbdOutcomes.model_validate_json(result.model_dump_json()) == result
    assert explain_outcomes(graph).model_dump_json() == result.model_dump_json()


def test_json_round_trip_does_not_depend_on_the_installed_version() -> None:
    """a version as in a shallow CI checkout must not break the round trip (reproduces the CI failure)"""
    graph = _all_tables["e0055"]
    release_information = graph.metadata.release_information
    assert release_information is not None
    shallow = release_information.model_copy(update={"rebdhuhn_version": "v0.1.dev1+gabc"})
    graph = graph.model_copy(update={"metadata": graph.metadata.model_copy(update={"release_information": shallow})})
    with pytest.raises(ValidationError):  # this is what the unpinned test did in CI
        EbdOutcomes.model_validate_json(explain_outcomes(graph).model_dump_json())
    result = explain_outcomes(_with_pinned_versions(graph))
    assert EbdOutcomes.model_validate_json(result.model_dump_json()) == result


def test_largest_example_is_fast() -> None:
    """E_0594 has hundreds of thousands of routes for some outcomes; they must not be enumerated"""
    graph = _all_tables["e0594_fv2504"]
    start = time.perf_counter()
    result = explain_outcomes(graph)
    assert time.perf_counter() - start < 3
    assert max(o.route_count or 0 for o in result.outcomes) > 1000
    assert all(o.routes is None for o in result.outcomes if (o.route_count or 0) > 20)


@pytest.mark.snapshot
def test_snapshot(snapshot: SnapshotAssertion) -> None:
    """pins the file format"""
    assert explain_outcomes(_all_tables["e0015"]).model_dump_json(indent=2) == snapshot


#: 1 ja -> 2, 1 nein -> A01; 2 ja -> 3, 2 nein -> A02; 3 ja -> 1 (loop), 3 nein -> Ende
_loop = _table(
    [
        EbdTableRow(step_number="1", description="eins?", sub_rows=[_sub_row(True, "2"), _sub_row(False, None, "A01")]),
        EbdTableRow(step_number="2", description="zwei?", sub_rows=[_sub_row(True, "3"), _sub_row(False, None, "A02")]),
        EbdTableRow(step_number="3", description="drei?", sub_rows=[_sub_row(True, "1"), _sub_row(False, "Ende")]),
    ]
)

#: 1 ja -> 2, 1 nein -> A01; 2 ja -> A02, 2 nein -> 3; 3 ja -> 2 (loop between 2 and 3), 3 nein -> A03
_loop_elsewhere = _table(
    [
        EbdTableRow(step_number="1", description="eins?", sub_rows=[_sub_row(True, "2"), _sub_row(False, None, "A01")]),
        EbdTableRow(step_number="2", description="zwei?", sub_rows=[_sub_row(True, None, "A02"), _sub_row(False, "3")]),
        EbdTableRow(step_number="3", description="drei?", sub_rows=[_sub_row(True, "2"), _sub_row(False, None, "A03")]),
    ]
)


class TestLoops:
    """steps can be passed more than once; answers are the answers given the last time"""

    def test_loop_exact(self) -> None:
        outcomes = _by_key(explain_outcomes(convert_table_to_graph(_loop)))
        assert list(outcomes) == ["A01", "A02", "Ende"]
        a01, a02, ende = outcomes["A01"], outcomes["A02"], outcomes["Ende"]
        assert _steps(a01) == [("1", [False])]
        assert _steps(a01, certain=False) == [("2", [True]), ("3", [True])]
        assert _steps(a02) == [("1", [True]), ("2", [False])]
        assert _steps(a02, certain=False) == [("3", [True])]  # only passed by going round the loop
        assert _steps(ende) == [("1", [True]), ("2", [True]), ("3", [False])]
        assert _steps(ende, certain=False) == []
        for outcome in (a01, a02, ende):  # the loop lies on the way to every outcome
            assert outcome.route_count is None
            assert outcome.routes is None

    def test_loop_elsewhere(self) -> None:
        outcomes = _by_key(explain_outcomes(convert_table_to_graph(_loop_elsewhere)))
        a01 = outcomes["A01"]
        assert a01.route_count == 1
        assert a01.routes == [Route(steps=[RouteStep(step_number="1", answer=False)])]
        a02 = outcomes["A02"]
        assert _steps(a02) == [("1", [True]), ("2", [True])]
        assert _steps(a02, certain=False) == [("3", [True])]
        assert a02.route_count is None and a02.routes is None
        assert outcomes["A03"].route_count is None

    def test_unreachable_outcome(self) -> None:
        graph = convert_table_to_graph(_loop_elsewhere)
        digraph = graph.graph
        # step 9 is not connected to Start (this cannot be created by the conversion, but must not break us)
        nine = DecisionNode(step_number="9", question="neun?")
        a77 = OutcomeNode(result_code="A77", note="nie")
        digraph.add_node("9", node=nine)
        digraph.add_node("A77", node=a77)
        digraph.add_edge("9", "A77", edge=ToYesEdge(source=nine, target=a77))
        digraph.add_edge("9", "A01", edge=ToNoEdge(source=nine, target=OutcomeNode(result_code="A01")))
        for max_routes, routes in ((20, []), (0, None)):
            a77_explained = _by_key(explain_outcomes(graph, max_routes=max_routes))["A77"]
            assert a77_explained.route_count == 0
            assert a77_explained.certain_steps == []
            assert a77_explained.possible_steps == []
            assert a77_explained.routes == routes
        # step 9 cannot be reached, it must not show up anywhere else
        a01 = _by_key(explain_outcomes(graph))["A01"]
        assert a01.route_count == 1
        assert _steps(a01) == [("1", [False])]


#: 1 ja -> 1 (self loop), 1 nein -> A01
_self_loop = _table(
    [EbdTableRow(step_number="1", description="eins?", sub_rows=[_sub_row(True, "1"), _sub_row(False, None, "A01")])]
)

#: inner loop 2 <-> 3, outer loop 1 -> 2 -> 4 -> 1
_nested_loops = _table(
    [
        EbdTableRow(step_number="1", description="eins?", sub_rows=[_sub_row(True, "2"), _sub_row(False, None, "A01")]),
        EbdTableRow(step_number="2", description="zwei?", sub_rows=[_sub_row(True, "3"), _sub_row(False, "4")]),
        EbdTableRow(step_number="3", description="drei?", sub_rows=[_sub_row(True, "2"), _sub_row(False, None, "A02")]),
        EbdTableRow(step_number="4", description="vier?", sub_rows=[_sub_row(True, "1"), _sub_row(False, None, "A03")]),
    ]
)

#: 1 nein -> A01, then step 2 (transitional outcome); 2 ja -> 1: the loop 1 -> A01 -> 2 -> 1 leads through A01
_loop_behind_outcome = _table(
    [
        EbdTableRow(
            step_number="1",
            description="eins?",
            sub_rows=[_sub_row(True, None, "A03"), _sub_row(False, "2", "A01", "weiter")],
        ),
        EbdTableRow(step_number="2", description="zwei?", sub_rows=[_sub_row(True, "1"), _sub_row(False, None, "A02")]),
    ]
)


class TestMoreLoops:
    """self loops, nested loops and loops behind an outcome"""

    def test_self_loop(self) -> None:
        result = explain_outcomes(convert_table_to_graph(_self_loop))
        assert [o.key for o in result.outcomes] == ["A01"]
        a01 = result.outcomes[0]
        assert _steps(a01) == [("1", [False])]  # 1 ja leads to 1 again, not to the outcome
        assert a01.possible_steps == []
        assert a01.route_count is None  # the self loop lies on the way to A01
        assert a01.routes is None
        # forward: both answers keep A01 reachable (ja stays in the loop, from which nein can still be answered)
        assert [
            (d.step_number, d.answer, d.reachable_result_codes, d.can_reach_end_without_result_code)
            for d in result.decisions
        ] == [
            ("1", False, ["A01"], False),
            ("1", True, ["A01"], False),
        ]

    def test_nested_loops(self) -> None:
        outcomes = _by_key(explain_outcomes(convert_table_to_graph(_nested_loops)))
        assert list(outcomes) == ["A01", "A02", "A03"]
        assert _steps(outcomes["A01"]) == [("1", [False])]
        assert _steps(outcomes["A01"], certain=False) == [("2", [False]), ("3", [True]), ("4", [True])]
        assert _steps(outcomes["A02"]) == [("1", [True]), ("2", [True]), ("3", [False])]
        assert _steps(outcomes["A02"], certain=False) == [("4", [True])]
        assert _steps(outcomes["A03"]) == [("1", [True]), ("2", [False]), ("4", [False])]
        assert _steps(outcomes["A03"], certain=False) == [("3", [True])]
        assert all(o.route_count is None and o.routes is None for o in outcomes.values())

    def test_loop_behind_the_outcome(self) -> None:
        outcomes = _by_key(explain_outcomes(convert_table_to_graph(_loop_behind_outcome)))
        # a route to A01 ends at its first A01 node, so the loop that starts there does not matter
        a01 = outcomes["A01"]
        assert a01.route_count == 1
        assert a01.routes == [Route(steps=[RouteStep(step_number="1", answer=False)])]
        assert _steps(a01) == [("1", [False])]
        assert a01.possible_steps == []
        # A03 and A02 can only be reached by going round the loop 1 -> A01 -> 2 -> 1 (A01 is not a step for them)
        a03 = outcomes["A03"]
        assert _steps(a03) == [("1", [True])]
        assert _steps(a03, certain=False) == [("2", [True])]
        assert a03.route_count is None
        a02 = outcomes["A02"]
        assert _steps(a02) == [("1", [False]), ("2", [False])]
        assert a02.route_count is None

    def test_key_with_non_ascii_digits(self) -> None:
        graph = convert_table_to_graph(_diamond)
        graph.graph.add_node("A5²", node=OutcomeNode(result_code=None, note="A5²"))
        keys = [o.key for o in explain_outcomes(graph).outcomes]
        assert keys == ["A05", "A5²", "A06"]  # A5² is natural-sorted like A5 followed by text


def _snapshot_of_graph(graph: EbdGraph) -> tuple[list[Any], list[Any]]:
    return list(graph.graph.nodes(data=True)), list(graph.graph.edges(data=True))


@pytest.mark.parametrize("name", list(_all_tables))
def test_input_graph_is_not_modified(name: str) -> None:
    graph = _all_tables[name]
    before = _snapshot_of_graph(graph)
    explain_outcomes(graph)
    assert _snapshot_of_graph(graph) == before


@pytest.mark.parametrize("name", list(_all_tables))
def test_max_routes_zero_disables_routes_for_every_outcome(name: str) -> None:
    result = explain_outcomes(_all_tables[name], max_routes=0)
    assert result.outcomes
    assert all(outcome.routes is None for outcome in result.outcomes)


class TestNotesAndOrder:
    """notes are deduplicated ignoring whitespace; outcomes are in natural order"""

    def test_wildcard_merge_e0055(self) -> None:
        outcomes = _by_key(explain_outcomes(convert_table_to_graph(_load("e0055.json"))))
        wildcard = outcomes["A**"]
        assert wildcard.result_code == "A**"
        graph = _all_tables["e0055"]
        expected = [
            graph.graph.nodes[key]["node"].note
            for key in graph.graph.nodes
            if getattr(graph.graph.nodes[key]["node"], "result_code", None) == "A**"
        ]
        assert len(wildcard.notes) == len(expected) >= 2
        assert wildcard.notes == expected  # different notes of different nodes, in graph order

    def test_notes_are_deduplicated_ignoring_whitespace(self) -> None:
        graph = convert_table_to_graph(_diamond)
        digraph = graph.graph
        digraph.add_node(
            "A05_x", node=TransitionalOutcomeNode(result_code="A05", subsequent_step_number="3", note="fuenf")
        )
        digraph.add_node(
            "A05_y", node=TransitionalOutcomeNode(result_code="A05", subsequent_step_number="3", note="fuenf.")
        )
        digraph.add_node(
            "A05_z", node=TransitionalOutcomeNode(result_code="A05", subsequent_step_number="3", note="f\nuenf")
        )
        digraph.add_node(
            "A05_w", node=TransitionalOutcomeNode(result_code="A05", subsequent_step_number="3", note="anders")
        )
        assert _by_key(explain_outcomes(graph))["A05"].notes == ["fuenf", "anders"]

    def test_natural_order(self) -> None:
        codes = ["A100", "A99", "A01", "A**", "A10", "A2"]
        rows = [
            EbdTableRow(
                step_number=str(i + 1),
                description=f"{i}?",
                sub_rows=[
                    _sub_row(False, None, code, f"note {code}"),
                    _sub_row(True, str(i + 2) if i + 1 < len(codes) else "Ende"),
                ],
            )
            for i, code in enumerate(codes)
        ]
        result = explain_outcomes(convert_table_to_graph(_table(rows)))
        assert [o.key for o in result.outcomes] == ["A01", "A2", "A10", "A99", "A100", "A**", "Ende"]


_snapshot_table = _table(
    [
        EbdTableRow(step_number="1", description="eins?", sub_rows=[_sub_row(True, "2"), _sub_row(False, "3")]),
        EbdTableRow(
            step_number="2", description="zwei?", sub_rows=[_sub_row(True, None, "A**", "x"), _sub_row(False, "3")]
        ),
        EbdTableRow(
            step_number="3",
            description="drei (Uebergang)",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=None, subsequent_step_number="4"),
                    result_code=None,
                    note="Die Trefferliste fuer Schritt 4 wird gefuellt",
                )
            ],
        ),
        EbdTableRow(
            step_number="4", description="vier?", sub_rows=[_sub_row(True, "5", "A05", "fuenf"), _sub_row(False, "5")]
        ),
        EbdTableRow(
            step_number="5", description="fuenf?", sub_rows=[_sub_row(True, None, "A**", "y"), _sub_row(False, "Ende")]
        ),
    ]
)


@pytest.mark.snapshot
def test_snapshot_loops_transitions_and_notes(snapshot: SnapshotAssertion) -> None:
    """pins the parts of the format that the other snapshot does not cover: possible steps, a transition step,
    both answers, a transitional outcome and several notes"""
    result = explain_outcomes(convert_table_to_graph(_snapshot_table))
    wildcard = _by_key(result)["A**"]
    assert wildcard.notes == ["x", "y"]
    assert _by_key(result)["A05"].has_subsequent_steps
    assert any(step.answers == [] for step in wildcard.possible_steps)
    assert [step.note for step in result.steps] == [
        None,
        None,
        "Die Trefferliste fuer Schritt 4 wird gefuellt",
        None,
        None,
    ]
    assert result.has_wildcard_outcome
    assert any(step.answers == [False, True] for step in wildcard.certain_steps)
    assert result.model_dump_json(indent=2) == snapshot


def _anonymous_json_problems(schema: dict[str, Any]) -> list[str]:
    """
    Returns the violations of the rule: every JSON object in the output is an instance of a named model (no dict,
    no Any), lists contain only named models or scalars (no nested lists, no tuples).
    """
    problems: list[str] = []

    def check_value(value: dict[str, Any], path: str, in_array: bool) -> None:
        """checks the schema of a field (or of the items of an array field)"""
        if "$ref" in value:
            return  # a named model (or enum)
        variants = [v for key in ("anyOf", "oneOf", "allOf") for v in value.get(key, [])]
        if variants:
            for variant in variants:
                check_value(variant, path, in_array)
            return
        value_type = value.get("type")
        if "prefixItems" in value:
            problems.append(f"{path}: tuple")
        elif value_type == "array":
            if in_array:
                problems.append(f"{path}: nested list")
            elif not isinstance(value.get("items"), dict):
                problems.append(f"{path}: list without item type")
            else:
                check_value(value["items"], f"{path}[]", True)
        elif value_type == "object":
            problems.append(f"{path}: anonymous object (dict or inline model)")
        elif value_type not in ("string", "integer", "number", "boolean", "null"):
            problems.append(f"{path}: untyped (Any)")

    models = {"#": schema, **{f"#/$defs/{name}": definition for name, definition in schema.get("$defs", {}).items()}}
    for model_path, model in models.items():
        if model["type"] != "object":
            if model["type"] != "string":
                problems.append(f"{model_path}: neither a model nor an enum")
            continue
        if model.get("additionalProperties") is not False:
            problems.append(f"{model_path}: open object")
        for field_name, field in model["properties"].items():
            check_value(field, f"{model_path}.{field_name}", False)
    return problems


@pytest.mark.parametrize("mode", ["validation", "serialization"])
def test_json_schema_has_no_anonymous_json(mode: Literal["validation", "serialization"]) -> None:
    """the output consists of named models only; the top level is the EbdOutcomes object, not a bare array"""
    schema = EbdOutcomes.model_json_schema(mode=mode)
    assert schema["type"] == "object"
    assert schema["title"] == "EbdOutcomes"
    assert _anonymous_json_problems(schema) == []


def test_json_schema_guard_detects_anonymous_json() -> None:
    """the guard must not be vacuous"""

    class Anonymous(BaseModel):
        """a model that violates every rule"""

        nested: list[list[int]]
        mapping: dict[str, int]
        anything: Any
        pair: tuple[int, str]

    problems = _anonymous_json_problems(Anonymous.model_json_schema())
    assert any("nested list" in p for p in problems)
    assert any("anonymous object" in p for p in problems)
    assert any("untyped" in p for p in problems)
    assert any("tuple" in p for p in problems)
    assert any("open object" in p for p in problems)
