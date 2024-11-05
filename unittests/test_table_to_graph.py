# mypy: disable-error-code="no-untyped-def"
import os
from pathlib import Path
from typing import List, Optional

import pytest
from lxml import etree
from networkx import DiGraph  # type:ignore[import-untyped]

from rebdhuhn import convert_graph_to_plantuml, convert_plantuml_to_svg_kroki, convert_table_to_graph
from rebdhuhn.graph_conversion import get_all_edges, get_all_nodes
from rebdhuhn.graphviz import convert_dot_to_svg_kroki, convert_graph_to_dot
from rebdhuhn.kroki import Kroki
from rebdhuhn.models import EbdGraph, EbdGraphMetaData
from rebdhuhn.models.ebd_graph import (
    DecisionNode,
    EbdGraphEdge,
    EbdGraphNode,
    EndNode,
    OutcomeNode,
    StartNode,
    ToNoEdge,
    ToYesEdge,
)
from rebdhuhn.models.ebd_table import EbdTable
from rebdhuhn.models.errors import GraphTooComplexForPlantumlError
from unittests.examples import table_e0003, table_e0015, table_e0025, table_e0401


class InterceptedKrokiClient(Kroki):
    """
    a wrapper around the kroki client for testing purposes. This class makes it possible to access the kroki
    response. It also provides an alternative version of the kroki response that has a comment for documentation
    purposes.
    """

    def __init__(self) -> None:
        super().__init__()
        self.intercepted_kroki_response: Optional[str] = None
        self.intercepted_kroki_response_with_xml_comment: Optional[str] = None

    def convert_dot_to_svg(self, *args, **kwargs) -> str:
        result = super().convert_dot_to_svg(*args, **kwargs)
        self.intercepted_kroki_response = result
        result_tree = etree.fromstring(result.encode("utf-8"))
        my_comment = (
            "curl --request POST "
            "--url https://kroki.io/ via local kroki docker container instance hosted at http://localhost:8125/"
            "--header 'Content-Type: application/json' "
            f"--data '{args[0]}'"
        ).replace(
            "--", "- -"
        )  # replace double hyphen for xml compatability
        result_tree.insert(0, etree.Comment(my_comment))
        self.intercepted_kroki_response_with_xml_comment = etree.tostring(result_tree).decode("utf-8")
        return result


