"""
Contains the raw data for E_0487 in the form of an EbdTable.
"""

from rebdhuhn.models import EbdCheckResult, EbdTable, EbdTableMetaData, EbdTableRow, EbdTableSubRow

table_e0487 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0287",
        chapter="GPKE",
        section="6.16.1: AD: Wiederherstellung der Anschlussnutzung bei Lieferbeginn",
        ebd_name="E_0487_Prüfen, ob Entsperrauftrag erfolgreich",
        role="NB",
    ),
    rows=[
        EbdTableRow(
            step_number="1",
            description="Ist die Entsperrung erfolgreich durchgeführt worden?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A01",
                    note="Marktlokation ist entsperrt",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code=None,
                    note="Bilaterale Klärung.",
                ),
            ],
            use_cases=None,
        )
    ],
)
