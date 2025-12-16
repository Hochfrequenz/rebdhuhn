"""
This module contains logic to convert EbdGraph data to dot code (Graphviz) and further to parse this code to SVG images.

Multi-Step Instructions (MSI) Visualization
-------------------------------------------
MultiStepInstruction (defined in rebdhuhn.models.ebd_table) provides only `first_step_number_affected`
and `instruction_text` - there is no explicit end step.

Assumptions made for visualization:
- Instructions are sorted by first_step_number_affected (numerically)
- Each instruction's scope extends from its first_step_number_affected until the next instruction begins
- The last instruction's scope extends to the end of the graph
- Step numbers can be parsed as integers for comparison

Not included in current visualization:
- Outcome nodes are not grouped into instruction clusters (only decision/transition nodes with step numbers)
- No visual distinction between different instruction types (e.g., "per MaLo" vs "collect all answers")
- PlantUML output does not render multi-step instructions
"""

import re
from xml.sax.saxutils import escape

from rebdhuhn.add_watermark import add_background as add_background_function
from rebdhuhn.add_watermark import add_release_info_footer
from rebdhuhn.add_watermark import add_watermark as add_watermark_function
from rebdhuhn.kroki import DotToSvgConverter
from rebdhuhn.models import DecisionNode, EbdGraph, EbdGraphEdge, EndNode, OutcomeNode, StartNode, ToNoEdge, ToYesEdge
from rebdhuhn.models.ebd_graph import EmptyNode, TransitionalOutcomeNode, TransitionNode
from rebdhuhn.models.ebd_table import EBD_REFERENCE_REGEX, EbdDocumentReleaseInformation, MultiStepInstruction
from rebdhuhn.utils import add_line_breaks

ADD_INDENT = "    "  #: This is just for style purposes to make the plantuml files human-readable.

_LABEL_MAX_LINE_LENGTH = 80
_MSI_LABEL_MAX_LINE_LENGTH = 50  #: Max line length for multi-step instruction labels
_MSI_NODE_BGCOLOR = "#e6f3ff"  #: Light blue background for multi-step instruction nodes
_MSI_CLUSTER_BGCOLOR = "#f0f7ff"  #: Very light blue background for multi-step instruction clusters


def _format_label(label: str, ebd_link_template: str | None = None) -> str:
    """
    Converts the given string e.g. a text for a node to a suitable output for dot. It replaces newlines (`\n`) with
    the HTML-tag `<BR>`.

    Args:
        label: The text to format
        ebd_link_template: Optional URL template for EBD cross-references.
            Use {ebd_code} as placeholder, e.g., "?ebd={ebd_code}"
            If provided, EBD references like "EBD E_0621" will be rendered as clickable links.
    """
    label_with_linebreaks = add_line_breaks(label, max_line_length=_LABEL_MAX_LINE_LENGTH, line_sep="\n")
    escaped_label = escape(label_with_linebreaks)

    # Replace EBD references with styled text if template is provided
    if ebd_link_template:
        escaped_label = _replace_ebd_references_with_styled_text(escaped_label)

    return escaped_label.replace("\n", '<BR align="left"/>')


def _replace_ebd_references_with_styled_text(text: str) -> str:
    """
    Replaces EBD references like "EBD E_0621" with styled text indicating a link.

    Graphviz HTML-like labels don't support <a href> tags directly in most contexts.
    Instead, we style the reference text with underline and blue color to visually
    indicate it's a link. The actual href is added at the node level for nodes
    that contain EBD references.

    Args:
        text: The text containing potential EBD references

    Returns:
        Text with EBD references styled as links (underlined, blue)
    """

    def replace_match(match: re.Match[str]) -> str:
        ebd_code = match.group(1)
        # Style as link: underline and blue color
        return f'<FONT COLOR="#0066cc"><U>EBD {ebd_code}</U></FONT>'

    return re.sub(EBD_REFERENCE_REGEX, replace_match, text)


