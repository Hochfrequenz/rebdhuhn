"""
contains the conversion logic
"""

from rebdhuhn.graph_conversion import convert_table_to_digraph, convert_table_to_graph
from rebdhuhn.graphviz import convert_dot_to_svg_kroki, convert_graph_to_dot
from rebdhuhn.models.errors import GraphConversionError, PlantumlConversionError, SvgConversionError
from rebdhuhn.plantuml import convert_graph_to_plantuml, convert_plantuml_to_svg_kroki

__all__ = [
    "convert_table_to_digraph",
    "convert_table_to_graph",
    "convert_dot_to_svg_kroki",
    "convert_graph_to_dot",
    "convert_graph_to_plantuml",
    "convert_plantuml_to_svg_kroki",
    # Base exception classes for pipeline distinction
    "GraphConversionError",
    "PlantumlConversionError",
    "SvgConversionError",
]
