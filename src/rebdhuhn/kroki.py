"""
we use kroki.io (hosted via docker at http://localhost:8125/) to convert dot code to SVG
"""

from typing import Protocol

import requests


# pylint:disable=too-few-public-methods
class DotToSvgConverter(Protocol):
    """
    a class that can convert dot to svg
    """

    def convert_dot_to_svg(self, dot_code: str) -> str:
        """
        convert the given dot to svg
        """


class PlantUmlToSvgConverter(Protocol):
    """
    a class that can convert plantuml to svg
    """

    def convert_plantuml_to_svg(self, plantuml_code: str) -> str:
        """
        convert the given plantuml code to svg
        """


# pylint:disable=too-few-public-methods
class Kroki:
    """
    A wrapper around any kroki request
    """

    def __init__(self, kroki_host: str = "http://localhost:8125") -> None:
        """
        initialize by providing the kroki host (e.g. https://kroki.io or http://localhost:8125...)
        """
        if not kroki_host:
            raise ValueError("kroki_host must be provided")
        self._host = kroki_host

    def convert_dot_to_svg(self, dot_code: str) -> str:
        """
        returns the svg code as str
        """
        url = self._host
        answer = requests.post(
            url,
            json={"diagram_source": dot_code, "diagram_type": "graphviz", "output_format": "svg"},
            timeout=5,
        )
        if answer.status_code != 200:
            raise ValueError(
                f"Error while converting dot to svg: {answer.status_code}: {requests.codes[answer.status_code]}. "
                f"{answer.text}"
            )
        return answer.text

    def convert_plantuml_to_svg(self, plantuml_code: str) -> str:
        """
        returns the svg code as str
        """
        url = self._host
        answer = requests.post(
            url,
            json={"diagram_source": plantuml_code, "diagram_type": "plantuml", "output_format": "svg"},
            timeout=5,
        )
        if answer.status_code != 200:
            raise ValueError(
                f"Error while converting plantuml to svg: {answer.status_code}: {requests.codes[answer.status_code]}. "
                f"{answer.text}"
            )
        return answer.text