def _convert_start_node_to_dot(ebd_graph: EbdGraph, node: str, indent: str) -> str:
    """
    Convert a StartNode to dot code
    """
    formatted_label = (
        f'<B>{ebd_graph.metadata.ebd_code}</B><BR align="left"/>'
        f'<FONT>Prüfende Rolle: <B>{ebd_graph.metadata.role}</B></FONT><BR align="center"/>'
    )
    return (
        f'{indent}"{node}" '
        # pylint:disable=line-too-long
        f'[margin="0.2,0.12", shape=box, style="filled,rounded", penwidth=0.0, fillcolor="#8ba2d7", label=<{formatted_label}>, fontname="Roboto, sans-serif"];'
    )


def _convert_empty_node_to_dot(ebd_graph: EbdGraph, node: str, indent: str) -> str:
    """
    Convert an EmptyNode to dot code
    """
    formatted_label = f'<B>{ebd_graph.metadata.ebd_code}</B><BR align="center"/>'
    if ebd_graph.metadata.remark:
        formatted_label += f'<FONT>{ebd_graph.metadata.remark}</FONT><BR align="center"/>'
    return (
        f'{indent}"{node}" '
        # pylint:disable=line-too-long
        f'[margin="0.2,0.12", shape=box, style="filled,rounded", penwidth=0.0, fillcolor="#7a8da1", label=<{formatted_label}>, fontname="Roboto, sans-serif"];'
    )


def _convert_end_node_to_dot(node: str, indent: str) -> str:
    """
    Convert an EndNode to dot code
    """
    # pylint:disable=line-too-long
    return f'{indent}"{node}" [margin="0.2,0.12", shape=box, style="filled,rounded", penwidth=0.0, fillcolor="#8ba2d7", label="Ende", fontname="Roboto, sans-serif"];'


def _convert_outcome_node_to_dot(
    ebd_graph: EbdGraph, node: str, indent: str, ebd_link_template: str | None = None
) -> str:
    """
    Convert an OutcomeNode to dot code

    Args:
        ebd_graph: The EBD graph
        node: The node key
        indent: Indentation string
        ebd_link_template: Optional URL template for EBD cross-references.
            Use {ebd_code} as placeholder, e.g., "?ebd={ebd_code}"
    """
    outcome_node = ebd_graph.graph.nodes[node]["node"]
    is_outcome_without_code = outcome_node.result_code is None
    formatted_label: str = ""
    if not is_outcome_without_code:
        formatted_label += f'<B>{outcome_node.result_code}</B><BR align="left"/><BR align="left"/>'
    if outcome_node.note:
        formatted_label += (
            f"<FONT>" f'{_format_label(outcome_node.note, ebd_link_template)}<BR align="left"/>' f"</FONT>"
        )

    # Build node attributes
    attrs = [
        'margin="0.2,0.12"',
        "shape=box",
        'style="filled,rounded"',
        "penwidth=0.0",
        'fillcolor="#c4cac1"',
        f"label=<{formatted_label}>",
        'fontname="Roboto, sans-serif"',
    ]

    # Add href for nodes with exactly one EBD reference (makes entire node clickable)
    if ebd_link_template and hasattr(outcome_node, "ebd_references") and len(outcome_node.ebd_references) == 1:
        ebd_code = outcome_node.ebd_references[0]
        url = ebd_link_template.replace("{ebd_code}", ebd_code)
        attrs.append(f'href="{url}"')
        attrs.append('target="_blank"')
        # Set tooltip to just the EBD code to prevent raw HTML appearing in xlink:title
        # (Graphviz defaults tooltip to label, which shows raw HTML-like label text on hover)
        attrs.append(f'tooltip="{ebd_code}"')

    # pylint:disable=line-too-long
    return f'{indent}"{node}" [{", ".join(attrs)}];'


def _convert_decision_node_to_dot(ebd_graph: EbdGraph, node: str, indent: str) -> str:
    """
    Convert a DecisionNode to dot code
    """
    formatted_label = (
        f'<B>{ebd_graph.graph.nodes[node]["node"].step_number}: </B>'
        f'{_format_label(ebd_graph.graph.nodes[node]["node"].question)}'
        f'<BR align="left"/>'
    )
    return (
        f'{indent}"{node}" [margin="0.2,0.12", shape=box, style="filled,rounded", penwidth=0.0, fillcolor="#c2cee9", '
        f'label=<{formatted_label}>, fontname="Roboto, sans-serif"];'
    )


