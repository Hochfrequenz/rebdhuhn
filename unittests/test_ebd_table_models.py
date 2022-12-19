import pytest  # type:ignore[import]

from ebdtable2graph.models.ebd_table import EbdCheckResult, EbdTable, EbdTableMetaData, EbdTableRow, EbdTableSubRow


class TestEbdTableModels:
    @pytest.mark.parametrize(
        "table",
        [
            pytest.param(
                EbdTable(
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
                            sub_rows=[
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
                        )
                    ],
                ),
                id="Erste Zeile von E_0015",
            )
        ],
    )
    def test_instantiation(self, table: EbdTable):
        """
        The test is successful already if the instantiation in the parametrization worked
        """
        assert table is not None

    @pytest.mark.parametrize(
        "row,expected_result",
        [
            pytest.param(
                EbdTableRow(
                    step_number="1",
                    description="Erfolgt die Aktivierung nach Ablauf der Clearingfrist für die KBKA?",
                    sub_rows=[
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
                True,
            ),
            pytest.param(
                EbdTableRow(
                    step_number="2",
                    description="""Ist in der Kündigung die Angabe der Identifikationslogik mit
dem Wert „Marktlokations-ID“ angegeben?""",
                    sub_rows=[
                        EbdTableSubRow(
                            check_result=EbdCheckResult(result=True, subsequent_step_number="3"),
                            result_code=None,
                            note=None,
                        ),
                        EbdTableSubRow(
                            check_result=EbdCheckResult(result=False, subsequent_step_number="4"),
                            result_code=None,
                            note=None,
                        ),
                    ],
                ),
                True,
            ),
            pytest.param(
                EbdTableRow(
                    step_number="2",
                    description="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?",
                    sub_rows=[
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
                False,
            ),
        ],
    )
    def test_has_subsequent_steps(self, row: EbdTableRow, expected_result: bool):
        actual = row.has_subsequent_steps()
        assert actual == expected_result
