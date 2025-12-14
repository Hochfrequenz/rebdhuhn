# mypy: disable-error-code="no-untyped-def"
import json
import os
from pathlib import Path
from typing import List, Optional

import pytest
from lxml import etree
from networkx import DiGraph, empty_graph  # type:ignore[import-untyped]

from rebdhuhn import (
    DecisionNode,
    EbdCheckResult,
    EbdGraph,
    EbdGraphMetaData,
    EbdTable,
    EbdTableMetaData,
    EbdTableRow,
    EbdTableSubRow,
    EndNode,
    Kroki,
    OutcomeNode,
    convert_dot_to_svg_kroki,
    convert_graph_to_dot,
    convert_graph_to_plantuml,
    convert_plantuml_to_svg_kroki,
    convert_table_to_graph,
)
from rebdhuhn.graph_conversion import convert_empty_table_to_graph, get_all_edges, get_all_nodes
from rebdhuhn.models.ebd_graph import EbdGraphEdge, EbdGraphNode, StartNode, ToNoEdge, ToYesEdge
from rebdhuhn.models.errors import GraphTooComplexForPlantumlError
from unittests.examples import table_e0003, table_e0015, table_e0025, table_e0401

from .e0266 import table_e0266
from .e0267 import e_0267
from .e0462 import table_e0462
from .e0487 import table_e0487
from .table_with_transition_node import table_0594_partly


