import pytest  # type:ignore[import]

from ebdtable2graph.models.ebd_table import (
    EbdCheckResult,
    EbdTable,
    EbdTableMetaData,
    EbdTableRow,
    EbdTableSubRow,
    MultiStepInstruction,
)


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

    def test_ebd_table_row_use_cases(self):
        row_17_in_e0462 = EbdTableRow(
            step_number="17",
            description="Liegt das Eingangsdatum der Anmeldung mehr als sechs Wochen nach dem Lieferbeginndatum der Anmeldung?",
            use_cases=["Einzug", "kME ohne RLM/mME/ Pauschalanlage"],
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A06",
                    note="Cluster: Ablehnung\nFristüberschreitung bei kME ohne RLM/mME/ Pauschalanlage",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="21"),
                    result_code=None,
                    note=None,
                ),
            ],
        )
        assert isinstance(row_17_in_e0462, EbdTableRow)
        assert row_17_in_e0462.use_cases is not None
        # if it can be instantiated with use cases that's a good enough test for the model

    def test_answer_code_aastersik(self):
        """
        This is an example from 6.27.1 E_0455_Information prüfen.
        The tests asserts that the validator of the result code allow the result code 'A**' which is used in E_0455.
        """
        sub_row = EbdTableSubRow(
            result_code="A**",
            check_result=EbdCheckResult(result=False, subsequent_step_number=None),
            note="Stammdaten wurden übernommen.\nHinweis A**: Es werden alle gemerkten Ant-wortcodes der vorhergehenden Prüfschritte übermittelt",
        )
        assert isinstance(sub_row, EbdTableSubRow)
        assert sub_row.result_code == "A**"

    def test_collect_answer_codes_instruction(self):
        snippet_from_e0453 = EbdTable(
            metadata=EbdTableMetaData(
                ebd_code="E_0453",
                chapter="6.18 AD: Stammdatensynchronisation",
                sub_chapter="6.18.1 E_0453_Änderung prüfen",
                role="ÜNB",
            ),
            multi_step_instructions=[
                MultiStepInstruction(
                    instruction_text="Alle festgestellten Antworten sind anzugeben, soweit im Format möglich (maximal 8 Antwortcodes)*.",
                    first_step_number_affected="4",
                )
            ],
            rows=[
                # ... steps 1-3
                EbdTableRow(
                    step_number="4",
                    description="Sind Fehler im Rahmen der AHB-Prüfungen in den Stammdaten des LF festgestellt worden?",
                    sub_rows=[
                        EbdTableSubRow(
                            check_result=EbdCheckResult(result=True, subsequent_step_number="5"),
                            result_code="A98",
                            note="Die Stammdaten des LF genügen nicht den AHB-Vorgaben.\nHinweis: Diese Prüfung ist auf alle Stammdaten des LF anzuwenden. Es sind die Fehlerorte aller dabei festgestellten Fehler in der Antwort zu benennen.",
                        ),
                        EbdTableSubRow(
                            check_result=EbdCheckResult(result=False, subsequent_step_number="5"),
                            result_code=None,
                            note=None,
                        ),
                    ],
                )
                # ... all the other steps 5-27
            ],
        )
        assert snippet_from_e0453.multi_step_instructions is not None
        # If it can be instantiated that's test enough for the model.
