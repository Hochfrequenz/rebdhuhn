"""
This module contains logic to convert EbdGraph data to dot code (Graphviz) and further to parse this code to SVG images.
"""

from typing import List, Optional, Set, Tuple
from xml.sax.saxutils import escape

from rebdhuhn.add_watermark import add_background as add_background_function
from rebdhuhn.add_watermark import add_watermark as add_watermark_function
from rebdhuhn.kroki import DotToSvgConverter
from rebdhuhn.models import DecisionNode, EbdGraph, EbdGraphEdge, EndNode, OutcomeNode, StartNode, ToNoEdge, ToYesEdge
from rebdhuhn.models.ebd_graph import EmptyNode, TransitionalOutcomeNode, TransitionNode
from rebdhuhn.models.ebd_table import MultiStepInstruction
from rebdhuhn.utils import add_line_breaks

ADD_INDENT = "    "  #: This is just for style purposes to make the plantuml files human-readable.

_LABEL_MAX_LINE_LENGTH = 80
_MSI_LABEL_MAX_LINE_LENGTH = 50  #: Max line length for multi-step instruction labels


def _format_label(label: str) -> str:
    """
    Converts the given string e.g. a text for a node to a suitable output for dot. It replaces newlines (`\n`) with
    the HTML-tag `<BR>`.
    """
    label_with_linebreaks = add_line_breaks(label, max_line_length=_LABEL_MAX_LINE_LENGTH, line_sep="\n")
    return escape(label_with_linebreaks).replace("\n", '<BR align="left"/>')
    # escaped_str = re.sub(r"^(\d+): ", r"<B>\1: </B>", label)
    # escaped_str = label.replace("\n", '<BR align="left"/>')
    # return f'<{escaped_str}<BR align="left"/>>'


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


def _convert_outcome_node_to_dot(ebd_graph: EbdGraph, node: str, indent: str) -> str:
    """
    Convert an OutcomeNode to dot code
    """
    is_outcome_without_code = ebd_graph.graph.nodes[node]["node"].result_code is None
    formatted_label: str = ""
    if not is_outcome_without_code:
        formatted_label += (
            f'<B>{ebd_graph.graph.nodes[node]["node"].result_code}</B><BR align="left"/><BR align="left"/>'
        )
    if ebd_graph.graph.nodes[node]["node"].note:
        formatted_label += (
            f"<FONT>" f'{_format_label(ebd_graph.graph.nodes[node]["node"].note)}<BR align="left"/>' f"</FONT>"
        )
    return (
        f'{indent}"{node}" '
        # pylint:disable=line-too-long
        f'[margin="0.2,0.12", shape=box, style="filled,rounded", penwidth=0.0, fillcolor="#c4cac1", label=<{formatted_label}>, fontname="Roboto, sans-serif"];'
    )


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


def _convert_node_to_dot(ebd_graph: EbdGraph, node: str, indent: str) -> str:
    """
    A shorthand to convert an arbitrary node to dot code. It just determines the node type and calls the
    respective function.
    """
    match ebd_graph.graph.nodes[node]["node"]:
        case DecisionNode():
            return _convert_decision_node_to_dot(ebd_graph, node, indent)
        case OutcomeNode() | TransitionalOutcomeNode():
            return _convert_outcome_node_to_dot(ebd_graph, node, indent)
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
        f'[margin="0.2,0.12", shape=note, style=filled, penwidth=0.0, fillcolor="#e6f3ff", '
        f'label=<{formatted_label}>, fontname="Roboto, sans-serif"];'
    )


def _get_step_number_from_node(ebd_graph: EbdGraph, node: str) -> Optional[str]:
    """
    Extract the step number from a node if it has one (DecisionNode or TransitionNode).
    Returns None for nodes without step numbers (Start, End, Outcome nodes).
    """
    node_data = ebd_graph.graph.nodes[node]["node"]
    if hasattr(node_data, "step_number"):
        return str(node_data.step_number)
    return None


def _compute_instruction_ranges(
    instructions: List[MultiStepInstruction], all_step_numbers: Set[str]
) -> List[Tuple[MultiStepInstruction, str, Optional[str]]]:
    """
    Compute the step number range for each multi-step instruction.
    Returns list of (instruction, start_step, end_step) tuples.
    end_step is None if the instruction applies to the end of the graph.
    """
    if not instructions:
        return []

    # Sort instructions by their first step number (numerically)
    sorted_instructions = sorted(instructions, key=lambda x: int(x.first_step_number_affected))

    ranges: List[Tuple[MultiStepInstruction, str, Optional[str]]] = []
    for i, inst in enumerate(sorted_instructions):
        start_step = inst.first_step_number_affected
        # End step is the step before the next instruction starts, or None if last
        if i + 1 < len(sorted_instructions):
            next_start = int(sorted_instructions[i + 1].first_step_number_affected)
            # Find the highest step number less than next_start
            end_step: Optional[str] = None
            for step in all_step_numbers:
                step_int = int(step)
                if int(start_step) <= step_int < next_start:
                    if end_step is None or step_int > int(end_step):
                        end_step = step
        else:
            end_step = None  # Last instruction applies to end of graph

        ranges.append((inst, start_step, end_step))

    return ranges