class TestEbdTableModels:
    @pytest.mark.parametrize(
        "table,expected_result",
        [
            pytest.param(
                table_e0003,
                [
                    StartNode(),
                    DecisionNode(step_number="1", question="Erfolgt der Eingang der Bestellung fristgerecht?"),
                    OutcomeNode(result_code="A01", note="Fristüberschreitung"),
                    DecisionNode(step_number="2", question="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?"),
                    OutcomeNode(result_code="A02", note="Gewählter Zeitpunkt nicht zulässig"),
                    EndNode(),
                ],
            )
        ],
    )
    def test_get_all_nodes(self, table: EbdTable, expected_result: List[EbdGraphNode]) -> None:
        actual = get_all_nodes(table)
        assert actual == expected_result

    @pytest.mark.parametrize(
        "table,expected_result",
        [
            pytest.param(
                table_e0003,
                [
                    EbdGraphEdge(
                        source=StartNode(),
                        target=DecisionNode(
                            step_number="1", question="Erfolgt der Eingang der Bestellung fristgerecht?"
                        ),
                        note=None,
                    ),
                    ToNoEdge(
                        source=DecisionNode(
                            step_number="1", question="Erfolgt der Eingang der Bestellung fristgerecht?"
                        ),
                        target=OutcomeNode(result_code="A01", note="Fristüberschreitung"),
                        note=None,
                    ),
                    ToYesEdge(
                        source=DecisionNode(
                            step_number="1", question="Erfolgt der Eingang der Bestellung fristgerecht?"
                        ),
                        target=DecisionNode(
                            step_number="2", question="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?"
                        ),
                        note=None,
                    ),
                    ToNoEdge(
                        source=DecisionNode(
                            step_number="2", question="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?"
                        ),
                        target=OutcomeNode(result_code="A02", note="Gewählter Zeitpunkt nicht zulässig"),
                        note=None,
                    ),
                    ToYesEdge(
                        source=DecisionNode(
                            step_number="2", question="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?"
                        ),
                        target=EndNode(),
                        note=None,
                    ),
                ],
            )
        ],
    )
    def test_get_all_edges(self, table: EbdTable, expected_result: List[EbdGraphEdge]) -> None:
        actual = get_all_edges(table)
        assert actual == expected_result

    @pytest.mark.parametrize(
        "table,expected_description",
        [
            pytest.param(
                table_e0003,
                "DiGraph with 6 nodes and 5 edges",
            ),
            pytest.param(
                table_e0015,
                "DiGraph with 22 nodes and 21 edges",
                # todo: check if result is ok
            ),
            pytest.param(
                table_e0025,
                "DiGraph with 10 nodes and 11 edges",
                # todo: check if result is ok
            ),
        ],
    )
    def test_table_to_digraph(self, table: EbdTable, expected_description: str):
        """
        Test the conversion pipeline. The results are stored in `unittests/output` for you to inspect the result
        manually. The test only checks if the svg can be built.
        """
        ebd_graph = convert_table_to_graph(table)
        assert str(ebd_graph.graph) == expected_description

        plantuml_code = convert_graph_to_plantuml(ebd_graph)
        with open(
            Path(__file__).parent / "output" / f"{ebd_graph.metadata.ebd_code}.puml", "w+", encoding="utf-8"
        ) as uml_file:
            uml_file.write(plantuml_code)
        svg_code = convert_plantuml_to_svg_kroki(plantuml_code, Kroki())  # Raises an error if conversion fails
        os.makedirs(Path(__file__).parent / "output", exist_ok=True)
        with open(
            Path(__file__).parent / "output" / f"{ebd_graph.metadata.ebd_code}.puml.svg", "w+", encoding="utf-8"
        ) as svg_file:
            svg_file.write(svg_code)

    @staticmethod
    def create_and_save_svg_test(ebd_graph: EbdGraph) -> str:
        """
        Creates the test svgs and saves them to the output folder.
        Also returns the kroki answer svg code as string to be stored for the mock request.
        """
        dot_code = convert_graph_to_dot(ebd_graph)
        kroki_client = InterceptedKrokiClient()
        svg_code = convert_dot_to_svg_kroki(
            dot_code, dot_to_svg_converter=kroki_client
        )  # Raises an error if conversion fails
        os.makedirs(Path(__file__).parent / "output", exist_ok=True)

        with open(
            Path(__file__).parent / "output" / f"{ebd_graph.metadata.ebd_code}.dot.svg",
            "w+",
            encoding="utf-8",
        ) as svg_file:
            svg_file.write(svg_code)

        svg_code_for_mock = kroki_client.intercepted_kroki_response_with_xml_comment
        assert svg_code_for_mock is not None
        return svg_code_for_mock

    @pytest.mark.parametrize(
        "table,expected_description",
        [
            pytest.param(
                table_e0003,
                "DiGraph with 6 nodes and 5 edges",
            ),
            pytest.param(
                table_e0015,
                "DiGraph with 22 nodes and 21 edges",
                # todo: check if result is ok
            ),
            pytest.param(
                table_e0025,
                "DiGraph with 10 nodes and 11 edges",
                # todo: check if result is ok
            ),
            pytest.param(
                table_e0401,
                "DiGraph with 23 nodes and 27 edges",
                # todo: check if result is ok
            ),
        ],
    )
    def test_table_to_digraph_dot_real_kroki_request(self, table: EbdTable, expected_description: str) -> None:
        """
        Test the conversion pipeline. The results are stored in `unittests/output` for you to inspect the result
        manually. The test only checks if the svg can be built.
        This test is disabled by default. To enable it, set `enable_request_to_kroki` to True.
        This will also update the mock files in `test_files` with the new responses from kroki.
        """
        enable_request_to_kroki = False  # Set to True to enable the request to kroki and to also update the mock file
        if not enable_request_to_kroki:
            pytest.skip("Disable automatic recreation on test runs")
        ebd_graph = convert_table_to_graph(table)
        assert str(ebd_graph.graph) == expected_description

        svg_code_for_mock = self.create_and_save_svg_test(ebd_graph)
        file_name_test_files = (
            Path(__file__).parent / "test_files" / f"{ebd_graph.metadata.ebd_code}_kroki_response.dot.svg"
        )
        with open(file_name_test_files, "w", encoding="utf-8") as ebd_svg:
            ebd_svg.write(svg_code_for_mock)

    @pytest.mark.parametrize(
        "table,expected_description",
        [
            pytest.param(
                table_e0003,
                "DiGraph with 6 nodes and 5 edges",
            ),
            pytest.param(
                table_e0015,
                "DiGraph with 22 nodes and 21 edges",
                # todo: check if result is ok
            ),
            pytest.param(
                table_e0025,
                "DiGraph with 10 nodes and 11 edges",
                # todo: check if result is ok
            ),
            pytest.param(
                table_e0401,
                "DiGraph with 23 nodes and 27 edges",
                # todo: check if result is ok
            ),
        ],
    )
    def test_table_to_digraph_dot_with_mock(self, table: EbdTable, expected_description: str, requests_mock) -> None:
        """
        Test the conversion pipeline. The results are stored in `unittests/output` for you to inspect the result
        manually. The test only checks if the svg can be built.
        This test uses a mock to avoid the request to kroki. The mock is stored in `test_files`.
        """
        ebd_graph = convert_table_to_graph(table)
        assert str(ebd_graph.graph) == expected_description
        with open(
            Path(__file__).parent / "test_files" / f"{ebd_graph.metadata.ebd_code}_kroki_response.dot.svg",
            "r",
            encoding="utf-8",
        ) as infile:
            kroki_response_string: str = infile.read()
        requests_mock.post("http://localhost:8125/", text=kroki_response_string)
        self.create_and_save_svg_test(ebd_graph)

    @staticmethod
    def create_and_save_watermark_and_background_svg(add_background: bool) -> str:
        """
        Creates the test svgs and saves them to the output folder.
        Also returns the kroki answer svg code as string to be stored for the mock request.
        """
        ebd_graph = convert_table_to_graph(table_e0003)
        dot_code = convert_graph_to_dot(ebd_graph)
        kroki_client = InterceptedKrokiClient()
        svg_code = convert_dot_to_svg_kroki(
            dot_code, add_watermark=False, add_background=False, dot_to_svg_converter=kroki_client
        )  # Raises an error if conversion fails
        os.makedirs(Path(__file__).parent / "output", exist_ok=True)

        with open(
            Path(__file__).parent / "output" / f"{ebd_graph.metadata.ebd_code}_without_watermark.dot.svg",
            "w+",
            encoding="utf-8",
        ) as svg_file:
            svg_file.write(svg_code)

        svg_code_with_watermark = convert_dot_to_svg_kroki(
            dot_code, add_watermark=True, add_background=add_background, dot_to_svg_converter=kroki_client
        )  # Raises an error if conversion fails

        file_path2 = (
            Path(__file__).parent
            / "output"
            / f"{ebd_graph.metadata.ebd_code}_with_watermark_background_is_{add_background}.dot.svg"
        )
        with open(file_path2, "w", encoding="utf-8") as ebd_svg:
            ebd_svg.write(svg_code_with_watermark)

        svg_code_for_mock = kroki_client.intercepted_kroki_response_with_xml_comment
        assert svg_code_for_mock is not None
        return svg_code_for_mock

    @pytest.mark.parametrize(
        "add_background",
        [
            pytest.param(
                True,
            ),
            pytest.param(
                False,
            ),
        ],
    )
    def test_table_to_digraph_dot_with_watermark_real_kroki_request(self, add_background: bool):
        """
        Test the combination of background and watermark addition to the svg. The results are stored in
        `unittests/output` for you to inspect the result manually.
        This test is disabled by default. To enable it, set `enable_request_to_kroki` to True.
        This will also update the mock file in `test_files` with the new response from kroki.
        """
        enable_request_to_kroki = False  # Set to True to enable the request to kroki and to also update the mock file
        if not enable_request_to_kroki:
            pytest.skip("Disable automatic recreation on test runs")
        svg_code_for_mock = self.create_and_save_watermark_and_background_svg(add_background)

        file_name_test_files = Path(__file__).parent / "test_files" / "E_0003_kroki_response.dot.svg"
        with open(file_name_test_files, "w", encoding="utf-8") as ebd_svg:
            ebd_svg.write(svg_code_for_mock)

    @pytest.mark.parametrize(
        "add_background",
        [
            pytest.param(
                True,
            ),
            pytest.param(
                False,
            ),
        ],
    )
    def test_table_to_digraph_dot_with_watermark_with_mock(self, add_background: bool, requests_mock) -> None:
        """
        Test the combination of background and watermark addition to the svg. The results are stored in
        `unittests/output` for you to inspect the result manually.
        This test uses a mock to avoid the request to kroki. The mock is stored in `test_files`.
        """
        with open(
            Path(__file__).parent / "test_files" / "E_0003_kroki_response.dot.svg", "r", encoding="utf-8"
        ) as infile:
            kroki_response_string: str = infile.read()
        requests_mock.post("http://localhost:8125/", text=kroki_response_string)
        self.create_and_save_watermark_and_background_svg(add_background)

    def test_table_to_digraph_dot_with_background(self, requests_mock) -> None:
        """
        Test the addition of a background in 'HF white' to the svg. The results are stored in
        `unittests/output` for you to inspect the result manually.
        This test uses a mock to avoid the request to kroki. The mock is stored in `test_files`.
        """
        with open(
            Path(__file__).parent / "test_files" / "E_0003_kroki_response.dot.svg", "r", encoding="utf-8"
        ) as infile:
            kroki_response_string: str = infile.read()
        requests_mock.post("http://localhost:8125/", text=kroki_response_string)
        ebd_graph = convert_table_to_graph(table_e0003)
        dot_code = convert_graph_to_dot(ebd_graph)
        kroki_client = InterceptedKrokiClient()
        svg_code = convert_dot_to_svg_kroki(
            dot_code, add_watermark=False, add_background=False, dot_to_svg_converter=kroki_client
        )  # Raises an error if conversion fails
        assert kroki_client.intercepted_kroki_response is not None
        os.makedirs(Path(__file__).parent / "output", exist_ok=True)

        with open(
            Path(__file__).parent / "output" / f"{ebd_graph.metadata.ebd_code}_without_watermark.dot.svg",
            "w+",
            encoding="utf-8",
        ) as svg_file:
            svg_file.write(svg_code)

        svg_code = convert_dot_to_svg_kroki(
            dot_code, add_watermark=False, add_background=True, dot_to_svg_converter=Kroki()
        )  # Raises an error if conversion fails

        file_path2 = Path(__file__).parent / "output" / f"{ebd_graph.metadata.ebd_code}_with_background.dot.svg"
        with open(file_path2, "w", encoding="utf-8") as ebd_svg:
            ebd_svg.write(svg_code)

    def test_table_e0401_too_complex_for_plantuml(self) -> None:
        """
        Test the conversion pipeline for E_0401. In this case the plantuml conversion should fail because the graph is
        too complex for this implementation.
        """
        with pytest.raises(GraphTooComplexForPlantumlError) as exc:
            _ = convert_graph_to_plantuml(convert_table_to_graph(table_e0401))
        assert "graph is too complex" in str(exc.value)

    @pytest.mark.parametrize(
        "table,expected_result",
        [
            pytest.param(
                table_e0003,
                EbdGraph(
                    metadata=EbdGraphMetaData(
                        ebd_code=table_e0003.metadata.ebd_code,
                        chapter=table_e0003.metadata.chapter,
                        section=table_e0003.metadata.section,
                        ebd_name=table_e0003.metadata.ebd_name,
                        role=table_e0003.metadata.role,
                    ),
                    graph=DiGraph(),
                ),
                id="E0003 (easy)",
            ),
            pytest.param(
                table_e0025,
                EbdGraph(
                    metadata=EbdGraphMetaData(
                        ebd_code=table_e0025.metadata.ebd_code,
                        chapter=table_e0025.metadata.chapter,
                        section=table_e0025.metadata.section,
                        ebd_name=table_e0025.metadata.ebd_name,
                        role=table_e0025.metadata.role,
                    ),
                    graph=DiGraph(),
                ),
                id="E0025 (easy-medium)",
            ),
            pytest.param(
                table_e0015,
                EbdGraph(
                    metadata=EbdGraphMetaData(
                        ebd_code=table_e0015.metadata.ebd_code,
                        chapter=table_e0015.metadata.chapter,
                        section=table_e0015.metadata.section,
                        ebd_name=table_e0015.metadata.ebd_name,
                        role=table_e0015.metadata.role,
                    ),
                    graph=DiGraph(),
                ),
                id="E0015 (medium)",
            ),
            pytest.param(
                table_e0401,
                EbdGraph(
                    metadata=EbdGraphMetaData(
                        ebd_code=table_e0401.metadata.ebd_code,
                        chapter=table_e0401.metadata.chapter,
                        section=table_e0401.metadata.section,
                        ebd_name=table_e0401.metadata.ebd_name,
                        role=table_e0401.metadata.role,
                    ),
                    graph=DiGraph(),
                ),
                id="E0401 (hard)",
            ),  # hard (because it's not a tree but only a directed graph)
            # todo: add E_0462
        ],
    )
    def test_table_to_graph(self, table: EbdTable, expected_result: EbdGraph) -> None:
        actual = convert_table_to_graph(table)
        pytest.skip("todo @leon - wird später in den examples.py ergänzt")
        assert actual == expected_result
