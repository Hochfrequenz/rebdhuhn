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

    def convert_to_svg(self, dot_code: str) -> str:
        """
        convert the given dot to svg
        """


# pylint:disable=too-few-public-methods
class Kroki:
    """
    A wrapper around any kroki request
    """

    def convert_to_svg(self, dot_code: str) -> str:
        """
        returns the svg code as str
        """
        url = "http://localhost:8125/"
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