def _get_nodes_in_step_range(ebd_graph: EbdGraph, start_step: str, end_step: Optional[str]) -> List[str]:
    """
    Get all node keys that have step numbers within the given range (inclusive).
    If end_step is None, includes all steps >= start_step.
    """
    nodes_in_range: List[str] = []
    start_int = int(start_step)
    end_int = int(end_step) if end_step else None

    for node in ebd_graph.graph.nodes:
        step_number = _get_step_number_from_node(ebd_graph, node)
        if step_number is not None:
            step_int = int(step_number)
            if step_int >= start_int and (end_int is None or step_int <= end_int):
                nodes_in_range.append(node)

    return nodes_in_range


def _convert_multi_step_instruction_cluster_to_dot(
    ebd_graph: EbdGraph,
    instruction: MultiStepInstruction,
    start_step: str,
    end_step: Optional[str],
    indent: str,
) -> str:
    """
    Convert a multi-step instruction and its affected nodes to a DOT subgraph cluster.
    The cluster creates a light box around all nodes affected by the instruction.
    """
    cluster_indent = indent
    inner_indent = indent + ADD_INDENT

    node_key = _get_multi_step_instruction_node_key(instruction)
    cluster_name = f"cluster_{node_key}"

    # Get all nodes in the step range
    nodes_in_range = _get_nodes_in_step_range(ebd_graph, start_step, end_step)

    lines: List[str] = []
    lines.append(f'{cluster_indent}subgraph "{cluster_name}" {{')
    # Light blue background with dashed border to match instruction node style
    lines.append(f'{inner_indent}style="dashed,rounded";')
    lines.append(f'{inner_indent}bgcolor="#f0f7ff";')  # Very light blue, lighter than instruction node
    lines.append(f'{inner_indent}color="#888888";')
    lines.append(f"{inner_indent}penwidth=1.5;")
    lines.append(f"{inner_indent}margin=16;")

    # Add the instruction node inside the cluster
    lines.append(_convert_multi_step_instruction_to_dot(instruction, inner_indent))

    # Add all affected step nodes inside the cluster
    for node in nodes_in_range:
        lines.append(_convert_node_to_dot(ebd_graph, node, inner_indent))

    lines.append(f"{cluster_indent}}}")

    return "\n".join(lines)


def _convert_nodes_to_dot(ebd_graph: EbdGraph, indent: str) -> str:
    """
    Convert all nodes of the EbdGraph to dot output and return it as a string.
    Nodes affected by multi-step instructions are grouped into clusters.
    """
    result_parts: List[str] = []

    # Track which nodes are already rendered inside clusters
    nodes_in_clusters: Set[str] = set()

    # Add multi-step instruction clusters if present
    if ebd_graph.multi_step_instructions:
        # Get all step numbers from the graph
        all_step_numbers: Set[str] = set()
        for node in ebd_graph.graph.nodes:
            step_number = _get_step_number_from_node(ebd_graph, node)
            if step_number is not None:
                all_step_numbers.add(step_number)

        # Compute ranges and create clusters
        ranges = _compute_instruction_ranges(ebd_graph.multi_step_instructions, all_step_numbers)
        for instruction, start_step, end_step in ranges:
            result_parts.append(
                _convert_multi_step_instruction_cluster_to_dot(ebd_graph, instruction, start_step, end_step, indent)
            )
            # Track nodes that are inside this cluster
            nodes_in_range = _get_nodes_in_step_range(ebd_graph, start_step, end_step)
            nodes_in_clusters.update(nodes_in_range)

    # Add remaining nodes that are not inside any cluster
    for node in ebd_graph.graph.nodes:
        if node not in nodes_in_clusters:
            result_parts.append(_convert_node_to_dot(ebd_graph, node, indent))

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


def _convert_edges_to_dot(ebd_graph: EbdGraph, indent: str) -> List[str]:
    """
    Convert all edges of the EbdGraph to dot output and return it as a string.
    Note: Multi-step instruction edges are no longer needed since instruction nodes
    are now inside clusters with their affected step nodes.
    """
    edges: List[str] = []

    # Add regular graph edges
    edges.extend([_convert_edge_to_dot(ebd_graph, edge[0], edge[1], indent) for edge in ebd_graph.graph.edges])

    return edges


def convert_graph_to_dot(ebd_graph: EbdGraph) -> str:
    """
    Convert the EbdGraph to dot output for Graphviz. Returns the dot code as string.
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
    dot_code += _convert_nodes_to_dot(ebd_graph, ADD_INDENT) + "\n\n"
    if "Start" in nx_graph:
        assert len(nx_graph["Start"]) == 1, "Start node must have exactly one outgoing edge."
        dot_code += "\n".join(_convert_edges_to_dot(ebd_graph, ADD_INDENT)) + "\n"
    dot_code += '\n    bgcolor="transparent";\nfontname="Roboto, sans-serif";\n'
    return dot_code + "}"


def convert_dot_to_svg_kroki(
    dot_code: str, dot_to_svg_converter: DotToSvgConverter, add_watermark: bool = True, add_background: bool = True
) -> str:
    """
    Converts dot code to svg (code) and returns the result as string. It uses kroki.io.
    Optionally add the HF watermark to the svg code, controlled by the argument 'add_watermark'
    Optionally add a background with the color 'HF white', controlled by the argument 'add_background'
    If 'add_background' is False, the background is transparent.
    """
    svg_out = dot_to_svg_converter.convert_dot_to_svg(dot_code)
    if add_watermark:
        svg_out = add_watermark_function(svg_out)
    if add_background:
        svg_out = add_background_function(svg_out)
    return svg_out