class InterceptedKrokiClient(Kroki):
    """
    a wrapper around the kroki client for testing purposes. This class makes it possible to access the kroki
    response. It also provides an alternative version of the kroki response that has a comment for documentation
    purposes.
    """

    def __init__(self, kroki_host: str = "http://localhost:8125") -> None:
        super().__init__(kroki_host=kroki_host)
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

    @pytest.mark.snapshot
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
    def test_table_to_digraph(self, table: EbdTable, expected_description: str, kroki_client: Kroki, snapshot):
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
        svg_code = convert_plantuml_to_svg_kroki(plantuml_code, kroki_client)  # Raises an error if conversion fails
        os.makedirs(Path(__file__).parent / "output", exist_ok=True)
        with open(
            Path(__file__).parent / "output" / f"{ebd_graph.metadata.ebd_code}.puml.svg", "w+", encoding="utf-8"
        ) as svg_file:
            svg_file.write(svg_code)
        assert svg_code == snapshot(name=f"test_table_to_digraph_{table.metadata.ebd_code}")

    @staticmethod
    def create_and_save_svg_test(ebd_graph: EbdGraph, kroki_host: str) -> str:
        """
        Creates the test svgs and saves them to the output folder.
        Also returns the kroki answer svg code as string to be stored for the mock request.
        """
        dot_code = convert_graph_to_dot(ebd_graph)
        intercepted_client = InterceptedKrokiClient(kroki_host=kroki_host)
        svg_code = convert_dot_to_svg_kroki(
            dot_code, dot_to_svg_converter=intercepted_client
        )  # Raises an error if conversion fails
        os.makedirs(Path(__file__).parent / "output", exist_ok=True)

        with open(
            Path(__file__).parent / "output" / f"{ebd_graph.metadata.ebd_code}.dot.svg",
            "w+",
            encoding="utf-8",
        ) as svg_file:
            svg_file.write(svg_code)

        svg_code_for_mock = intercepted_client.intercepted_kroki_response_with_xml_comment
        assert svg_code_for_mock is not None
        return svg_code_for_mock

    @pytest.mark.snapshot
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
            pytest.param(
                e_0267,
                "DiGraph with 20 nodes and 19 edges",
                # todo: check if result is ok
            ),
        ],
    )
    def test_table_to_digraph_dot_real_kroki_request(
        self, table: EbdTable, expected_description: str, kroki_client: Kroki, snapshot
    ) -> None:
        """
        Test the conversion pipeline. The results are stored in `unittests/output` for you to inspect the result
        manually. The test only checks if the svg can be built.
        This will also update the mock files in `test_files` with the new responses from kroki.
        """
        ebd_graph = convert_table_to_graph(table)
        assert str(ebd_graph.graph) == expected_description

        svg_code_for_mock = self.create_and_save_svg_test(ebd_graph, kroki_client._host)
        file_name_test_files = (
            Path(__file__).parent / "test_files" / f"{ebd_graph.metadata.ebd_code}_kroki_response.dot.svg"
        )
        with open(file_name_test_files, "w", encoding="utf-8") as ebd_svg:
            ebd_svg.write(svg_code_for_mock)
        assert svg_code_for_mock == snapshot(
            name=f"test_table_to_digraph_dot_real_kroki_request_{table.metadata.ebd_name}"
        )

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
            pytest.param(
                table_e0266,
                "DiGraph with 54 nodes and 68 edges",
                # todo: check if result is ok
            ),
            pytest.param(
                table_0594_partly,
                "DiGraph with 6 nodes and 6 edges",
                # Start
                # 1
                # 270
                # 2  3
                # 275 |
                # 4  /
                # 280
                # 5  6
                # A02 |
                #    A123
                # = 6 nodes + 6 edges
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
        kroki_response_path = (
            Path(__file__).parent / "test_files" / f"{ebd_graph.metadata.ebd_code}_kroki_response.dot.svg"
        )
        if not kroki_response_path.exists():
            pytest.skip("It's ok")
        with open(
            kroki_response_path,
            "r",
            encoding="utf-8",
        ) as infile:
            kroki_response_string: str = infile.read()
        requests_mock.post("http://localhost:8125/", text=kroki_response_string)
        self.create_and_save_svg_test(ebd_graph, "http://localhost:8125")

    @staticmethod
    def create_and_save_watermark_and_background_svg(add_background: bool, kroki_host: str) -> str:
        """
        Creates the test svgs and saves them to the output folder.
        Also returns the kroki answer svg code as string to be stored for the mock request.
        """
        ebd_graph = convert_table_to_graph(table_e0003)
        dot_code = convert_graph_to_dot(ebd_graph)
        intercepted_client = InterceptedKrokiClient(kroki_host=kroki_host)
        svg_code = convert_dot_to_svg_kroki(
            dot_code, add_watermark=False, add_background=False, dot_to_svg_converter=intercepted_client
        )  # Raises an error if conversion fails
        os.makedirs(Path(__file__).parent / "output", exist_ok=True)

        with open(
            Path(__file__).parent / "output" / f"{ebd_graph.metadata.ebd_code}_without_watermark.dot.svg",
            "w+",
            encoding="utf-8",
        ) as svg_file:
            svg_file.write(svg_code)

        svg_code_with_watermark = convert_dot_to_svg_kroki(
            dot_code, add_watermark=True, add_background=add_background, dot_to_svg_converter=intercepted_client
        )  # Raises an error if conversion fails

        file_path2 = (
            Path(__file__).parent
            / "output"
            / f"{ebd_graph.metadata.ebd_code}_with_watermark_background_is_{add_background}.dot.svg"
        )
        with open(file_path2, "w", encoding="utf-8") as ebd_svg:
            ebd_svg.write(svg_code_with_watermark)

        svg_code_for_mock = intercepted_client.intercepted_kroki_response_with_xml_comment
        assert svg_code_for_mock is not None
        return svg_code_for_mock

    @pytest.mark.snapshot
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
    def test_table_to_digraph_dot_with_watermark_real_kroki_request(
        self, add_background: bool, kroki_client: Kroki, snapshot
    ):
        """
        Test the combination of background and watermark addition to the svg. The results are stored in
        `unittests/output` for you to inspect the result manually.
        This will also update the mock file in `test_files` with the new response from kroki.
        """
        svg_code_for_mock = self.create_and_save_watermark_and_background_svg(add_background, kroki_client._host)

        file_name_test_files = Path(__file__).parent / "test_files" / "E_0003_kroki_response.dot.svg"
        with open(file_name_test_files, "w", encoding="utf-8") as ebd_svg:
            ebd_svg.write(svg_code_for_mock)
        assert svg_code_for_mock == snapshot(
            name=f"test_table_to_digraph_dot_with_watermark_real_kroki_request_background_{add_background}"
        )

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
        self.create_and_save_watermark_and_background_svg(add_background, "http://localhost:8125")

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

    @pytest.mark.snapshot
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
            pytest.param(
                table_e0487,
                EbdGraph(
                    metadata=EbdGraphMetaData(
                        ebd_code=table_e0487.metadata.ebd_code,
                        chapter=table_e0487.metadata.chapter,
                        section=table_e0487.metadata.section,
                        ebd_name=table_e0487.metadata.ebd_name,
                        role=table_e0487.metadata.role,
                    ),
                    graph=DiGraph(),
                ),
                id="E0487",
            ),
            pytest.param(
                table_0594_partly,
                EbdGraph(
                    metadata=EbdGraphMetaData(
                        ebd_code=table_0594_partly.metadata.ebd_code,
                        chapter=table_0594_partly.metadata.chapter,
                        section=table_0594_partly.metadata.section,
                        ebd_name=table_0594_partly.metadata.ebd_name,
                        role=table_0594_partly.metadata.role,
                    ),
                    graph=DiGraph(),
                ),
                id="E_0594 steps 270 to 280 including transition node",
            ),
            # todo: add E_0462
        ],
    )
    def test_table_to_graph(self, table: EbdTable, expected_result: EbdGraph) -> None:
        _ = convert_table_to_graph(table)

    @pytest.mark.snapshot
    @pytest.mark.parametrize(
        "metadata_only",
        [
            pytest.param(
                EbdTableMetaData(
                    chapter="GPKE",
                    ebd_code="E_0590",
                    ebd_name="E_0590_Bestellung zur Stammdatenänderung prüfen",
                    remark="Derzeit ist für diese Entscheidung kein Entscheidungsbaum notwendig, da keine Antwort gegeben wird.",
                    role="N/A",
                    section="6.24.3: AD: Bestellung zur Stammdatenänderung an LF (verantwortlich)",
                )
            )
        ],
    )
    def test_empty_table_to_graph(self, metadata_only: EbdTableMetaData, kroki_client: Kroki, snapshot) -> None:
        empty_graph = convert_table_to_graph(EbdTable(metadata=metadata_only, rows=[]))
        dot_code = convert_graph_to_dot(empty_graph)
        svg_code = kroki_client.convert_dot_to_svg(dot_code)
        os.makedirs(Path(__file__).parent / "output", exist_ok=True)
        with open(
            Path(__file__).parent / "output" / f"empty_{empty_graph.metadata.ebd_code}.dot.svg", "w+", encoding="utf-8"
        ) as svg_file:
            svg_file.write(svg_code)
        assert svg_code == snapshot(name=f"empty_{empty_graph.metadata.ebd_code}")

    def test_empty_table_with_empty_remark_to_graph(self, kroki_client: Kroki) -> None:
        """
        Test that an empty EBD table with an empty remark string generates valid DOT code.
        This is a regression test for the bug where empty remark generated <FONT></FONT>
        which Kroki/Graphviz rejected as invalid.
        """
        json_path = Path(__file__).parent / "test_files" / "e0452_empty_remark.json"
        with open(json_path, "r", encoding="utf-8") as f:
            table_json = json.load(f)
        table = EbdTable.model_validate(table_json)

        assert table.metadata.ebd_code == "E_0452"
        assert table.metadata.remark == ""  # Empty string, not None

        graph = convert_table_to_graph(table)
        dot_code = convert_graph_to_dot(graph)

        # Verify no empty FONT tags in the output
        assert "<FONT></FONT>" not in dot_code

        # Verify it can be converted to SVG without error
        svg_code = kroki_client.convert_dot_to_svg(dot_code)
        assert svg_code is not None
        assert "<svg" in svg_code

    @pytest.mark.snapshot
    @pytest.mark.parametrize(
        "table",
        [
            pytest.param(table_e0487, id="E_0487"),
            pytest.param(table_0594_partly, id="E_0594-partly"),
        ],
    )
    def test_table_to_dot_to_svg(self, table: EbdTable, kroki_client: Kroki, snapshot) -> None:
        graph = convert_table_to_graph(table)
        dot_code = convert_graph_to_dot(graph)
        svg_code = kroki_client.convert_dot_to_svg(dot_code)
        os.makedirs(Path(__file__).parent / "output", exist_ok=True)
        with open(
            Path(__file__).parent / "output" / f"table_dot_svg_{graph.metadata.ebd_code}.svg", "w+", encoding="utf-8"
        ) as svg_file:
            svg_file.write(svg_code)
        assert dot_code == snapshot(name=f"table_dot_svg_{graph.metadata.ebd_code}")


