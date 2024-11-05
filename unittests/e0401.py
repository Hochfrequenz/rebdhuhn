"""
Contains the raw data for E_0401 in the form of an EbdTable.
"""

from rebdhuhn.models import EbdCheckResult, EbdTable, EbdTableMetaData, EbdTableRow, EbdTableSubRow

e_0401 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0401",
        chapter="GPKE",
        section="6.2.1: AD: Lieferende LF an NB",
        ebd_name="6.2.1	E_0401_Abmeldung prüfen",
        role="NB",
    ),
    rows=[
        EbdTableRow(
            step_number="10",
            description="Liegt ein Transaktionsgrund vor, der eine Abmeldung nur in die Zukunft zulässt?\nDas ist bei den folgenden Transaktionsgründen der Fall:\nEnde wegen Kündigung durch LF\nEnde wegen Kündigung durch Kunde/LFN\nEnde der ESV ohne Folgelieferung\nAufhebung einer zukünftigen Zuordnung wegen aufgehobenem Vertragsverhältnis",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="40"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="20"),
                    result_code=None,
                    note="Hinweis: Es liegt einer der folgenden Transaktionsgründe vor:\nEin-/Auszug (Umzug)\nAuszug wegen Stilllegung\nAufhebung einer zukünftigen Zuordnung wegen Auszug des Kunden\nAufhebung einer zukünftigen Zuordnung wegen Stilllegung",
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="20",
            description="Liegt ein Transaktionsgrund vor, welcher mitteilt, dass der Kunde vor Lieferbeginn ausgezogen ist, bzw. die Marktlokation vor Lieferbeginn stillgelegt wurde?\nDas ist bei den folgenden Transaktionsgründen der Fall:\nAufhebung einer zukünftigen Zuordnung wegen Auszug des Kunden\nAufhebung einer zukünftigen Zuordnung wegen Stilllegung",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="30"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="80"),
                    result_code=None,
                    note="Hinweis: Es liegt einer der folgenden Transaktionsgründe vor: \nEin-/Auszug (Umzug)\nAuszug wegen Stilllegung",
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="30",
            description="Liegt das Abmeldedatum mindestens einen Tag nach dem Eingangsdatum der Abmeldung?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A01",
                    note="Cluster: Ablehnung\nFristüberschreitung bei Aufhebung einer zu-künftigen Zuordnung wegen Auszug oder Still-legung.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="110"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="40",
            description="Liegt das Eingangsdatum mindestens 6 WT vor dem Abmeldedatum?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A02",
                    note="Cluster: Ablehnung\nFristüberschreitung bei Transaktionsgründen für eine Abmeldung in der Zukunft.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="50"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="50",
            description="Liegt der Transaktionsgrund \nAufhebung einer zukünftigen Zuordnung wegen aufgehobenem Vertragsverhältnis\nvor?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="110"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="60"),
                    result_code=None,
                    note="Hinweis: Es liegt einer der folgenden Transaktionsgründe vor: \nEnde wegen Kündigung durch LF\nEnde wegen Kündigung durch Kunde/LFN\nEnde der ESV ohne Folgelieferung",
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="60",
            description="Liegt der Transaktionsgrund \nEnde der ESV ohne Folgelieferung\nvor?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="70"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="120"),
                    result_code=None,
                    note="Hinweis: Es liegt einer der folgenden Transaktionsgründe vor: \nEnde wegen Kündigung durch LF\nEnde wegen Kündigung durch Kunde/LFN",
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="70",
            description="Gab es an dieser Marktlokation eine bestätigte Anmeldung zur Ersatz- Grundversorgung mit einem Lieferbeginnzeitpunkt, welcher innerhalb 3 Monaten vom Endezeitpunkt der Belieferung aus dieser Abmeldung begonnen hat?\nHinweis: \nEine Lieferende mit dem Grund „Ende der ESV ohne Folgelieferung“ kann nur in dem Fall vorliegen, wenn diese Marktlokation innerhalb der letzten 3 Monate auch über den Use-Case „Beginn der Ersatz-/Grundversorgung“ vom NB beim LF angemeldet wurde.",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A11",
                    note="Cluster: Ablehnung\nDie Marklokation wurde nicht innerhalb der letzten 3 Monate zur Ersatz-/ Grundversorgung angemeldet. Somit kann es sich nicht um eine Beendigung einer ESV handeln.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="120"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="80",
            description="Handelt es sich um eine Marktlokation, deren Mess-lokationen vollständig mit iMS ausgestattet sind oder/und deren Prognosegrundlage auf Basis von Werten erfolgt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="90"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="100"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="90",
            description="Liegt das Abmeldedatum mindestens einen Tag nach dem Eingangsdatum der Abmeldung?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A03",
                    note="Cluster: Ablehnung\nEingangsfrist bei iMS/kME mit RLM nicht ein-gehalten.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="120"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="100",
            description="Liegt das Eingangsdatum der Abmeldung mehr als sechs Wochen nach dem Abmeldedatum der Abmeldung?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A04",
                    note="Cluster: Ablehnung\nFristüberschreitung bei kME ohne RLM/mME/ Pauschalanlage.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="120"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="110",
            description="Erfolgt die Aufhebung einer zukünftigen Zuordnung zu dem gleichen Datum (Zeitpunkt), welcher dem Lieferanten im Lieferbeginn bestätigt wurde?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A10",
                    note="Cluster: Ablehnung\nDie Aufhebung einer zukünftigen Zuordnung muss zum Datum (Zeitpunkt) angegeben werden, wie im Lieferbeginn bestätigt.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="120"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="120",
            description='Wurde die Zuordnung des anfragenden Lieferanten zur Marktlokation zum identischen Abmeldedatum bereits durch eine Bestätigung in den folgenden Prozessschritten beendet? Fall:\nSD: Lieferende von LF an NB, Prozessschritt 2 "Antwort auf Abmeldung"\nSD: Lieferende von NB an LF, Prozessschritt 2 "Antwort auf Abmeldung"\nSD: Lieferbeginn, Prozessschritt 4 "Beantwortung der Abmeldeanfrage" oder die Bestätigung erfolgt durch die Fristverstreichung',
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="130"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A06",
                    note="Cluster: Zustimmung\nBestätigung der Abmeldung",
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="130",
            description="Ist der anfragende LF am Folgetag des Abmeldungsdatum der Marktlokation noch zugeordnet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="140"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A06",
                    note="Cluster: Zustimmung\nBestätigung der Abmeldung",
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="140",
            description="Liegt ein Transaktionsgrund vor, aus welchem hervorgeht, dass der Anschlussnutzer ausgezogen ist?\nDas ist bei den folgenden Transaktionsgründen der Fall:\nEin-/Auszug (Umzug)\nAuszug wegen Stilllegung",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A07",
                    note="Cluster: Ablehnung \nLieferende zum Abmeldedatum wurde bereits bestätigt.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="150"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="150",
            description="Liegt in der bereits bestätigten Abmeldung ein Transaktionsgrund vor, aus welchem nicht hervorgeht, dass der Anschlussnutzer ausgezogen ist?\nDas ist bei den folgenden Transaktionsgründen der Fall:\nEnde wegen Kündigung durch LF\nEnde wegen Kündigung durch Kunde/LFN\nEnde der ESV ohne Folgelieferung\nAufhebung einer zukünftigen Zuordnung wegen\naufgehobenem Vertragsverhältnis\nAbmeldung wg. fehl. Zuordnungsermächtigung\nAbmeldung wegen fehl. Zuordnungsermächtigung aufgrund Änderung ZRT\nLieferbeginn und Abmeldung aus der Ersatzversorgung",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A08",
                    note="Cluster: Ablehnung \nLieferende zum Abmeldedatum wurde aus gleichem Grund bereits bestätigt.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A09",
                    note="Cluster: Zustimmung\nErneute Bestätigung der Abmeldung aufgrund der Information, dass der Anschlussnutzer nicht mehr an der Marktlokation vorhanden ist.\nHinweis: Das bisher bestätigte Bilanzierungsende bleibt unverändert bestehen.",
                ),
            ],
            use_cases=None,
        ),
    ],
    multi_step_instructions=None,
)