def _convert_transition_node_to_dot(ebd_graph: EbdGraph, node: str, indent: str) -> str:
    """
    Convert a TransitionNode to dot code
    """
    formatted_label = (
        f'<B>{ebd_graph.graph.nodes[node]["node"].step_number}: </B>'
        f'{_format_label(ebd_graph.graph.nodes[node]["node"].question)}'
        f'<BR align="left"/>'
    )
    if ebd_graph.graph.nodes[node]["node"].note:
        formatted_label += (
            f"<FONT>" f'{_format_label(ebd_graph.graph.nodes[node]["node"].note)}<BR align="left"/>' f"</FONT>"
        )
    return (
        f'{indent}"{node}" [margin="0.2,0.12", shape=box, style="filled,rounded", penwidth=0.0, fillcolor="#c2cee9", '
        f'label=<{formatted_label}>, fontname="Roboto, sans-serif"];'
    )


def _convert_node_to_dot(ebd_graph: EbdGraph, node: str, indent: str, ebd_link_template: str | None = None) -> str:
    """
    A shorthand to convert an arbitrary node to dot code. It just determines the node type and calls the
    respective function.

    Args:
        ebd_graph: The EBD graph
        node: The node key
        indent: Indentation string
        ebd_link_template: Optional URL template for EBD cross-references.
    """
    match ebd_graph.graph.nodes[node]["node"]:
        case DecisionNode():
            return _convert_decision_node_to_dot(ebd_graph, node, indent)
        case OutcomeNode() | TransitionalOutcomeNode():
            return _convert_outcome_node_to_dot(ebd_graph, node, indent, ebd_link_template)
        case EndNode():
            return _convert_end_node_to_dot(node, indent)
        case StartNode():
            return _convert_start_node_to_dot(ebd_graph, node, indent)
        case EmptyNode():
            return _convert_empty_node_to_dot(ebd_graph, node, indent)
        case TransitionNode():
            return _convert_transition_node_to_dot(ebd_graph, node, indent)
        case _:
            raise ValueError(f"Unknown node type: {ebd_graph.graph.nodes[node]['node']}")


def _get_multi_step_instruction_node_key(instruction: MultiStepInstruction) -> str:
    """
    Returns the node key for a multi-step instruction node.
    Format: msi_{first_step_number_affected}
    """
    return f"msi_{instruction.first_step_number_affected}"


def _convert_multi_step_instruction_to_dot(instruction: MultiStepInstruction, indent: str) -> str:
    """
    Convert a MultiStepInstruction to a dot node.
    Uses light blue background (#e6f3ff) to distinguish from outcome notes.
    """
    # Format the instruction text with word wrapping
    label_with_linebreaks = add_line_breaks(
        instruction.instruction_text, max_line_length=_MSI_LABEL_MAX_LINE_LENGTH, line_sep="\n"
    )
    formatted_label = escape(label_with_linebreaks).replace("\n", '<BR align="left"/>')
    formatted_label = f'<FONT><I>{formatted_label}</I></FONT><BR align="left"/>'

    node_key = _get_multi_step_instruction_node_key(instruction)
    # pylint:disable=line-too-long
    return (
        f'{indent}"{node_key}" '
        f'[margin="0.2,0.12", shape=note, style=filled, penwidth=0.0, fillcolor="{_MSI_NODE_BGCOLOR}", '
        f'label=<{formatted_label}>, fontname="Roboto, sans-serif"];'
    )


def _collect_node_keys_in_step_range(ebd_graph: EbdGraph, start_step: str, end_step: str | None) -> set[str]:
    """
    Returns node keys for nodes with step numbers in [start_step, end_step].
    If end_step is None, includes all steps >= start_step.
    """
    start = int(start_step)
    end = int(end_step) if end_step else None

    node_keys: set[str] = set()
    for node_key in ebd_graph.graph.nodes:
        node = ebd_graph.graph.nodes[node_key]["node"]
        if not hasattr(node, "step_number"):
            continue
        step = int(node.step_number)
        if step >= start and (end is None or step <= end):
            node_keys.add(node_key)

    return node_keys


