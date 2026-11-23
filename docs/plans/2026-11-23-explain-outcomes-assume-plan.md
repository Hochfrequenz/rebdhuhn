# explain_outcomes with assumed answers — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `explain_outcomes(graph, assume={"17": False})` answers "if I always answer 'nein' at step 17, which steps
and result codes are still reachable?"

**Architecture:** The existing analysis in `src/rebdhuhn/outcomes.py` runs on an answer multigraph
(`_get_answer_graph`, edge key = answer). Assumptions remove the excluded answer edges from that multigraph before
anything else is computed; the per-outcome and forward analyses then work on the cut graph unchanged. Two new fields
on `EbdOutcomes` record the assumptions and the unreachable steps.

**Tech Stack:** Python ≥3.10, pydantic v2, networkx, pytest, syrupy. Tooling via `uv`.

**Spec:** `docs/plans/2026-11-23-explain-outcomes-assume-design.md` (read it first; it is short). Background:
`docs/plans/2026-11-18-outcome-lookup-design.md`.

## Global Constraints

- Models: pydantic v2, `model_config = ConfigDict(frozen=True, extra="forbid")`, every field with a docstring below
  it (style of `src/rebdhuhn/models/ebd_outcomes.py`). No `dict`, no `Any`, no tuples, no nested lists in models.
- Export new public names from both `rebdhuhn.models` and `rebdhuhn`, keeping the grouped `__all__` style.
- Graph algorithms via networkx built-ins; no hand-written traversals.
- Output stays deterministic (sorted lists; step numbers sorted with `_step_sort_key`).
- Must pass: `uv run pytest`, `uv run --group linting ruff check src/rebdhuhn`, `uv run --group linting ruff format
  --check .`, `uv run --group linting ruff check --select I .`,
  `uv run --group type_check mypy --show-error-codes --strict src/rebdhuhn` and the same for `unittests`.
- This machine has 8 GB RAM: run the test suite once at a time, never two heavy jobs in parallel. Tests that need a
  kroki docker container may be skipped/fail locally for lack of docker; only `unittests/test_outcomes.py` must be
  fully green, plus the whole suite must not regress compared to `main`.
- Commit messages: conventional commits (`feat: ...`, `test: ...`, `docs: ...`), ending with
  `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

## Review Focus

1. A decision whose both answers lead to the same node (`_same_target` in the tests): assuming either answer must
   keep that node reachable. Test in Task 2.
2. An assumed step that becomes unreachable through another assumption (e.g. assume 1=ja and 3=nein in `_diamond`
   where 3 is still reachable via 2; and a case where it is not): no crash, step listed in `unreachable_steps`,
   assumption still listed in `assumed_answers`. Test in Task 2.
3. An assumption on a step inside a loop (`e0259`): result consistent with the invariants of the property test.
   Covered by the property test in Task 2.
4. Step numbers with a star (`"6*"`) as keys of `assume`: sorted correctly in `assumed_answers`. Covered by the
   property test over the example tables (which contain starred steps, e.g. `e0594_fv2504`).
5. The caller's `assume` mapping and the input graph must not be modified (existing `test_input_graph_is_not_modified`
   extended in Task 2).

---

### Task 1: new model fields and `unreachable_steps`

**Files:**
- Modify: `src/rebdhuhn/models/ebd_outcomes.py` (new class `AssumedAnswer`, two new fields on `EbdOutcomes`)
- Modify: `src/rebdhuhn/models/__init__.py`, `src/rebdhuhn/__init__.py` (export `AssumedAnswer`)
- Modify: `src/rebdhuhn/outcomes.py` (`explain_outcomes` fills `unreachable_steps`)
- Test: `unittests/test_outcomes.py`, snapshot `unittests/__snapshots__/test_outcomes.ambr`

**Interfaces:**
- Produces:
  - `class AssumedAnswer(BaseModel)`: `step_number: str` (number of the decision step), `answer: bool`
    (`True` = "ja", `False` = "nein").
  - `EbdOutcomes.assumed_answers: list[AssumedAnswer] = []` — place it directly after `has_wildcard_outcome`.
    Docstring: the answers assumed when computing this result (see `explain_outcomes(assume=...)`), sorted by step
    number; empty if nothing was assumed.
  - `EbdOutcomes.unreachable_steps: list[str] = []` — place it directly after `assumed_answers`. Docstring: numbers
    of the decision and transition steps that cannot be reached from the start (under the assumed answers), sorted
    by step number; such steps cannot influence any outcome.
  - In `outcomes.py`: `_unreachable_steps(graph: nx.DiGraph, answer_graph: nx.MultiDiGraph) -> list[str]` using
    `nx.descendants(answer_graph, _START_KEY)`; returns the step numbers of `DecisionNode`/`TransitionNode` nodes not
    reachable, sorted by `_step_sort_key`.

- [ ] **Step 1: Write failing tests** in `unittests/test_outcomes.py` (new class `TestUnreachableSteps`):

```python
def test_no_unreachable_steps_and_no_assumptions_by_default(self) -> None:
    result = explain_outcomes(convert_table_to_graph(_diamond))
    assert result.unreachable_steps == []
    assert result.assumed_answers == []

