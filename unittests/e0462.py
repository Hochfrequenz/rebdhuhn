"""
Contains the raw data for E_0401 in the form of an EbdTable.
"""

from rebdhuhn.models import EbdCheckResult, EbdTable, EbdTableMetaData, EbdTableRow, EbdTableSubRow

table_e0462 = EbdTable(
    metadata=EbdTableMetaData(ebd_code="E_0462", chapter="GPKE", section="6.4.1: AD: Lieferbeginn", role="NB"),
    rows=[
        EbdTableRow(
            step_number="1",
            description="Ist in der Anmeldung die Angabe der Identifikationslogik mit dem Wert „Marktlokations-ID“ angegeben?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="2"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="4"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="2",
            description="Wurde die im Geschäftsvorfall angegebene ID der Marktlokation im IT-System des Empfängers gefunden?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A01",
                    note="Cluster: Ablehnung\nMarktlokation ist nicht identifizierbar.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="3"),
                    result_code=None,
                    note="Hinweis: Bei dieser Prüfung hat der NB auch die Marktlokationen zu berücksichtigen, die in den letzten drei Jahren vor dem Eingang der Anfrage im Netzgebiet des NB waren.",
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="3",
            description="Nimmt die Marktlokation zum Anmeldedatum an der Marktkommunikation teil?\n(Dies sind Marktlokationen, bei welchen ein Bilanzkreis und ein Lieferant zugeordnet ist. Z.B. stillgelegte Marktlokationen oder Marktlokationen einer Kundenanlage, welche vom Kundenanlagenbetreiber beliefert werden und somit keine Zuordnung zu einem Lieferanten haben, nehmen nicht an der Marktkommunikation teil.)",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A15",
                    note="Cluster: Ablehnung\nMarktlokation, die über Marktlokations-ID identifiziert wurde, nimmt nicht an der Marktkommunikation teil.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="10"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="4",
            description="Wurde mit allen zur Verfügung gestellten Informationen aus der Anmeldung unter Wahrung der gebotenen Sorgfalt genau eine Marktlokation ermittelt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="5"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="6"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="5",
            description="Nimmt die Marktlokation zum Anmeldedatum an der Marktkommunikation teil? \n(Dies sind Marktlokationen, bei welchen ein Bilanzkreis und ein Lieferant zugeordnet ist. Z.B. stillgelegte Marktlokationen oder Marktlokationen einer Kundenanlage, welche vom Kundenanlagenbetreiber beliefert werden und somit keine Zuordnung zu einem Lieferanten haben, nehmen nicht an der Marktkommunikation teil.)",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A16",
                    note="Cluster: Ablehnung\nIdentifizierte Marktlokation nimmt nicht an der Marktkommunikation teil.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="10"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="6",
            description="Wurde mit allen zur Verfügung gestellten Informationen aus der Anmeldung unter Wahrung der gebotenen Sorgfalt mehr als eine Marktlokation ermittelt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="7"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="9"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="7",
            description="Handelt es sich um einen „Einzug in Neuanlage“?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A03",
                    note="Cluster: Ablehnung\nKeine Identifizierung",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="8"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="8",
            description="Ist die Anmeldung (der Neuanlage) vor mehr als 60 WT eingegangen?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A18",
                    note="Cluster: Ablehnung\nNeuangelegte Marktlokation konnte nicht identifiziert werden",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="4"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="9",
            description="Nimmt von den identifizierten Marktlokationen exakt eine Marktlokation an der Marktkommunikation teil? \n(Die andere(n) Marktlokation(en) sind z.B. stillgelegte Marktlokation(en), Objekt(e) um einen Teil einer Kundenanlage.)",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A17",
                    note="Cluster: Ablehnung\nMehrfachidentifizierung",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="10"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="10",
            description="Ist die Marktlokation zum Eingangsdatum der Meldung dem Netzgebiet zugeordnet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A04",
                    note="Cluster: Ablehnung\nMarktlokation befindet sich zum Eingangsdatum der Meldung nicht mehr im Netzgebiet des NB.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="11"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="11",
            description="Handelt es sich um einen Ein-/Auszug (Umzug)?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="14"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="12"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="12",
            description="Handelt es sich um einen „Einzug in Neuanlage“?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="14"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="13"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="13",
            description="Liegt der Transaktionsgrund zur Beendigung einer Ersatz-versorgung vor?\nDies ist bei dem folgenden Transaktionsgrund der Fall:\nLieferbeginn und Abmeldung aus der Ersatzversorgung",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="15"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="18"),
                    result_code=None,
                    note="Hinweis: es liegt der Transaktionsgrund „Wechsel“ vor.",
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="14",
            description="Sind bisheriger und neuer Anschlussnutzer identisch?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A13",
                    note="Cluster: Ablehnung\nEs handelt sich nicht um einen Einzug, da zum genannten Datum kein Anschlussnutzerwechsel stattfand.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="15"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="15",
            description="Handelt es sich um eine Marktlokation, deren Messlokationen vollständig mit iMS ausgestattet sind oder/und deren Prognosegrundlage auf Basis von Werten erfolgt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="16"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="17"), result_code=None, note=None
                ),
            ],
            use_cases=["Einzug"],
        ),
        EbdTableRow(
            step_number="16",
            description="Liegt das Lieferbeginndatum der Anmeldung mindestens einen Tag nach dem Eingangsdatum der Anmeldung?\nHinweis: Diese Prüfung enthält keine Aussage darüber, ob eine Verschiebung des Lieferbeginns notwendig ist.",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A05",
                    note="Cluster: Ablehnung\nEingangsfrist bei iMS / kME mit RLM nicht ein-gehalten",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="21"), result_code=None, note=None
                ),
            ],
            use_cases=["Einzug", "iMS/kME mit RLM"],
        ),
        EbdTableRow(
            step_number="17",
            description="Liegt das Eingangsdatum der Anmeldung mehr als sechs Wochen nach dem Lieferbeginndatum der Anmeldung?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A06",
                    note="Cluster: Ablehnung\nFristüberschreitung bei kME ohne RLM/mME/ Pauschalanlage",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="21"), result_code=None, note=None
                ),
            ],
            use_cases=["Einzug", "kME ohne RLM/mME/ Pauschalanlage"],
        ),
        EbdTableRow(
            step_number="18",
            description="Ist in der Anmeldung die Angabe der Identifikationslogik mit dem Wert „Marktlokations-ID“ angegeben?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="19"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="20"), result_code=None, note=None
                ),
            ],
            use_cases=["Lieferantenwechsel"],
        ),
        EbdTableRow(
            step_number="19",
            description="Liegt das Lieferbeginndatum der Anmeldung mindestens 7 WT nach dem Eingangsdatum der Anmeldung?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A09",
                    note="Cluster: Ablehnung\nFrist bei einem Lieferantenwechsel nicht ein-gehalten im Rahmen der schnellen Identifikation.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="21"), result_code=None, note=None
                ),
            ],
            use_cases=["Lieferantenwechsel", "schnelle Identifikation"],
        ),
        EbdTableRow(
            step_number="20",
            description="Liegt das Lieferbeginndatum der Anmeldung mindestens 10 WT nach dem Eingangsdatum der Anmeldung?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A10",
                    note="Cluster: Ablehnung\nFrist bei einem Lieferantenwechsel nicht eingehalten im Rahmen der langsamen Identifikation.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="21"), result_code=None, note=None
                ),
            ],
            use_cases=["Lieferantenwechsel", "langsame Identifikation"],
        ),
        EbdTableRow(
            step_number="21",
            description="Liegt für diese Marktlokation bereits eine gerade in Arbeit befindliche und noch nicht beantwortete Anmeldung vor?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A11",
                    note="Cluster: Ablehnung\nAndere Anmeldung in Bearbeitung.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="22"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="22",
            description="Liegt die notwendige Zuordnungsermächtigung (Bilanzkreis/Bilanzierungsverfahren) vor?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A12",
                    note="Cluster: Ablehnung\nZuordnungsermächtigung fehlt.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="23"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="23",
            description="Liegt der Transaktionsgrund „Lieferbeginn und Abmeldung aus der Ersatzversorgung“ vor?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code=None,
                    note="EBD E_0402_Prüfen, ob eine Abmeldeanfrage erforderlich",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="24"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="24",
            description="Ist der zum Anmeldedatum zugeordnete LF der GV?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A14",
                    note="Cluster: Ablehnung\nGrundversorger ist der Marktlokation nicht zu-geordnet.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code=None,
                    note="EBD E_0402_Prüfen, ob eine Abmeldeanfrage erforderlich",
                ),
            ],
            use_cases=None,
        ),
    ],
    multi_step_instructions=None,
)
