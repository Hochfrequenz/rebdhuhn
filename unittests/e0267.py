"""
Contains the raw data for E_0529 in the form of an EbdTable.
"""

from rebdhuhn.models import EbdCheckResult, EbdTable, EbdTableMetaData, EbdTableRow, EbdTableSubRow

e_0267 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0267",
        chapter="WiM Strom",
        section="8.27.4: AD: Abrechnung einer für den ESA erbrachten Leistung",
        role="ESA",
        ebd_name="E_0267_Prüfen, ob Antwort auf Stornierung erforderlich",
        remark=None,
    ),
    rows=[
        EbdTableRow(
            step_number="10",
            description="Ist die zu stornierende Rechnung beim Empfänger bekannt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A01",
                    note="Die zu stornierende Rechnung ist nicht vorhanden.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="15"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="15",
            description="Liegt vom Rechnungssteller die in dieser Rechnung verwendete Rechnungsnummer bereits vor?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A06",
                    note="Rechnungsnummer wurde bereits verwendet.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="20"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="20",
            description="Wurde die zu stornierende Rechnung bereits storniert?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A02",
                    note="Die zu stornierende Rechnung wurde bereits storniert.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="30"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="30",
            description="Ist der Rechnungstyp der Stornorechnung identisch mit dem Rechnungstyp der ursprünglichen Rechnung?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A03",
                    note="Der Rechnungstyp der Stornorechnung ist nicht identisch mit dem Rechnungstyp der ursprünglichen Rechnung.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="40"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="40",
            description="Ist der Abrechnungszeitraum bzw. das Ausführungsdatum der Stornorechnung identisch mit dem Abrechnungszeitraum bzw. dem Ausführungsdatum der ursprünglichen Rechnung?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A04",
                    note="Der Abrechnungszeitraum bzw. das Ausführungsdatum der Stornorechnung ist nicht identisch mit dem Abrechnungszeitraum bzw. dem Ausführungsdatum der ursprünglichen Rechnung.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="50"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="50",
            description="Entsprechen die Beträge der Stornorechnung den Beträgen der ursprünglichen Rechnung?\n\nHinweis: Alle MOA-Segmente im Summenteil müssen unter Nutzung der Absolutbetragfunktion übereinstimmen.",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A05",
                    note="Mindestens ein Betrag der Stornorechnung ist nicht identisch mit dem Betrag der ursprünglichen Rechnung.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="60"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="60",
            description="Ist ein zuvor nicht spezifizierter Fehler aufgetreten?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A99",
                    note="Ablehnung Sonstiges\n\nHinweis: Das identifizierte Problem ist in der Antwort zu beschreiben/benennen. \nNutzungsmöglichkeit Ende: 01.04.2026 00:00 Uhr",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="70"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="70",
            description="Wurde der ursprünglichen Rechnung zugestimmt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="Ende"),
                    result_code=None,
                    note="Stornorechnung zustimmen und im Zahlungslauf berücksichtigen",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="80"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="80",
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