def test_unreachable_step_is_reported(self) -> None:
    # reuse the table of TestSteps.test_unreachable_step_is_in_the_legend_and_steps_are_sorted (step "10" unreachable);
    # move that table to a module level constant if needed
    assert explain_outcomes(graph).unreachable_steps == ["10"]

def test_old_json_without_the_new_fields_still_validates(self) -> None:
    data = json.loads(explain_outcomes(convert_table_to_graph(_diamond)).model_dump_json())
    del data["assumed_answers"]
    del data["unreachable_steps"]
    assert EbdOutcomes.model_validate(data).unreachable_steps == []
```

Check first which steps of that existing table are really unreachable and use the actual value.

- [ ] **Step 2: Run** `uv run pytest unittests/test_outcomes.py -k TestUnreachableSteps -v` — expected: FAIL
  (`AttributeError`/`ValidationError` about unknown fields).
- [ ] **Step 3: Implement** the model changes, the exports and `_unreachable_steps`; call it in `explain_outcomes`
  (empty EBD: `unreachable_steps=[]`).
- [ ] **Step 4: Run** `uv run pytest unittests/test_outcomes.py -v` — expected: only `test_snapshot` fails, with the
  two new keys as the only diff. Update with `uv run pytest unittests/test_outcomes.py --snapshot-update`, check with
  `git diff unittests/__snapshots__` that only the two keys were added, rerun: all PASS.
- [ ] **Step 5: Commit** `feat: report unreachable steps in explain_outcomes`

### Task 2: the `assume` parameter

**Files:**
- Modify: `src/rebdhuhn/outcomes.py`
- Modify: `README.md` (section of `explain_outcomes`, after the existing code example)
- Test: `unittests/test_outcomes.py`

**Interfaces:**
- Consumes: `AssumedAnswer`, `EbdOutcomes.assumed_answers`, `EbdOutcomes.unreachable_steps`, `_unreachable_steps`
  from Task 1.
- Produces: `explain_outcomes(graph: EbdGraph, max_routes: int = 20, assume: Mapping[str, bool] | None = None)
  -> EbdOutcomes` (`Mapping` from `collections.abc`). Extend its docstring with one paragraph on `assume`.
- Internal: `_apply_assumptions(graph: nx.DiGraph, answer_graph: nx.MultiDiGraph, assume: Mapping[str, bool]) ->
  list[AssumedAnswer]` — validates, removes from `answer_graph` (in place; it is a fresh copy) every out edge of the
  step whose key is the excluded answer (`not answer`), returns the sorted `AssumedAnswer`s. Validation, in this
  order per step: key not in the graph → `ValueError(f"Step {step!r} does not exist in {ebd_code}")`; node is not a
  `DecisionNode` → `ValueError(f"Step {step!r} is no decision step (only decision steps have answers)")`. Exact
  wording is free, but the message must contain the step number.
- Call order in `explain_outcomes`: empty-EBD check (raise for non-empty `assume`: unknown step) →
  `_get_answer_graph` → `_apply_assumptions` → everything else as today on the cut answer graph.
- `_explain_decisions` currently uses `nx.descendants(graph, key)` on the original DiGraph. Change it to use the
  answer graph so the forward direction respects the assumptions (entries for removed edges disappear automatically
  because it iterates `answer_graph.edges`). Results without assumptions must stay identical (the snapshot and all
  existing tests prove it).

- [ ] **Step 1: Write failing tests** (new class `TestAssume`), using the module level tables:

```python
def test_diamond_step_1_nein(self) -> None:
    result = explain_outcomes(convert_table_to_graph(_diamond), assume={"1": False})
    assert result.assumed_answers == [AssumedAnswer(step_number="1", answer=False)]
    assert result.unreachable_steps == ["2"]
    a05 = _by_key(result)["A05"]
    assert [(s.step_number, s.answers) for s in a05.certain_steps] == [("1", [False]), ("3", [True])]
    assert a05.possible_steps == []
    assert a05.route_count == 1
    assert ("1", True) not in {(d.step_number, d.answer) for d in result.decisions}
    assert ("1", False) in {(d.step_number, d.answer) for d in result.decisions}

def test_diamond_two_assumptions_make_an_outcome_unreachable(self) -> None:
    result = explain_outcomes(convert_table_to_graph(_diamond), assume={"1": False, "3": True})
    a06 = _by_key(result)["A06"]
    assert a06.route_count == 0 and a06.certain_steps == [] and a06.possible_steps == []