class TestEbdCrossReferenceLinks:
    """Tests for EBD cross-reference link rendering in DOT output."""

    def test_ebd_link_template_renders_styled_link(self) -> None:
        """Verify that ebd_link_template parameter renders EBD references with styling and href."""
        table_with_ebd_reference = EbdTable(
            metadata=EbdTableMetaData(
                ebd_code="E_TEST",
                chapter="Test Chapter",
                section="Test Section",
                ebd_name="E_TEST_Test",
                role="Test",
            ),
            rows=[
                EbdTableRow(
                    step_number="1",
                    description="Is this a test?",
                    sub_rows=[
                        EbdTableSubRow(
                            check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                            result_code=None,
                            note="EBD E_0621_Prüfen, ob Anfrage zur Beendigung der Zuordnung erforderlich",
                        ),
                        EbdTableSubRow(
                            check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                            result_code="A01",
                            note="Cluster: Ablehnung",
                        ),
                    ],
                ),
            ],
        )

        graph = convert_table_to_graph(table_with_ebd_reference)

        # Without template - should have plain text "EBD E_0621"
        dot_without_links = convert_graph_to_dot(graph)
        assert "EBD E_0621" in dot_without_links
        assert 'href="?ebd=' not in dot_without_links

        # With template - should have styled text and href attribute
        dot_with_links = convert_graph_to_dot(graph, ebd_link_template="?ebd={ebd_code}")
        assert '<FONT COLOR="#0066cc"><U>EBD E_0621</U></FONT>' in dot_with_links
        assert 'href="?ebd=E_0621"' in dot_with_links

    def test_ebd_link_template_with_full_url(self) -> None:
        """Verify that full URL templates work correctly."""
        table_with_ebd_reference = EbdTable(
            metadata=EbdTableMetaData(
                ebd_code="E_TEST",
                chapter="Test Chapter",
                section="Test Section",
                ebd_name="E_TEST_Test",
                role="Test",
            ),
            rows=[
                EbdTableRow(
                    step_number="1",
                    description="Is this a test?",
                    sub_rows=[
                        EbdTableSubRow(
                            check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                            result_code=None,
                            note="EBD E_0621_Prüfen",
                        ),
                        EbdTableSubRow(
                            check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                            result_code="A01",
                            note="Cluster: Ablehnung",
                        ),
                    ],
                ),
            ],
        )

        graph = convert_table_to_graph(table_with_ebd_reference)
        dot_code = convert_graph_to_dot(graph, ebd_link_template="https://example.com/ebd/{ebd_code}")
        assert '<FONT COLOR="#0066cc"><U>EBD E_0621</U></FONT>' in dot_code
        assert 'href="https://example.com/ebd/E_0621"' in dot_code

    def test_multiple_ebd_references_all_styled(self) -> None:
        """Verify that multiple EBD references in one note all get styled."""
        table_with_multiple_refs = EbdTable(
            metadata=EbdTableMetaData(
                ebd_code="E_TEST",
                chapter="Test Chapter",
                section="Test Section",
                ebd_name="E_TEST_Test",
                role="Test",
            ),
            rows=[
                EbdTableRow(
                    step_number="1",
                    description="Is this a test?",
                    sub_rows=[
                        EbdTableSubRow(
                            check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                            result_code=None,
                            note="Siehe EBD E_0621 und EBD E_0622 für Details",
                        ),
                        EbdTableSubRow(
                            check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                            result_code="A01",
                            note="Cluster: Ablehnung",
                        ),
                    ],
                ),
            ],
        )

        graph = convert_table_to_graph(table_with_multiple_refs)
        dot_code = convert_graph_to_dot(graph, ebd_link_template="?ebd={ebd_code}")
        # Both references should be styled
        assert '<FONT COLOR="#0066cc"><U>EBD E_0621</U></FONT>' in dot_code
        assert '<FONT COLOR="#0066cc"><U>EBD E_0622</U></FONT>' in dot_code
        # Note: Node with multiple references won't have href (only single-ref nodes get href)

    def test_no_ebd_reference_no_link(self) -> None:
        """Verify that notes without EBD references are not affected."""
        graph = convert_table_to_graph(table_e0003)
        dot_code = convert_graph_to_dot(graph, ebd_link_template="?ebd={ebd_code}")

        # Should not have any styled links since table_e0003 has no EBD references
        assert 'href="?ebd=' not in dot_code
        assert "<U>EBD E_" not in dot_code

    def test_real_ebd_e0462_integration(self) -> None:
        """Integration test using real E_0462 data which contains EBD E_0402 cross-references."""
        # E_0462 has EBD E_0402 references in steps 23 and 24
        graph = convert_table_to_graph(table_e0462)

        # Verify the outcome nodes have ebd_references extracted
        outcome_nodes_with_refs: list[OutcomeNode] = []
        for node_key in graph.graph.nodes:
            node = graph.graph.nodes[node_key]["node"]
            if isinstance(node, OutcomeNode) and any(node.ebd_references):
                outcome_nodes_with_refs.append(node)

        assert len(outcome_nodes_with_refs) > 0, "Expected at least one OutcomeNode with ebd_references"
        assert any("E_0402" in refs for node in outcome_nodes_with_refs for refs in node.ebd_references)

        # Verify DOT output has styled links and href attributes
        dot_code = convert_graph_to_dot(graph, ebd_link_template="?ebd={ebd_code}")
        assert '<FONT COLOR="#0066cc"><U>EBD E_0402</U></FONT>' in dot_code
        assert 'href="?ebd=E_0402"' in dot_code


