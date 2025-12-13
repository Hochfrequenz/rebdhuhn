# Multi-Step Instructions Visualization Design

## Overview

Render multi-step instructions as annotation boxes in DOT/SVG output. Each instruction appears as a distinct box positioned above the first affected step node, connected by a dashed line.

## Context

Multi-step instructions are contextual notes in EBD tables that apply to multiple steps from a specified step number onwards. Examples include:
- "The following checks are performed for each MaLo"
- "All identified answers should be provided, up to 8 response codes"

Currently, `multi_step_instructions` are parsed and passed through to `EbdGraph`, but not rendered in the visual output.

## Visual Specification

### Annotation Box
- Light blue background (`#e6f3ff`)
- Word-wrapped text at ~50 characters per line
- Same font as other nodes (Roboto)
- Shape: `note` (gives a folded corner appearance)

### Connection
- Dashed line from annotation box to first affected step node
- No arrowhead
- Gray color (`#888888`) to avoid visual clutter

### Positioning
- Above the target decision node
- Node key format: `msi_{step_number}` (e.g., `msi_100`)

## Example DOT Output

```dot
// Multi-step instruction node
"msi_100" [
    label=<Die nachfolgenden Prüfungen erfolgen<BR/>auf Basis der Identifikationskriterien...>,
    shape=note,
    style=filled,
    fillcolor="#e6f3ff",
    fontname="Roboto, sans-serif"
];

// Dashed edge to first affected step
"msi_100" -> "100" [style=dashed, color="#888888", arrowhead=none];
```

## Implementation

### Changes to `src/rebdhuhn/graphviz.py`

1. New function `_convert_multi_step_instruction_to_dot()` - renders instruction node
2. New function `_convert_multi_step_instruction_edge_to_dot()` - renders dashed edge
3. Update `_convert_nodes_to_dot()` - generate instruction nodes
4. Update edge generation - add dashed edges

### No changes needed to
- Models (already pass `multi_step_instructions` through)
- PlantUML (out of scope)

## Testing

- Verify instruction nodes appear in DOT output
- Verify dashed edge syntax
- Verify light blue fill color
- Snapshot test for visual regression