def _convert_multi_step_instruction_cluster_to_dot(
    ebd_graph: EbdGraph,
    instruction: MultiStepInstruction,
    affected_node_keys: set[str],
    indent: str,
    ebd_link_template: str | None = None,
) -> str:
    """
    Renders a DOT subgraph cluster containing the instruction note and all affected step nodes.

    Args:
        ebd_graph: The EBD graph
        instruction: The multi-step instruction
        affected_node_keys: Node keys affected by this instruction
        indent: Indentation string
        ebd_link_template: Optional URL template for EBD cross-references.
    """
    inner_indent = indent + ADD_INDENT
    msi_node_key = _get_multi_step_instruction_node_key(instruction)

    lines: list[str] = [
        f'{indent}subgraph "cluster_{msi_node_key}" {{',
        f'{inner_indent}label="";',
        f'{inner_indent}style="dashed,rounded";',
        f'{inner_indent}bgcolor="{_MSI_CLUSTER_BGCOLOR}";',
        f'{inner_indent}color="#888888";',
        f"{inner_indent}penwidth=1.5;",
        f"{inner_indent}margin=16;",
        _convert_multi_step_instruction_to_dot(instruction, inner_indent),
    ]
    for node_key in sorted(affected_node_keys, key=lambda k: int(k) if k.isdigit() else float("inf")):
        lines.append(_convert_node_to_dot(ebd_graph, node_key, inner_indent, ebd_link_template))
    lines.append(f"{indent}}}")

    return "\n".join(lines)


def _convert_nodes_to_dot(ebd_graph: EbdGraph, indent: str, ebd_link_template: str | None = None) -> str:
    """
    Convert all nodes of the EbdGraph to dot output.
    Nodes affected by multi-step instructions are grouped into clusters.

    Args:
        ebd_graph: The EBD graph
        indent: Indentation string
        ebd_link_template: Optional URL template for EBD cross-references.
    """
    result_parts: list[str] = []
    node_keys_in_clusters: set[str] = set()

    for scope in ebd_graph.get_instruction_scopes():
        affected_node_keys = _collect_node_keys_in_step_range(ebd_graph, scope.start_step, scope.end_step)
        result_parts.append(
            _convert_multi_step_instruction_cluster_to_dot(
                ebd_graph, scope.instruction, affected_node_keys, indent, ebd_link_template
            )
        )
        node_keys_in_clusters.update(affected_node_keys)

    for node_key in ebd_graph.graph.nodes:
        if node_key not in node_keys_in_clusters:
            result_parts.append(_convert_node_to_dot(ebd_graph, node_key, indent, ebd_link_template))

    return "\n".join(result_parts)


def _convert_yes_edge_to_dot(node_src: str, node_target: str, indent: str) -> str:
    """
    Converts a YesEdge to dot code
    """
    return (
        f'{indent}"{node_src}" -> "{node_target}" [label=<<B>JA</B>>, color="#88a0d6", fontname="Roboto, sans-serif"];'
    )


def _convert_no_edge_to_dot(node_src: str, node_target: str, indent: str) -> str:
    """
    Converts a NoEdge to dot code
    """
    # pylint:disable=line-too-long
    return f'{indent}"{node_src}" -> "{node_target}" [label=<<B>NEIN</B>>, color="#88a0d6", fontname="Roboto, sans-serif"];'


def _convert_ebd_graph_edge_to_dot(node_src: str, node_target: str, indent: str) -> str:
    """
    Converts a simple GraphEdge to dot code
    """
    return f'{indent}"{node_src}" -> "{node_target}" [color="#88a0d6"];'