class TestEbdReferencesPropagation:
    """Tests for ebd_references propagation from EbdTableSubRow to OutcomeNode during graph conversion."""

    def test_ebd_references_propagates_to_outcome_node(self) -> None:
        """Verify that ebd_references from EbdTableSubRow note are available in the OutcomeNode after conversion."""
        table_with_ebd_reference = EbdTable(
            metadata=EbdTableMetaData(
                ebd_code="E_TEST",
                chapter="Test Chapter",
                section="Test Section",
                ebd_name="E_TEST_Test",
                role="Test",
            ),
            rows=[
                EbdTableRow(
                    step_number="1",
                    description="Is this a test?",
                    sub_rows=[
                        EbdTableSubRow(
                            check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                            result_code=None,
                            note="EBD E_0621_Prüfen, ob Anfrage zur Beendigung der Zuordnung erforderlich",
                        ),
                        EbdTableSubRow(
                            check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                            result_code="A01",
                            note="Cluster: Ablehnung",
                        ),
                    ],
                ),
            ],
        )

        # Verify sub_row has the reference extracted
        assert table_with_ebd_reference.rows[0].sub_rows[0].ebd_references == ["E_0621"]

        # Convert to graph
        graph = convert_table_to_graph(table_with_ebd_reference)

        # Find the outcome node with the EBD reference note
        outcome_node_with_ref: OutcomeNode | None = None
        for node_key in graph.graph.nodes:
            node = graph.graph.nodes[node_key]["node"]
            if isinstance(node, OutcomeNode) and node.note and "EBD E_0621" in node.note:
                outcome_node_with_ref = node
                break

        assert outcome_node_with_ref is not None, "OutcomeNode with EBD reference not found in graph"
        assert outcome_node_with_ref.ebd_references == ["E_0621"]

    def test_outcome_node_without_ebd_reference_has_empty_list(self) -> None:
        """Verify that OutcomeNode without EBD references has an empty list."""
        graph = convert_table_to_graph(table_e0003)

        # Find outcome nodes
        for node_key in graph.graph.nodes:
            node = graph.graph.nodes[node_key]["node"]
            if isinstance(node, OutcomeNode):
                assert not any(
                    node.ebd_references
                ), f"Expected empty list for {node.get_key()}, got {node.ebd_references}"
