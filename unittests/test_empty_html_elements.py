"""
Graphviz rejects empty elements in HTML-like labels (e.g. `<B></B>`) with a syntax error, so kroki answers HTTP 400
and no SVG is produced. These tests make sure that empty metadata/text values never lead to such elements.
"""

import re

import pytest

from rebdhuhn import (
    EbdCheckResult,
    EbdTable,
    EbdTableMetaData,
    EbdTableRow,
    EbdTableSubRow,
    Kroki,
    convert_graph_to_dot,
    convert_table_to_graph,
)
from rebdhuhn.graphviz import convert_dot_to_svg_kroki
from rebdhuhn.models.ebd_table import MultiStepInstruction

#: matches an HTML-like element (inline formatting tags) that contains nothing but whitespace
_EMPTY_ELEMENT_REGEX = re.compile(r"<(B|I|U|FONT)\b[^>]*>\s*</\1>")


def _table(
    role: str = "ÜNB", chapter: str = "MaBiS", section: str = "7.1 Test", instruction: str | None = None
) -> EbdTable:
    multi_step_instructions = (
        None
        if instruction is None
        else [MultiStepInstruction(first_step_number_affected="1", instruction_text=instruction)]
    )
    return EbdTable(
        metadata=EbdTableMetaData(
            ebd_code="E_9999", chapter=chapter, section=section, ebd_name="E_9999_Test", role=role
        ),
        rows=[
            EbdTableRow(
                step_number="1",
                description="Ist das ein Test?",
                sub_rows=[
                    EbdTableSubRow(
                        check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                        result_code="A01",
                        note="Kein Test",
                    ),
                    EbdTableSubRow(
                        check_result=EbdCheckResult(result=True, subsequent_step_number="Ende"),
                        result_code=None,
                        note=None,
                    ),
                ],
            ),
        ],
        multi_step_instructions=multi_step_instructions,
    )


def _dot(table: EbdTable) -> str:
    return convert_graph_to_dot(convert_table_to_graph(table))


class TestEmptyHtmlElements:
    @pytest.mark.parametrize("role", ["", " ", " \t\n "])
    def test_empty_role_emits_no_empty_element(self, role: str) -> None:
        dot = _dot(_table(role=role))
        assert not _EMPTY_ELEMENT_REGEX.search(dot)
        assert "Prüfende Rolle" not in dot
        assert "<B>E_9999</B>" in dot

    def test_normal_role_is_rendered_bold(self) -> None:
        dot = _dot(_table(role="ÜNB"))
        assert "<FONT>Prüfende Rolle: <B>ÜNB</B></FONT>" in dot

    @pytest.mark.parametrize("chapter,section", [("", "7.1 Test"), ("MaBiS", ""), ("", ""), (" ", " ")])
    def test_empty_chapter_or_section_emits_no_empty_element(self, chapter: str, section: str) -> None:
        dot = _dot(_table(chapter=chapter, section=section))
        assert not _EMPTY_ELEMENT_REGEX.search(dot)

    @pytest.mark.parametrize("instruction", ["", "  "])
    def test_empty_multi_step_instruction_emits_no_empty_element(self, instruction: str) -> None:
        dot = _dot(_table(instruction=instruction))
        assert not _EMPTY_ELEMENT_REGEX.search(dot)

    def test_regex_detects_empties(self) -> None:
        assert _EMPTY_ELEMENT_REGEX.search("<FONT>x: <B></B></FONT>")
        assert _EMPTY_ELEMENT_REGEX.search('<B><FONT POINT-SIZE="18"> </FONT></B>')
        assert not _EMPTY_ELEMENT_REGEX.search("<B>x</B><BR/>")

    @pytest.mark.parametrize(
        "table",
        [
            _table(role=""),
            _table(chapter="", section=""),
            _table(instruction=""),
        ],
        ids=["empty-role", "empty-header", "empty-instruction"],
    )
    def test_kroki_renders_svg(self, kroki_client: Kroki, table: EbdTable) -> None:
        svg = convert_dot_to_svg_kroki(_dot(table), kroki_client)
        assert "<svg" in svg