def _convert_edge_to_dot(ebd_graph: EbdGraph, node_src: str, node_target: str, indent: str) -> str:
    """
    A shorthand to convert an arbitrary node to dot code. It just determines the node type and calls the
    respective function.
    """
    match ebd_graph.graph[node_src][node_target]["edge"]:
        case ToYesEdge():
            return _convert_yes_edge_to_dot(node_src, node_target, indent)
        case ToNoEdge():
            return _convert_no_edge_to_dot(node_src, node_target, indent)
        case EbdGraphEdge():
            return _convert_ebd_graph_edge_to_dot(node_src, node_target, indent)
        case _:
            raise ValueError(f"Unknown edge type: {ebd_graph.graph[node_src][node_target]['edge']}")


def _convert_edges_to_dot(ebd_graph: EbdGraph, indent: str) -> list[str]:
    """
    Convert all edges of the EbdGraph to dot output and return it as a string.
    Note: Multi-step instruction edges are no longer needed since instruction nodes
    are now inside clusters with their affected step nodes.
    """
    edges: list[str] = []

    # Add regular graph edges
    edges.extend([_convert_edge_to_dot(ebd_graph, edge[0], edge[1], indent) for edge in ebd_graph.graph.edges])

    return edges


def convert_graph_to_dot(ebd_graph: EbdGraph, ebd_link_template: str | None = None) -> str:
    """
    Convert the EbdGraph to dot output for Graphviz. Returns the dot code as string.

    Args:
        ebd_graph: The EBD graph to convert
        ebd_link_template: Optional URL template for EBD cross-references.
            Use {ebd_code} as placeholder, e.g., "?ebd={ebd_code}"
            If provided, EBD references like "EBD E_0621" in outcome node notes
            will be rendered as clickable links in the SVG output.
    """
    nx_graph = ebd_graph.graph
    # _mark_last_common_ancestors(nx_graph)
    header = (
        f'<B><FONT POINT-SIZE="18">{ebd_graph.metadata.chapter}</FONT></B><BR align="left"/><BR/>'
        f'<B><FONT POINT-SIZE="16">{ebd_graph.metadata.section}</FONT></B><BR align="left"/><BR/><BR/><BR/>'
    )

    dot_attributes: dict[str, str] = {
        # https://graphviz.org/doc/info/attrs.html
        "labelloc": '"t"',
        "label": f"<{header}>",
        "ratio": '"compress"',
        "concentrate": "true",
        "pack": "true",
        "rankdir": "TB",
        "packmode": '"array"',
        "size": '"20,20"',  # in inches 🤮
        "fontsize": "12",
        "pad": "0.25",  # https://graphviz.org/docs/attrs/pad/
    }
    dot_code = "digraph D {\n"
    for dot_attr_key, dot_attr_value in dot_attributes.items():
        dot_code += f"{ADD_INDENT}{dot_attr_key}={dot_attr_value};\n"
    dot_code += _convert_nodes_to_dot(ebd_graph, ADD_INDENT, ebd_link_template) + "\n\n"
    if "Start" in nx_graph:
        assert len(nx_graph["Start"]) == 1, "Start node must have exactly one outgoing edge."
        dot_code += "\n".join(_convert_edges_to_dot(ebd_graph, ADD_INDENT)) + "\n"
    dot_code += '\n    bgcolor="transparent";\nfontname="Roboto, sans-serif";\n'
    return dot_code + "}"


def convert_dot_to_svg_kroki(
    dot_code: str,
    dot_to_svg_converter: DotToSvgConverter,
    add_watermark: bool = True,
    add_background: bool = True,
    release_info: EbdDocumentReleaseInformation | None = None,
) -> str:
    """
    Converts dot code to svg (code) and returns the result as string. It uses kroki.io.
    Optionally add the HF watermark to the svg code, controlled by the argument 'add_watermark'
    Optionally add a background with the color 'HF white', controlled by the argument 'add_background'
    If 'add_background' is False, the background is transparent.
    If 'release_info' is provided, adds release information footer to the bottom-right corner.
    """
    svg_out = dot_to_svg_converter.convert_dot_to_svg(dot_code)
    if add_watermark:
        svg_out = add_watermark_function(svg_out)
    if add_background:
        svg_out = add_background_function(svg_out)
    if release_info:
        svg_out = add_release_info_footer(svg_out, release_info)
    return svg_out