def test_assumed_step_that_becomes_unreachable(self) -> None:
    result = explain_outcomes(convert_table_to_graph(_diamond), assume={"1": False, "2": True})
    assert result.unreachable_steps == ["2"]
    assert [a.step_number for a in result.assumed_answers] == ["1", "2"]

@pytest.mark.parametrize("answer", [True, False])
def test_both_answers_to_the_same_node(self, answer: bool) -> None:
    result = explain_outcomes(convert_table_to_graph(_same_target), assume={"2": answer})
    assert _by_key(result)["Ende"].route_count == 1
    assert [(s.step_number, s.answers) for s in _by_key(result)["Ende"].certain_steps] == [("1", [True]), ("2", [answer])]

def test_unknown_step(self) -> None:
    with pytest.raises(ValueError, match="'42'"):
        explain_outcomes(convert_table_to_graph(_diamond), assume={"42": True})

def test_transition_step(self) -> None:
    # pick the step number of a TransitionNode in table_0594_partly
    with pytest.raises(ValueError, match=...):
        explain_outcomes(convert_table_to_graph(table_0594_partly), assume={<transition step>: True})

def test_empty_ebd(self) -> None:
    with pytest.raises(ValueError):
        explain_outcomes(convert_table_to_graph(_load("e0452_empty_remark.json")), assume={"1": True})

def test_no_assumption_equals_empty_assumption(self) -> None:
    graph = convert_table_to_graph(_diamond)
    assert explain_outcomes(graph, assume={}) == explain_outcomes(graph) == explain_outcomes(graph, assume=None)

def test_json_round_trip_with_assumptions(self) -> None:
    result = explain_outcomes(convert_table_to_graph(_diamond), assume={"1": False})
    assert EbdOutcomes.model_validate_json(result.model_dump_json()) == result
```

Verify the exact expectations by hand against the diagram comments of `_diamond` (1 ja → 2, 1 nein → 3;
2 ja → A05, 2 nein → 3; 3 ja → A05, 3 nein → A06) and `_same_target` before relying on them; fix the test, not the
code, if an expectation above is wrong, and say so in the report.

Property test (module level, parametrized over `_all_tables`, `max_routes=1000` only where routes are compared,
otherwise `max_routes=0`; the whole test must stay well under ~10 s — measure with `--durations=5`):

```python
@pytest.mark.parametrize("name", list(_all_tables))
def test_assumptions_are_respected(name: str) -> None:
    graph = _all_tables[name]
    base = explain_outcomes(graph, max_routes=0)
    reachable_base = {o.key for o in base.outcomes if o.route_count != 0}
    for step in [s.step_number for s in base.steps if <is a decision step>]:
        for answer in (False, True):
            result = explain_outcomes(graph, max_routes=20, assume={step: answer})
            # no step used anywhere is unreachable
            # PassedStep of `step`: answers ⊆ [answer]; RouteStep of `step`: answer == answer
            # no decision entry (step, not answer)
            # {o.key for o in result.outcomes if o.route_count != 0} ⊆ reachable_base
            # set(base.unreachable_steps) ⊆ set(result.unreachable_steps)
```

Decision steps: those with an entry in `base.decisions`. If the test is too slow on the largest tables, limit the
steps per table (e.g. the first 15 decision steps) and note it in a comment.

Extend `test_input_graph_is_not_modified` so it also calls `explain_outcomes(graph, assume={<first decision step>:
True})` and checks that the passed mapping is unchanged.

- [ ] **Step 2: Run** `uv run pytest unittests/test_outcomes.py -k "TestAssume or assumptions" -v` — expected: FAIL
  (`TypeError: unexpected keyword argument 'assume'`).
- [ ] **Step 3: Implement** `assume` as described in Interfaces.
- [ ] **Step 4: Run** `uv run pytest unittests/test_outcomes.py -v --durations=5` — expected: all PASS, snapshot
  unchanged, property test well under ~10 s.
- [ ] **Step 5: README**: below the existing `explain_outcomes` example, add a short paragraph and example:

```python
# "If I always answer 'nein' at step 17, does step 39 still matter?"
assumed = explain_outcomes(graph, assume={"17": False})
print("39" in assumed.unreachable_steps)
print([outcome.key for outcome in assumed.outcomes if outcome.route_count != 0])  # codes still reachable
```

  One sentence each: an assumption holds on every pass of a loop; answers excluded by an assumption are missing
  from `decisions`; unknown steps and transition steps raise `ValueError`.
- [ ] **Step 6: Run all gates** from Global Constraints — expected: all green (except docker-dependent tests that
  fail on `main` too).
- [ ] **Step 7: Commit** `feat: explain_outcomes(assume=...) for what-if analysis`
