"""
Contains the raw data for E_0529 in the form of an EbdTable.
"""

from rebdhuhn.models import EbdCheckResult, EbdTable, EbdTableMetaData, EbdTableRow, EbdTableSubRow

e_0529 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0529",
        chapter="GPKE",
        sub_chapter="6.36.6: AD Bestellung einer Konfiguration vom NB an MSB",
        role="MSB",
    ),
    rows=[
        EbdTableRow(
            step_number="10",
            description="Konnte die Konfiguration an allen Lokationen umgesetzt werden?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A01",
                    note="Cluster: Ablehnung\nDie Konfiguration konnte nicht an allen Lokationen umgesetzt werden",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="20"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="20",
            description="Ist ein zuvor nicht spezifizierter Fehler aufgetreten?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A99",
                    note="Cluster: Ablehnung\nSonstiges\nHinweis: Das identifizierte Problem ist in der Antwort zu beschreiben/benennen.\nNutzungsmöglichkeit Ende: 01.10.2024 00:00 Uhr",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A02",
                    note="Cluster: Zustimmung\nKonfiguration konnte an allen Lokationen umgesetzt werden",
                ),
            ],
            use_cases=None,
        ),
    ],
    multi_step_instructions=None,
)
