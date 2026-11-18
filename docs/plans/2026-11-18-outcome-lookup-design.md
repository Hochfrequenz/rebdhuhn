# Outcome lookup: what does a result code imply? (design)

Date: 2026-11-18. Related: issue #516 (part 2, graph-based analysis).

## Why

Someone who receives a result code (e.g. `A05`, or `A99` with a free text) knows from the AHB which EBD to consult,
but then has to trace the diagram by hand to learn which checks were passed on the way to that code.
The goal is to make `machine-readable_entscheidungsbaumdiagramme` the best EBD source online. For that the toolchain
shall publish one additional static file per EBD (`<EBD>.outcomes.json`) next to `.json`/`.dot`/`.svg`.
Consumers are (a) the static frontend (no backend) and (b) AI agents that read raw files.
This repo provides the computation and the pydantic model; writing the file happens in the toolchain (not here).

## Goals

- Backward: for every outcome of an EBD, which steps were passed on the way, with which answer.
- Forward: for every decision step and each answer, which result codes are still reachable.
- Self-contained output: full question texts and notes, so a consumer needs no second file.
- Works on every EBD, including the huge ones (`E_0594`/`A13` has 466,946 routes in FV2610; the largest graph has
  345 nodes). Must never enumerate routes before knowing there are few.

## Non-goals

- No code → EBD index across EBDs, no full text search, no diff between format versions (separate work).
- No file writing, no CLI, no change to existing models or conversions.

## Approaches considered

- A: backward summary per result code only.
- B: list of routes only. Rejected: explodes on big EBDs; a cap would silently drop information.
- **C (chosen): A plus the forward direction in the same model.** The forward part costs little and is what a later
  format-version diff needs to say which result codes a changed step affects.

## Public API

New module `src/rebdhuhn/outcomes.py`, new models in `src/rebdhuhn/models/ebd_outcomes.py`,
both exported from `rebdhuhn` and `rebdhuhn.models` (keep the grouped `__all__` style).

```python
def explain_outcomes(graph: EbdGraph, max_routes: int = 20) -> EbdOutcomes: ...
```

Models (pydantic v2, `extra="forbid"`, frozen, every field with a docstring like the existing models):

```python
class PassedStep:               # one step on the way to an outcome
    step_number: str
    question: str               # DecisionNode.question / TransitionNode.question
    answers: list[bool]         # [] = transition step (no decision); [True] = "ja"; [False] = "nein";
                                # [False, True] = either answer can lead to this outcome

class RouteStep:                # one step of one concrete route
    step_number: str
    answer: bool | None         # None for transition steps

class Route:                    # one concrete route from Start to an outcome
    steps: list[RouteStep]      # in order of traversal

class OutcomeExplanation:
    key: str                    # result code if there is one; "Ende" for the EndNode; otherwise the node key (note)
    result_code: str | None
    notes: list[str]            # distinct notes of all nodes that carry this outcome, in graph order
    has_subsequent_steps: bool  # True if at least one occurrence is a TransitionalOutcomeNode
    certain_steps: list[PassedStep]   # on EVERY route from Start to this outcome, in order of traversal
    possible_steps: list[PassedStep]  # on at least one route but not on every; sorted by step number
    route_count: int | None     # number of distinct routes Start -> outcome; None if the graph has a cycle
    routes: list[Route] | None  # all routes if route_count <= max_routes, else None

class DecisionConsequence:      # forward direction, one entry per decision step and answer
    step_number: str
    question: str
    answer: bool
    reachable_result_codes: list[str]     # sorted, distinct
    can_reach_end_without_result_code: bool  # an EndNode or an outcome without own result code is reachable

class EbdOutcomes:
    metadata: EbdGraphMetaData
    outcomes: list[OutcomeExplanation]    # sorted by key
    decisions: list[DecisionConsequence]  # sorted by step number (numeric part, then suffix), "nein" before "ja"
```

No bare/anonymous JSON: every JSON object in the output is an instance of a named pydantic model. No `dict`,
no `Any`, no nested lists (`list[list[...]]`), no tuples; lists only ever contain a named model or a plain scalar.
The top level of a file is the `EbdOutcomes` object, never a bare array.

## Semantics

- An *outcome* groups all `OutcomeNode`s and `TransitionalOutcomeNode`s with the same `result_code`
  (the wildcard code with different notes is therefore one outcome with several notes). Outcome nodes without
  result code are one outcome each (key = node key). The `EndNode` is an outcome with key `"Ende"`: it answers
  "what must be true to pass without a result code".
- A step is *certain* if it lies on every route from `Start` to any node of the outcome. Compute with dominators
  (`networkx.immediate_dominators`) on the graph plus a virtual sink that all nodes of the outcome point to; do not
  derive it from enumerated routes. This also works for cyclic graphs.
- A step is *possible* if it is reachable from `Start` and can reach a node of the outcome, and is not certain.
- `answers` of a step for an outcome: the answers whose edge target is a node of the outcome or can reach one.
- `route_count`: dynamic programming over the DAG (topological order), not enumeration. If the graph is not a DAG:
  `route_count = None`, `routes = None`; everything else is still filled.
