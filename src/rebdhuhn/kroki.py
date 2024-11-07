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


class KrokiDotBadRequestError(Exception):
    """
    is raised, when kroki rejects our dot-to-svg request
    """

    def __init__(self, dot_code: str, response_body: str | None = None) -> None:
        self.dot_code = dot_code
        self.response_body = response_body

    def __str__(self) -> str:
        return f"BadRequest while creating svg: {self.response_body} / {self.dot_code}"


class KrokiPlantUmlBadRequestError(Exception):
    """
    is raised, when kroki rejects our puml-to-svg request
    """

    def __init__(self, plant_uml_code: str, response_body: str | None = None) -> None:
        self.plant_uml_code = plant_uml_code
        self.response_body = response_body

    def __str__(self) -> str:
        return f"BadRequest while creating svg: {self.response_body} / {self.plant_uml_code}"


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
            if answer.status_code == 400:
                raise KrokiDotBadRequestError(dot_code, answer.text)
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
            json={
                "diagram_source": plantuml_code,
                "diagram_type": "plantuml",
                "output_format": "svg",
            },
            timeout=5,
        )
        if answer.status_code != 200:
            if answer.status_code == 400:
                raise KrokiPlantUmlBadRequestError(plantuml_code, answer.text)
            raise ValueError(
                f"Error while converting plantuml to svg: {answer.status_code}: {requests.codes[answer.status_code]}. "
                f"{answer.text}"
            )
        return answer.text
