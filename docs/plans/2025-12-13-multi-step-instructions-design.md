# Multi-Step Instructions Visualization Design

## Overview

Render multi-step instructions as clustered boxes in DOT/SVG output. Each instruction and its affected steps are grouped within a subgraph cluster, clearly showing the scope of the instruction.

## Context

Multi-step instructions are contextual notes in EBD tables that apply to multiple steps from a specified step number onwards. Examples include:
- "The following checks are performed for each MaLo"
- "All identified answers should be provided, up to 8 response codes"

Currently, `multi_step_instructions` are parsed and passed through to `EbdGraph`, but not rendered in the visual output.

## Visual Specification

### Instruction Node
- Light blue background (`#e6f3ff`)
- Word-wrapped text at ~50 characters per line
- Same font as other nodes (Roboto)
- Shape: `note` (gives a folded corner appearance)
- Node key format: `msi_{step_number}` (e.g., `msi_100`)

### Cluster Box
- Very light blue background (`#f0f7ff`) - lighter than instruction node
- Dashed, rounded border
- Gray border color (`#888888`)
- Contains the instruction node and all affected step nodes
- Cluster name format: `cluster_msi_{step_number}`

### Scope Determination
- Each instruction applies from its `first_step_number_affected` until the next instruction begins
- The last instruction applies to all remaining steps

## Example DOT Output

```dot
// Cluster containing instruction and affected steps
subgraph "cluster_msi_100" {
    style="dashed,rounded";
    bgcolor="#f0f7ff";
    color="#888888";
    penwidth=1.5;
    margin=16;

    // Multi-step instruction node
    "msi_100" [
        label=<Die nachfolgenden Prüfungen erfolgen<BR/>auf Basis der Identifikationskriterien...>,
        shape=note,
        style=filled,
        fillcolor="#e6f3ff",
        fontname="Roboto, sans-serif"
    ];

    // Affected step nodes (100-199)
    "100" [...];
    "105" [...];
    // ... more steps
}
```

## Implementation

### Changes to `src/rebdhuhn/graphviz.py`

1. `_convert_multi_step_instruction_to_dot()` - renders instruction node
2. `_get_step_number_from_node()` - extracts step number from node
3. `_compute_instruction_ranges()` - determines step range for each instruction
4. `_get_nodes_in_step_range()` - finds nodes within a step range
5. `_convert_multi_step_instruction_cluster_to_dot()` - renders cluster with instruction and affected nodes
6. Update `_convert_nodes_to_dot()` - generate clusters for instructions, regular nodes for others

### No changes needed to
- Models (already pass `multi_step_instructions` through)
- PlantUML (out of scope)

## Testing

- Verify instruction nodes appear in DOT output
- Verify cluster subgraph syntax
- Verify light blue fill colors (instruction node and cluster)
- Verify cluster contains correct step nodes
- Snapshot test for visual regression
