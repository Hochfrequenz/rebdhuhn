"""
we use kroki.io to convert dot code to SVG
"""
import requests


class Kroki:
    """
    A wrapper around any kroki request
    """

    def convert_to_svg(self, dot_code: str) -> str:
        """
        returns the svg code as str
        """
        url = "https://kroki.io"
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
