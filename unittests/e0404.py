"""
Contains the raw data for E_0404 in the form of an EbdTable.
"""

from rebdhuhn.models import EbdCheckResult, EbdTable, EbdTableMetaData, EbdTableRow, EbdTableSubRow

e_0404 = EbdTable(
    metadata=EbdTableMetaData(ebd_code="E_0404", chapter="GPKE", section="6.4.4: AD: Lieferbeginn", role="NB"),
    rows=[
        EbdTableRow(
            step_number="1",
            description="Wurde eine Abmeldeanfrage gestellt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="6"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="2"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="2",
            description="Hat der LFA fristgerecht geantwortet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="3"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="6"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="3",
            description="Hat der LFA der Abmeldeanfrage widersprochen?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="4"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="6"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="4",
            description="Wurde in der Beantwortung der Abmeldeanfrage der Code A30 „Ablehnung: Die Belieferung wurde zu dem angefragten Termin aus der Abmeldeanfrage bereits beendet und eine Abmeldung von dem LFA bereits versendet, die durch den NB bereits bestätigt wurde.“ verwendet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A50",
                    note="Cluster: Ablehnung\nDer LFA hat der Abmeldeanfrage widersprochen.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="5"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="5",
            description="Wurde die NN-Anmeldung des LFN bereits durch den NB beantwortet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code=None,
                    note="Ende\nHinweis: Der vom LFN gestartete Lieferbeginn-prozess (Anmeldung), der beim NB zur Versen-dung der Abmeldeanfrage an den LFA führte, wurde bereits durch einen vom LFA gestarteten Lieferendeprozess, der vor dem Eingang der Antwort der Abmeldeanfrage abgeschlossen wurde, beendet. Das führte dazu, dass der NB die Anmeldung des LFN vor dem Eingang der Antwort der Abmeldeanfrage bestätigt hatte. Somit ist an den LFN keine weitere Antwort auf seine Anmeldung mehr zu senden.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="6"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="6",
            description="Liegt die notwendige Zuordnungsermächtigung (Bilanzkreis/Bilanzierungsverfahren) vor?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A52",
                    note="Cluster: Ablehnung\nZuordnungsermächtigung fehlt.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A51",
                    note="Cluster: Zustimmung\nBestätigung der Anmeldung",
                ),
            ],
            use_cases=None,
        ),
    ],
    multi_step_instructions=None,
)
