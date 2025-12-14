# EBD Cross-Reference Links Design

## Overview

Detect EBD cross-references (e.g., "EBD E_0621") in outcome node notes and render them as clickable links in SVG output.

Related issue: https://github.com/Hochfrequenz/rebdhuhn/issues/105

## Data Flow

```
EbdTableSubRow (parsing)     →  OutcomeNode (graph)      →  DOT/SVG (rendering)
├─ note: "EBD E_0621..."     │  ├─ note: "EBD E_0621..."  │  ├─ <a href="?ebd=E_0621">
├─ ebd_references: ["E_0621"]│  ├─ ebd_references: [...]  │  │   EBD E_0621</a>...
```

**Regex pattern**: `EBD (E_\d{4})` - captures the EBD code from patterns like "EBD E_0621_Prüfen..."

**Link format**: Configurable URL template, e.g., `?ebd={ebd_code}` where `{ebd_code}` gets replaced with the detected code.

## Model Changes

### EbdTableSubRow (src/rebdhuhn/models/ebd_table.py)

```python
class EbdTableSubRow(BaseModel):
    # ... existing fields ...

    ebd_references: list[str] = Field(default_factory=list)
    """EBD codes referenced in the note field, e.g., ["E_0621"]."""

    @model_validator(mode="after")
    def extract_ebd_references(self) -> "EbdTableSubRow":
        """Extract EBD references from note using regex."""
        if self.note:
            pattern = r"EBD (E_\d{4})"
            self.ebd_references = re.findall(pattern, self.note)
        return self
```

### OutcomeNode (src/rebdhuhn/models/ebd_graph.py)

```python
class OutcomeNode(EbdGraphNode):
    # ... existing fields ...

    ebd_references: list[str] = Field(default_factory=list)
    """EBD codes referenced in this outcome, e.g., ["E_0621"]."""

    @model_validator(mode="after")
    def extract_ebd_references(self) -> "OutcomeNode":
        """Extract EBD references from note using regex."""
        if self.note:
            pattern = r"EBD (E_\d{4})"
            self.ebd_references = re.findall(pattern, self.note)
        return self
```

### Graph Conversion (src/rebdhuhn/graph_conversion.py)

When creating `OutcomeNode` from `EbdTableSubRow`, copy `ebd_references` from the sub_row.

## Rendering Changes

### convert_graph_to_dot signature (src/rebdhuhn/graphviz.py)

```python
def convert_graph_to_dot(
    ebd_graph: EbdGraph,
    ebd_link_template: str | None = None
) -> str:
    """
    ...
    Args:
        ebd_link_template: Optional URL template for EBD cross-references.
            Use {ebd_code} as placeholder, e.g., "?ebd={ebd_code}"
            If None, references are rendered as plain text (no links).
    """
```

### _convert_outcome_node_to_dot changes

- Accept `ebd_link_template` parameter
- When formatting the note, if `ebd_references` is non-empty and template is provided:
  - Replace `EBD E_0621` in the note text with `<a href="?ebd=E_0621">EBD E_0621</a>`
- Use Graphviz HTML-like label syntax for the anchor tag

### Example output

```dot
"E_0621_ref" [label=<<FONT><a href="?ebd=E_0621">EBD E_0621</a>_Prüfen, ob...</FONT>>];
```

## Testing Strategy

### Unit tests

1. **Model extraction tests** (`test_ebd_table_models.py`):
   - `EbdTableSubRow` with note containing `EBD E_0621` → `ebd_references == ["E_0621"]`
   - `EbdTableSubRow` with note containing no reference → `ebd_references == []`
   - `EbdTableSubRow` with multiple references → all captured

2. **Graph conversion test** (`test_table_to_graph.py`):
   - Verify `ebd_references` propagates from `EbdTableSubRow` to `OutcomeNode`

3. **Rendering tests** (`test_graphviz.py` or new file):
   - With `ebd_link_template=None` → no `<a href=...>` in output
   - With `ebd_link_template="?ebd={ebd_code}"` → link appears in DOT output
   - Verify link only wraps the `EBD E_0621` text, not the entire note

### Integration test

- Use real E_0622 JSON, render to DOT with link template, verify clickable links appear
