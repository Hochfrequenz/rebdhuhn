# explain_outcomes with assumed answers (design)

Date: 2026-11-23. Closes issue #516 together with an issue comment. Builds on
`2026-11-18-outcome-lookup-design.md` (#644).

## Why

Issue #516 asks for three things: (1) condition `[123]` → EBD reverse lookup, (2) graph-based impact analysis, (3) full
text search over EBDs. The user wants the reporter's points answered properly and within rebdhuhn's scope.

rebdhuhn's scope is one EBD at a time: models, table → graph conversion, rendering and analysis of that graph.
Anything across many EBDs or format versions belongs to the planned EBD MCP server
(Hochfrequenz/entscheidungsbaumdiagramme#757, Python, built on rebdhuhn models). mcp-bdew-mako, the consumer the
issue was written for, dropped its EBD tools on 2026-10-09 (#282).

- (1) No EBD table from FV2304 to FV2610 contains an AHB condition reference like `[123]` (checked against the
  published JSON files). The lookup belongs to the AHB side / #757. Answered in an issue comment, no code.
- (3) Search needs all EBDs of a format version at once: #757. Answered in an issue comment, no code.
- (2) Mostly covered by `explain_outcomes` (#644). Missing: "if I always answer 'nein' at step 17, does the change at
  step 39 affect me at all?" That is built here.

## Approaches

- **Chosen: an optional `assume` parameter on `explain_outcomes`.** The graph is cut down to the assumed answers and
  the whole existing analysis runs on the rest. One function, no new semantics to learn.
- New separate function returning only reachable steps/codes: rejected, it duplicates the reachability code and gives
  less (no certain/possible steps, no routes under the assumption).
- Search and condition lookup in rebdhuhn: rejected, out of scope (see above).

## API

```python
def explain_outcomes(
    graph: EbdGraph, max_routes: int = 20, assume: Mapping[str, bool] | None = None
) -> EbdOutcomes: ...
```

`assume` maps a decision step number (e.g. `"17"`, `"6*"`) to the answer that is always given there
(`True` = "ja", `False` = "nein"). Keyword use is expected; the positional order of existing params stays.

New model in `models/ebd_outcomes.py` (frozen, `extra="forbid"`, docstrings like the others; exported from
`rebdhuhn.models` and `rebdhuhn`):

```python
class AssumedAnswer:
    step_number: str
    answer: bool
```

New fields on `EbdOutcomes`:

- `assumed_answers: list[AssumedAnswer]`: the assumptions the file was computed under, sorted by step number;
  `[]` without assumptions.
- `unreachable_steps: list[str]`: numbers of decision and transition steps that cannot be reached from the start
  (under the assumptions), sorted by step number. This answers "does step 39 still matter?" directly. Computed always
  (also without assumptions; normally `[]`).

Both fields have defaults (`[]`) so existing JSON still validates. They are serialized, so the snapshot and the
toolchain's `.outcomes.json` files gain two short keys.

## Semantics

- Assuming answer `a` for step `k` removes every edge of `k` in the answer graph whose answer is `not a`. If both
  answers of `k` lead to the same node, the edge for `a` remains. This holds on every pass of a loop too ("always").
- Everything else (outcomes, certain/possible steps, answers, route counts, routes) is computed on the cut answer
  graph exactly as today. Outcomes that become unreachable stay in the list with `route_count = 0`, empty steps and
  `routes = []` (existing rule). `PassedStep.answers` for an assumed step can then only contain the assumed answer.
- `decisions`: entries for the excluded answers are dropped; all others are computed on the cut graph (forward
  reachability after the remaining answer).
- `steps` (the legend) is unchanged: every step of the EBD, also unreachable ones.
- Errors (`ValueError`, message names the step): a step number that is not in the graph, a step that is a transition
  step (no yes/no question). An empty EBD with a non-empty `assume` is an unknown step.
- `assume=None` and `assume={}` give exactly today's result plus the two new fields at their defaults
  (`unreachable_steps` computed).

## Tests

- Diamond table: assume step 1 = nein, check outcomes reachable/unreachable, `unreachable_steps`, `decisions`
  without the ja-entry of step 1, `assumed_answers`.
- A decision whose both answers lead to the same node: assuming either answer keeps the node reachable.
- A loop EBD from the examples: assumption on a step inside the loop does not crash and stays consistent (property
  test below).
- Property test over all example tables, assuming each answer of each decision step one at a time (keep the whole
  test well under ~10 s, e.g. `max_routes=0` where routes are not needed):
  - no `step_number` of any `PassedStep`/`RouteStep` is in `unreachable_steps`;
  - for the assumed step `k` with answer `a`: every `PassedStep` of `k` has `answers` ⊆ `[a]`, every `RouteStep` of
    `k` has `answer == a`, and `decisions` has no entry `(k, not a)`;
  - outcomes with `route_count != 0` under the assumption are a subset of those without it;
  - `unreachable_steps` without assumption ⊆ `unreachable_steps` with it.
- Errors: unknown step, transition step, empty EBD.
- `assume=None` result equals the old result (existing snapshot, updated only by the two new keys).
- JSON round trip with assumptions.

## Left to the builder

Helper structure, docstrings, the README example (extend the existing explain_outcomes section with one `assume`
example). Issue comment and PR text are written by the orchestrating session, not the builder.
