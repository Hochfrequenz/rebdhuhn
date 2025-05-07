"""
Contains a small part of the FV2504 E_0594 EBD table (the important/new part: a transition node)
"""

from rebdhuhn.models import EbdCheckResult, EbdTable, EbdTableMetaData, EbdTableRow, EbdTableSubRow

table_0594_partly = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0594",
        chapter="GPKE",
        section="MaLo Ident",
        ebd_name="Ein Teil von E_0594 mit einem Transition Node",
        role="VNB",
    ),
    rows=[
        EbdTableRow(
            step_number="270",
            description="Ist das Identifikationskriterium „Adresse“ in der Anfrage enthalten?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="275"),
                    result_code=None,
                    note=None,
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="280"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(  # hier der transition node
            step_number="275",
            description="Vollständige [Adressprüfung]",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=None, subsequent_step_number="280"),
                    result_code=None,
                    note="Aufnahme von 0..n Treffern in die Trefferliste auf Basis der alleinigen Adressprüfung",
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="280",
            description="Gibt es in der Trefferliste auf Basis der alleinigen Adressprüfung genau einen Treffer mit dem Identifikationskriterium Adresse?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A02",
                    note="Cluster Ablehnung blablba",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A123",  # ist egal, der wichtige part ist step 275
                    note="Cluster keine Ablehnung bliblub",
                ),
            ],
            use_cases=None,
        ),
    ],
    multi_step_instructions=None,
)
