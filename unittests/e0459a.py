"""
Contains the raw data for E_0459 in the form of an EbdTable. Modified to test an error
"""

from rebdhuhn.models import EbdCheckResult, EbdTable, EbdTableMetaData, EbdTableRow, EbdTableSubRow

table_e0459a = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0459",
        chapter="GPKE",
        section="6.7.4: AD: Netznutzungsabrechnung",
        ebd_name="E_0459_Prüfen, ob Antwort auf Stornierung erforderlich",
        role="LF",
    ),
    rows=[
        EbdTableRow(
            step_number="1",
            description="Ist die zu stornierende Rechnung beim Empfänger bekannt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A01",
                    note="Die zu stornierende Rechnung ist nicht vorhanden.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="2"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="2",
            description="Wurde die zu stornierende Rechnung bereits storniert?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A02",
                    note="Die zu stornierende Rechnung wurde bereits storniert.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="3"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="3",
            description="Ist der Rechnungstyp der Stornorechnung identisch mit dem Rechnungstyp der ursprünglichen Rechnung?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A03",
                    note="Der Rechnungstyp der Stornorechnung ist nicht identisch mit dem Rechnungstyp der ursprünglichen Rechnung.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="4"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="4",
            description="Ist der Abrechnungszeitraum bzw. das Ausführungsdatum der Stornorechnung identisch mit dem Abrechnungszeitraum bzw. dem Ausführungsdatum der ursprünglichen Rechnung?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A04",
                    note="Der Abrechnungszeitraum bzw. des Ausführungsdatum der Stornorechnung ist nicht identisch mit dem Abrechnungszeitraum bzw. dem Ausführungsdatum der ursprünglichen Rechnung.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="5"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="5",
            description="Entsprechen die Beträge der Stornorechnung den Beträgen der ursprünglichen Rechnung?\n\nHinweis: Alle MOA-Segmente im Summenteil müssen unter Nutzung der Absolutbetragfunktion übereinstimmen.",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A05",
                    note="Mindestens ein Betrag der Stornorechnung ist nicht identisch mit dem Betrag der ursprünglichen Rechnung.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="6"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="6",
            description="Ist ein zuvor nicht spezifizierter Fehler aufgetreten?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A99",
                    note="Ablehnung Sonstiges\nHinweis: Das identifizierte Problem ist in der Antwort zu beschreiben/benennen. \nNutzungsmöglichkeit Ende: 01.10.2024 00:00 Uhr",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="7"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="7",
            description="Wurde der ursprünglichen Rechnung zugestimmt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="Ende"),
                    result_code=None,
                    note=None,
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="8"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="8",
            description="Wurde die ursprüngliche Rechnung abgelehnt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="Ende"),
                    result_code=None,
                    note="Hinweis: \nWurde die ursprüngliche Rechnung mit einem Nichtzahlungsavis abgelehnt, dann ist auf die Stornorechnung keine Antwort zu senden",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="Ende"),
                    result_code=None,
                    note="Hinweis: \nWurde die ursprüngliche Rechnung noch nicht beantwortet, weder mit einem Zahlungsavis noch mit einem Nichtzahlungsavis, dann ist weder auf die Rechnung noch auf die Stornorechnung eine Antwort zu senden.",
                ),
            ],
            use_cases=None,
        ),
    ],
    multi_step_instructions=None,
)