- `routes` are enumerated only if `route_count <= max_routes`. `max_routes=0` disables route lists.
- Only `DecisionNode` and `TransitionNode` appear as steps. `Start`, outcome nodes and the virtual sink never do.
  A `TransitionalOutcomeNode` lying on the way to a *different* outcome is not a step either (documented limitation).
- Empty EBDs (single `EmptyNode`): `outcomes == []`, `decisions == []`.
- The output must be deterministic (stable ordering), since the files are committed and diffed.

### Amendments after the first review (2026-11-18); these override the bullets above where they differ

- Loops are real in EBDs (iterations over a Trefferliste): a step can be passed more than once. On such graphs
  `possible_steps` deliberately includes steps that are only passed by going round a loop, and `answers` means
  *the answer given the last time the step was passed*: answer `a` of step `k` counts only if the target of that
  edge reaches the outcome without passing `k` again. On loop-free graphs this is identical to the old definition.
- `route_count`/`routes` are decided per outcome, not per EBD: they are `None` only if the nodes that lie between
  `Start` and this outcome contain a cycle ("routes to this outcome can loop"). Otherwise count as usual.
- (Superseded by the second amendments.) `Ende` means "finished without any result code": routes that pass a `TransitionalOutcomeNode` do not count for
  `Ende` (they did produce a code). This applies to the `Ende` outcome only. `route_count == 0` is a valid answer.
- An outcome that cannot be reached from `Start` always gets `route_count = 0`, empty step lists and
  `routes = []` (or `None` if `max_routes == 0`), also on graphs with loops.
- `max_routes == 0`: `routes` is `None` for every outcome, without exception.
- `notes` are deduplicated ignoring whitespace differences (reuse the helpers in `graph_conversion.py`).
- `outcomes` are in natural order of `key` (`A01 < A99 < A100`), not plain string order; still deterministic.
- The inference "a decision with one successor means both answers lead there" rests on the conversion rule that
  every decision sub-row becomes an edge; say so in a code comment.

### Amendments after the second review (2026-11-18); these override everything above where they differ

- `Ende` has no special rule any more. In the real data (FV2610) the `EndNode` exists in 59 of 361 EBDs and is
  only ever entered directly from a decision step (a table sub-row "Ende" without code and note); a sub-row "Ende"
  with a code or note becomes an ordinary outcome node instead. The `Ende` outcome therefore means "the check ran
  to a bare Ende"; routes that passed a `TransitionalOutcomeNode` earlier count like any other route. This makes
  backward and forward direction agree.
- Forward field renamed: `can_end_without_result_code` -> `can_reach_end_without_result_code`, documented as
  "an EndNode or an outcome node that itself carries no result code is reachable (result codes with subsequent
  steps may have been produced on the way)".
- Graph algorithms use networkx built-ins only; no hand-written traversals. Route listing via
  `networkx.all_simple_edge_paths` (or `all_simple_paths`) on the cut graph; the last-pass check via networkx
  reachability on the graph without the step (e.g. one `networkx.ancestors(graph_without_k, sink)` per step that
  needs it, not one search per answer). The route count may stay a short loop over `networkx.topological_sort`
  (networkx has no path counting). Runtime over a whole format version may grow to ~15 s; more is not acceptable.

## Tests

- Hand-checkable cases with exact expectations: `E_0003` (linear), a diamond where two routes reach the same code
  (certain vs. possible, `answers == [False, True]`), a table with a transition node, `e0259.json` (transitional
  outcomes), an empty EBD, `max_routes` boundary (equal, above, 0).
- Property test over the existing example tables: for each outcome with `routes` not `None`, `certain_steps` equals
  the intersection of the routes, `possible_steps` equals union minus intersection, and `len(routes) == route_count`.
- A test that the largest example available in `unittests` (E_0594 if its table exists, otherwise the biggest one)
  finishes fast (well under a few seconds).
- JSON round trip: `EbdOutcomes.model_validate_json(x.model_dump_json()) == x`.
- One syrupy snapshot of the JSON for a medium EBD to pin the file format.

## Left to the builder

Internal helper structure, exact docstrings, README section (short usage example).

### Amendment before release: question texts only once per file (2026-11-18)

Measured on FV2610 (242 EBDs with a table, JSON with `indent=2`): the outcomes files add up to 19.75 MB, while the
whole format version directory (svg, dot, json, puml) is 13.3 MB today. About half of that is the question text
repeated in every `PassedStep` and `DecisionConsequence`. Without the repetition it is 10.6 MB.
(`E_0406`/`E_0407` alone are about 3 MB each afterwards: 129 outcomes, 424 decision entries, one big loop.)

- New model `StepDescription` (`step_number: str`, `question: str`) and new field
  `EbdOutcomes.steps: list[StepDescription]`: every `DecisionNode` and `TransitionNode` of the graph exactly once,
  sorted by step number like `decisions`. It is the legend of the file; the file stays self-contained.
- `question` is removed from `PassedStep` and from `DecisionConsequence`; both refer to `steps` via `step_number`.
- Every `step_number` used anywhere in the file must exist in `steps` (test this over all example tables).
