# pylint:disable=line-too-long
"""
tests the utility functions
"""

import pytest

from rebdhuhn.utils import add_line_breaks


@pytest.mark.parametrize(
    "original, length, line_break_char, expected",
    [
        pytest.param("text shorter than 80 chars", 80, "\n", "text shorter than 80 chars"),
        pytest.param(
            "Die Köchin der Frau Grubach, seiner Zimmervermieterin, die ihm jeden Tag gegen acht Uhr früh das Frühstück brachte, kam diesmal nicht.",
            80,
            "\n",
            "Die Köchin der Frau Grubach, seiner Zimmervermieterin, die ihm jeden Tag gegen\nacht Uhr früh das Frühstück brachte, kam diesmal nicht.",
        ),
        pytest.param(
            "Er war schlank und doch fest gebaut, er trug ein anliegendes schwarzes Kleid, das, ähnlich den Reiseanzügen, mit verschiedenen Falten, Taschen, Schnallen, Knöpfen und einem Gürtel versehen war und infolgedessen, ohne daß man sich darüber klar wurde, wozu es dienen sollte, besonders praktisch erschien. »Wer sind Sie?« fragte K. und saß gleich halb aufrecht im Bett. Der Mann aber ging über die Frage hinweg, als müsse man seine Erscheinung hinnehmen, und sagte bloß seinerseits: »Sie haben geläutet?« »Anna soll mir das Frühstück bringen«, sagte K. und versuchte, zunächst stillschweigend, durch Aufmerksamkeit und Überlegung festzustellen, wer der Mann eigentlich war. Aber dieser setzte sich nicht allzulange seinen Blicken aus, sondern wandte sich zur Tür, die er ein wenig öffnete, um jemandem, der offenbar knapp hinter der Tür stand, zu sagen: »Er will, daß Anna ihm das Frühstück bringt.«",
            80,
            "<br/>",
            "Er war schlank und doch fest gebaut, er trug ein anliegendes schwarzes Kleid,<br/>das, ähnlich den Reiseanzügen, mit verschiedenen Falten, Taschen, Schnallen,<br/>Knöpfen und einem Gürtel versehen war und infolgedessen, ohne daß man sich<br/>darüber klar wurde, wozu es dienen sollte, besonders praktisch erschien. »Wer<br/>sind Sie?« fragte K. und saß gleich halb aufrecht im Bett. Der Mann aber ging<br/>über die Frage hinweg, als müsse man seine Erscheinung hinnehmen, und sagte<br/>bloß seinerseits: »Sie haben geläutet?« »Anna soll mir das Frühstück bringen«,<br/>sagte K. und versuchte, zunächst stillschweigend, durch Aufmerksamkeit und<br/>Überlegung festzustellen, wer der Mann eigentlich war. Aber dieser setzte sich<br/>nicht allzulange seinen Blicken aus, sondern wandte sich zur Tür, die er ein<br/>wenig öffnete, um jemandem, der offenbar knapp hinter der Tür stand, zu sagen:<br/>»Er will, daß Anna ihm das Frühstück bringt.«",
        ),
        pytest.param(
            "Der Mann aber ging über die Frage hinweg, als müsse man seine Erscheinung hinnehmen, und sagte bloß seinerseits:\n »Sie haben geläutet?« »Anna soll mir das Frühstück bringen«, sagte K. und versuchte, zunächst stillschweigend, durch Aufmerksamkeit und Überlegung festzustellen, wer der Mann eigentlich war.",
            80,
            "<br/>",
            "Der Mann aber ging über die Frage hinweg, als müsse man seine Erscheinung hinnehmen, und sagte bloß seinerseits:<br/>»Sie haben geläutet?« »Anna soll mir das Frühstück bringen«, sagte K. und<br/>versuchte, zunächst stillschweigend, durch Aufmerksamkeit und Überlegung<br/>festzustellen, wer der Mann eigentlich war.",
        ),
    ],
)
def test_add_line_breaks(original: str, length: int, line_break_char: str, expected: str) -> None:
    actual = add_line_breaks(original, max_line_length=length, line_sep=line_break_char)
    assert actual == expected
