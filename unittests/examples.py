from ebd_table_to_graph import EbdTable
from ebd_table_to_graph.models.ebd_table import EbdCheckResult, EbdTableMetaData, EbdTableRow, EbdTableSubRow

# E_0003 is pretty short
# https://www.entscheidungsbaumdiagramm.de/diagram?ebdKey=E_0003&formatVersion=FV2204
table_e0003 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0003",
        chapter="7.39 AD: Bestellung der Aggregationsebene der Bilanzkreissummenzeitreihe auf Ebene der Regelzone",
        sub_chapter="7.39.1 E_0003_Bestellung der Aggregationsebene RZ prüfen",
        role="ÜNB",
    ),
    rows=[
        EbdTableRow(
            step_number="1",
            description="Erfolgt der Eingang der Bestellung fristgerecht?",
            check_results=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A01",
                    note="Fristüberschreitung",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="2"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="2",
            description="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?",
            check_results=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A02",
                    note="Gewählter Zeitpunkt nicht zulässig",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="Ende"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
    ],
)

# E_00015 is a rather simple diagram:
# https://www.entscheidungsbaumdiagramm.de/diagram?ebdKey=E_0015&formatVersion=FV2204
table_e0015 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0015",
        chapter="7.17 AD: AD: Aktivierung eines MaBiS-ZP für Bilanzierungsgebietssummenzeitreihen vom ÜNB an BIKO und NB",
        sub_chapter="7.17.1 E_0015_MaBiS-ZP Aktivierung prüfen",
        role="BIKO",
    ),
    rows=[
        EbdTableRow(
            step_number="1",
            description="Erfolgt die Aktivierung nach Ablauf der Clearingfrist für die KBKA?",
            check_results=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A01",
                    note="Cluster Ablehnung\nFristüberschreitung",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="2"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="2",
            description="Erfolgt die Aktivierung zum Monatsersten 00:00 Uhr?",
            check_results=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A02",
                    note="Cluster Ablehnung\nGewählter Zeitpunkt nicht zulässig",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="3"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="3",
            description="Ist die richtige Regelzone angegeben",
            check_results=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A03",
                    note="Cluster Ablehnung\nRegelzone falsch",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="4"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="4",
            description="Ist das Bilanzierungsgebiet zum Aktivierungsbeginn in der Regelzone des BIKO gültig?",
            check_results=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A04",
                    note="Cluster Ablehnung\nBilanzierungsgebiet nicht gültig",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="5"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="5",
            description="Ist der ÜNB zum Aktivierungsbeginn für das Bilanzierungsgebiet zuständig?",
            check_results=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A05",
                    note="Cluster Ablehnung\nKeine Berechtigung",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="6"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="6",
            description="Existiert bereits ein abweichendes Tupel unter der ID des MaBiS-ZP?",
            check_results=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A06",
                    note="Cluster Ablehnung\nAbweichender MaBiS-ZP bereits vorhanden",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="7"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="7",
            description="Existiert bereits für das genannte Tupel aus Aggregations-verantwortlicher, Bilanzierungsgebiet, Spannungsebene und ZRT eine abweichende ID des MaBiS-ZP?",
            check_results=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A07",
                    note="Cluster Ablehnung\nAbweichende ID zum MaBiS-ZP bereits vorhanden",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="8"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="8",
            description="Ist der ÜNB zur Aktivierung des ZRT berechtigt?",
            check_results=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A08",
                    note="Cluster Ablehnung\nZRT Aktivierung nicht berechtigt",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="9"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="9",
            description="Passt die OBIS-Kennzahl zum ZRT?",
            check_results=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A09",
                    note="Cluster Ablehnung\nOBIS nicht passend",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="10"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="10",
            description="Ist der MaBiS-ZP zum Zeitpunkt der Aktivierung bereits aktiviert?",
            check_results=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A10",
                    note="Cluster Ablehnung\nMaBiS-ZP bereits aktiviert",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A11",
                    note="Cluster: Zustimmung\nAktivierung durchgeführt",
                ),
            ],
        ),
    ],
)
