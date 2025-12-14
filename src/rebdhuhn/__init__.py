"""
contains the conversion logic
"""

from rebdhuhn.graph_conversion import convert_table_to_digraph, convert_table_to_graph
from rebdhuhn.graphviz import convert_dot_to_svg_kroki, convert_graph_to_dot
from rebdhuhn.kroki import DotToSvgConverter, Kroki, PlantUmlToSvgConverter
from rebdhuhn.models import (
    DecisionNode,
    EbdCheckResult,
    EbdGraph,
    EbdGraphMetaData,
    EbdTable,
    EbdTableMetaData,
    EbdTableRow,
    EbdTableSubRow,
    EndNode,
    MultiStepInstruction,
    OutcomeNode,
)
from rebdhuhn.models.errors import GraphConversionError, PlantumlConversionError, SvgConversionError
from rebdhuhn.plantuml import convert_graph_to_plantuml, convert_plantuml_to_svg_kroki

# pylint: disable=duplicate-code
__all__ = [
    # Conversion functions
    "convert_table_to_digraph",
    "convert_table_to_graph",
    "convert_dot_to_svg_kroki",
    "convert_graph_to_dot",
    "convert_graph_to_plantuml",
    "convert_plantuml_to_svg_kroki",
    # Kroki converters
    "DotToSvgConverter",
    "Kroki",
    "PlantUmlToSvgConverter",
    # Graph models
    "DecisionNode",
    "EbdGraph",
    "EbdGraphMetaData",
    "EndNode",
    "OutcomeNode",
    # Table models
    "EbdCheckResult",
    "EbdTable",
    "EbdTableMetaData",
    "EbdTableRow",
    "EbdTableSubRow",
    "MultiStepInstruction",
    # Exceptions
    "GraphConversionError",
    "PlantumlConversionError",
    "SvgConversionError",
]
