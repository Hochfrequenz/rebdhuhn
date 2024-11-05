"""
Contains the raw data for E_0454 in the form of an EbdTable.
"""

from rebdhuhn.models import EbdCheckResult, EbdTable, EbdTableMetaData, EbdTableRow, EbdTableSubRow

table_e0454 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0454",
        chapter="GPKE",
        section="6.27.2: AD: Information über die Zuordnung einer Marktlokation zur Datenaggregation durch den ÜNB",
        role="ÜNB",
    ),
    rows=[
        EbdTableRow(
            step_number="1",
            description="Sind Fehler im Rahmen der AHB-Prüfungen in den Stammdaten des NB festgestellt worden?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A97",
                    note="Die Stammdaten des NB genügen nicht den AHB-Vorgaben.\nHinweis: Diese Prüfung ist auf alle Stammdaten des NB anzuwenden. Es sind die Fehlerorte aller dabei festgestellten Fehler in der Antwort zu benennen.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="2"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="2",
            description="Wechselt für die Marktlokation die Aggregationsverantwortung vom ÜNB zum NB?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="3"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="4"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="3",
            description="Ist die Marktlokation bzw. Tranche zu dem im Vorgang unter „Verwendung der Daten bis“ genannten Zeitpunkt dem ÜNB zur Datenaggregation zugeordnet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A02",
                    note="Die Marktlokation bzw. Tranche ist zum genannten Zeitpunkt nicht dem ÜNB zur Aggregation zugeordnet",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="9"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="4",
            description="Liegt eine Stilllegung der Marktlokation vor bzw. wurde die Marktlokation über das Netz des NB in ein anderes Übertragungsnetz eingebunden?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="5"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="7"),
                    result_code=None,
                    note="Hinweis: Es liegt eine Änderung des Bilanzierungsverfahrens von Viertelstundenwerte auf Profile vor und die Aggregationsverantwortung liegt beim NB",
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="5",
            description="Ist die Marktlokation bzw. Tranche zu dem im Vorgang unter „Verwendung der Daten bis“ genannten Zeitpunkt dem ÜNB bekannt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A03",
                    note="Die Marktlokation bzw. Tranche ist zu dem im Vorgang unter „Verwendung der Daten bis“ genannten Zeitpunkt dem ÜNB nicht bekannt",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="6"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="6",
            description='Liegt das im Vorgang unter "Verwendung der Daten bis" genannte Datum zum Zeitpunkt des Empfangs des Vorgangs beim ÜNB vor dem Beginn des Vormonats, in dem der Vorgang beim ÜNB eingeht?',
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A08",
                    note='Das Datum „Verwendung der Daten bis“ des Vor-gangs liegt vor dem Beginn des Vormonats, in dem der Vorgang beim ÜNB eingeht. \nHinweis: Eine Korrektur des Datums "Verwendung der Daten bis" auf den nächstmöglichen Zeitpunkt ist erforderlich.',
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="11"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="7",
            description="Ist die Marktlokation bzw. Tranche zu dem im Vorgang unter „Verwendung der Daten bis“ genannten Zeitpunkt dem NB zur Datenaggregation zugeordnet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A04",
                    note="Die Marktlokation bzw. Tranche ist zum genannten Zeitpunkt nicht dem NB zur Aggregation zugeordnet",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="8"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="8",
            description="Liegt die Marktlokation bzw. Tranche zu dem im Vorgang unter „Verwendung der Daten bis“ genannten Zeitpunkt dem ÜNB mit dem Bilanzierungsverfahren Bilanzierung auf Basis von Viertelstundenwerten vor?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A05",
                    note="Die Marktlokation bzw. Tranche liegt zum genannten Zeitpunkt dem ÜNB nicht mit dem Bilanzierungsverfahren Bilanzierung auf Basis von Viertelstundenwerten vor",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="9"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="9",
            description='Liegt das im Vorgang unter "Verwendung der Daten bis" genannte Datum zum Zeitpunkt des Empfangs des Vorgangs beim ÜNB vor dem Beginn des Monats, in dem der Vorgang beim ÜNB eingeht?',
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A09",
                    note='Das Datum „Verwendung der Daten bis“ des Vorgangs liegt vor dem Beginn des Monats, in dem der Vorgang beim ÜNB eingeht. \nHinweis: Eine Korrektur des Datums "Verwendung der Daten bis" auf den nächstmöglichen Zeitpunkt ist erforderlich.',
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="10"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="10",
            description='Ist das im Vorgang unter "Verwendung der Daten bis" genannte Datum ein anderes Datum, als der Erste eines Monats?',
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A10",
                    note='Das Datum "Verwendung der Daten bis" ist nicht der Erste eines Monats. \nHinweis: Eine Korrektur des Datums "Verwendung der Daten bis" auf den Ersten eines Monats ist erforderlich.',
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="11"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="11",
            description="Ist die Marktlokation bzw. Tranche zu dem im Vorgang unter „Verwendung der Daten bis“ genannten Zeitpunkt dem im Vorgang angegebenen Netzbetreiber zugeordnet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A06",
                    note="Angegebener Netzbetreiber ist zum angegebenen Zeitpunkt der Marktlokation bzw. Tranche nicht zugeordnet.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="12"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="12",
            description="Ist der im Vorgang genannte LF identisch mit dem Absender der Nachricht?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A07",
                    note="LF im Vorgang weicht vom Absender ab",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A01",
                    note="Stammdaten wurden widerspruchsfrei übernommen.",
                ),
            ],
            use_cases=None,
        ),
    ],
    multi_step_instructions=None,
)
