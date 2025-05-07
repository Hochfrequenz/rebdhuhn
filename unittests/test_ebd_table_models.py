import cattrs
import pytest

from rebdhuhn.models.ebd_table import (
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
                        section="7.17.1 E_0015_MaBiS-ZP Aktivierung prüfen",
                        ebd_name="E_0404_Lieferbeginn prüfen",
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
    def test_instantiation(self, table: EbdTable) -> None:
        """
        The test is successful already if the instantiation in the parametrization worked
        """
        assert table is not None
        serialized_table = cattrs.unstructure(table)
        deserialized_table = cattrs.structure(serialized_table, EbdTable)
        assert deserialized_table == table

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
    def test_has_subsequent_steps(self, row: EbdTableRow, expected_result: bool) -> None:
        actual = row.has_subsequent_steps()
        assert actual == expected_result

    def test_ebd_table_row_use_cases(self) -> None:
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

    def test_answer_code_astersik(self) -> None:
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

    def test_subrow_with_only_subsequent_step(self) -> None:
        """
        This is an example from E_0594 where there is no result code but only a subsequent step.
        """
        sub_row = EbdTableSubRow(
            result_code=None,
            check_result=EbdCheckResult(result=None, subsequent_step_number="110"),
            note="Aufnahme von 0..n Treffern in die Trefferliste auf Basis eines Kriteriums",
        )
        assert isinstance(sub_row, EbdTableSubRow)

    def test_subrow_not_both_must_be_null(self) -> None:
        """
        Check that the result code and the subsequent step are not both null.
        """
        with pytest.raises(ValueError):
            _ = (EbdCheckResult(result=None, subsequent_step_number=None),)

    def test_row_with_only_one_subrow(self) -> None:
        """
        This is an example from E_0594 where there is a step with only 1 subrow and no ja/nein distinction
        """
        row = EbdTableRow(
            step_number="105",
            # pylint:disable=line-too-long
            description="[Adressprüfung] (Straße und PLZ oder geographische Koordinaten oder Flurstücknummer) Hinweis: Das Weglassen der Hausnummer, trägt dem Umstand Rechnung, dass einige NB eher die Adresse des Geräts und nicht die Lieferadresse hinterlegt haben. Wenn der Zähler im Doppelhaus nebenan zu finden ist, weiß der Kunde das ggf.",
            sub_rows=[
                EbdTableSubRow(
                    result_code=None,
                    check_result=EbdCheckResult(result=None, subsequent_step_number="110"),
                    note="Aufnahme von 0..n Treffern in die Trefferliste auf Basis eines Kriteriums",
                )
            ],
        )
        assert isinstance(row, EbdTableRow)

    def test_row_with_only_one_subrow_is_not_allowed_if_ja_nein_distinction(self) -> None:
        with pytest.raises(ValueError):
            _ = EbdTableRow(
                step_number="105",
                description="[Adressprüfung] (Straße und PLZ oder geographische Koordinaten oder Flurstücknummer) Hinweis: Das Weglassen der Hausnummer, trägt dem Umstand Rechnung, dass einige NB eher die Adresse des Geräts und nicht die Lieferadresse hinterlegt haben. Wenn der Zähler im Doppelhaus nebenan zu finden ist, weiß der Kunde das ggf.",
                sub_rows=[
                    EbdTableSubRow(
                        result_code=None,
                        check_result=EbdCheckResult(result=True, subsequent_step_number="110"),  # <--not allowed
                        note="Aufnahme von 0..n Treffern in die Trefferliste auf Basis eines Kriteriums",
                    )
                ],
            )

    def test_row_with_two_subrows_does_not_allow_none_result(self) -> None:
        with pytest.raises(ValueError):
            _ = EbdTableRow(
                step_number="105",
                description="xyz.",
                sub_rows=[
                    EbdTableSubRow(
                        result_code=None,
                        check_result=EbdCheckResult(result=True, subsequent_step_number="110"),
                        note="Foo",
                    ),
                    EbdTableSubRow(
                        result_code=None,
                        check_result=EbdCheckResult(result=None, subsequent_step_number="111"),  # <--not allowed
                        note="Bar",
                    ),
                ],
            )

    def test_2023_answer_code_regex(self) -> None:
        """
        This is an example from E_0406.
        The test asserts that the validator of the result code allows the result code 'AC7'.
        """
        sub_row = EbdTableSubRow(
            result_code="AC7",
            check_result=EbdCheckResult(result=False, subsequent_step_number=None),
            note="Cluster: Ablehnung auf Kopfebene\nDie Frist für die Abschlagsrechnung wurde nicht eingehalten.",
        )
        assert isinstance(sub_row, EbdTableSubRow)
        assert sub_row.result_code == "AC7"

    def test_collect_answer_codes_instruction(self) -> None:
        snippet_from_e0453 = EbdTable(
            metadata=EbdTableMetaData(
                ebd_code="E_0453",
                chapter="6.18 AD: Stammdatensynchronisation",
                section="6.18.1 E_0453_Änderung prüfen",
                ebd_name="E_0404_Lieferbeginn prüfen",
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
