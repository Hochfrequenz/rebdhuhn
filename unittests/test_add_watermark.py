"""
Tests for the add_watermark module, specifically the release info footer.
"""

from datetime import date

from lxml import etree

from rebdhuhn.add_watermark import add_release_info_footer
from rebdhuhn.models.ebd_table import EbdDocumentReleaseInformation

_MINIMAL_SVG = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"'
    ' version="1.1" width="1000pt" viewBox="0 0 1000 500" height="500pt">'
    "<g/>"
    "</svg>"
)


class TestAddReleaseInfoFooter:
    """Tests for add_release_info_footer in add_watermark.py."""

    def test_footer_contains_link_to_ebd_hochfrequenz(self) -> None:
        """The footer must wrap the version text in a hyperlink to ebd.hochfrequenz.de."""
        release_info = EbdDocumentReleaseInformation(
            version="4.2",
            release_date=date(2025, 12, 11),
            rebdhuhn_version=None,
            ebdamame_version=None,
        )
        svg_result = add_release_info_footer(_MINIMAL_SVG, release_info)
        root = etree.fromstring(svg_result.encode("utf-8"))

        # Find all <a> elements
        a_elements = root.findall(".//{http://www.w3.org/2000/svg}a") + root.findall(".//a")
        assert any(
            elem.attrib.get("href") == "https://ebd.hochfrequenz.de" for elem in a_elements
        ), "Footer must contain a hyperlink to https://ebd.hochfrequenz.de"

    def test_footer_link_text_is_not_underlined(self) -> None:
        """The footer text must not have an underline (text-decoration: none)."""
        release_info = EbdDocumentReleaseInformation(
            version="4.2",
            rebdhuhn_version=None,
            ebdamame_version=None,
        )
        svg_result = add_release_info_footer(_MINIMAL_SVG, release_info)
        root = etree.fromstring(svg_result.encode("utf-8"))

        text_elements = root.findall(".//{http://www.w3.org/2000/svg}text") + root.findall(".//text")
        assert any(
            elem.attrib.get("text-decoration") == "none" for elem in text_elements
        ), "Footer text must have text-decoration='none' to avoid an ugly underline"

    def test_footer_returns_unchanged_svg_when_version_is_missing(self) -> None:
        """If the release info has no version, the SVG should be returned unchanged."""
        release_info = EbdDocumentReleaseInformation(
            version="",
            rebdhuhn_version=None,
            ebdamame_version=None,
        )
        svg_result = add_release_info_footer(_MINIMAL_SVG, release_info)
        assert svg_result == _MINIMAL_SVG
