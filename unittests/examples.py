"""
this module contains ready-to-test examples from the EDI@Energy Documents
https://www.edi-energy.de/index.php?id=38&tx_bdew_bdew%5Buid%5D=1486&tx_bdew_bdew%5Baction%5D=download&tx_bdew_bdew%5Bcontroller%5D=Dokument&cHash=6d81fa28a8c94fb46ebab5e0088d641e
"""
from ebd_table_to_graph import EbdTable
from ebd_table_to_graph.models.ebd_table import EbdCheckResult, EbdTableMetaData, EbdTableRow, EbdTableSubRow

# todo @ konstantin
# the "manual" EBDs that cause problems with the existing code are e.g.:
# E_0011, E_0401, E_0453, E_0455, E_0462
# see https://github.com/Hochfrequenz/ebd_parser-backend/pull/189/files
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
            sub_rows=[
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
    ],
)

# E_0025 does not contain a lot of text
# https://www.entscheidungsbaumdiagramm.de/diagram?ebdKey=E_0025&formatVersion=FV2204
table_e0025 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0025",
        chapter="7.41 AD: Übermittlung Prüfmitteilung für die Bilanzkreissummenzeitreihe vom BKV an BIKO und ÜNB",
        sub_chapter="7.41.2 E_0025_Prüfmitteilung prüfen",
        role="BIKO",
    ),
    rows=[
        EbdTableRow(
            step_number="1",
            description="Erfolgt der Eingang der Prüfmitteilung nach Ablauf der Clearingfrist für die KBKA?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A01",
                    note="Fristüberschreitung",
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
            description="Befindet sich der MaBiS-ZP auf der Aggregationsebene RZ?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="3"),
                    result_code=None,
                    note=None,
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="5"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="3",
            description="""Hat der BKV für den BK dieses MaBiS-ZP in diesem Bilanzie-
rungsmonat die Aggregationsebene RZ abbestellt?""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="4"),
                    result_code=None,
                    note=None,
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="Ende"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="4",
            description="""Hat der BKV dem BIKO für diesen Bilanzierungsmonat bereits
mitgeteilt, dass die weiteren Prüfungen auf Ebene des BG
stattfinden müssen?""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A02",
                    note="Falsche Aggregationsebene BG",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="Ende"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="5",
            description="""Hat der BKV dem BIKO für diesen Bilanzierungsmonat bereits
mitgeteilt, dass die weiteren Prüfungen auf Ebene des BG
stattfinden müssen?""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A03",
                    note="Falsche Aggregationsebene RZ",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="Ende"),
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
        chapter="7.17 AD: Aktivierung eines MaBiS-ZP für Bilanzierungsgebietssummenzeitreihen vom ÜNB an BIKO und NB",
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
        ),
        EbdTableRow(
            step_number="2",
            description="Erfolgt die Aktivierung zum Monatsersten 00:00 Uhr?",
            sub_rows=[
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
            sub_rows=[
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
            sub_rows=[
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
            sub_rows=[
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
            sub_rows=[
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
            sub_rows=[
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
            sub_rows=[
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
            sub_rows=[
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
            sub_rows=[
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


# E_0401 is rather fucked up. This is, because it is technically a graph and not tree anymore
# https://www.entscheidungsbaumdiagramm.de/diagram?ebdKey=E_0401&formatVersion=FV2204
table_e0401 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0401",
        chapter="6.2 AD: Lieferende LF an NB",
        sub_chapter="6.2.1 E_0401_Abmeldung prüfen",
        role="NB",  # NB=VNB
    ),
    rows=[
        EbdTableRow(
            step_number="1",
            description="""Liegt ein Transaktionsgrund vor, der eine Abmeldung nur in
die Zukunft zulässt?
Das ist bei den folgenden Transaktionsgründen der Fall:
 Wechsel
 Ende der ESV ohne Folgelieferung
 Aufhebung einer zukünftigen Zuordnung wegen
aufgehobenem Vertragsverhältnis""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="4"),
                    result_code=None,
                    note=None,
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="2"),
                    result_code=None,
                    note="""Hinweis: Es liegt einer der folgenden
Transaktionsgründe vor:
 Ein-/Auszug (Umzug)
 Auszug wegen Stilllegung
 Aufhebung einer zukünftigen Zuordnung
wegen Auszug des Kunden
 Aufhebung einer zukünftigen Zuordnung
wegen Stilllegung""",
                ),
            ],
        ),
        EbdTableRow(
            step_number="2",
            description="""Liegt ein Transaktionsgrund vor, welcher mitteilt, dass der
Kunde vor Lieferbeginn ausgezogen ist, bzw. die
Marktlokation vor Lieferbeginn stillgelegt wurde?
Das ist bei den folgenden Transaktionsgründen der Fall:
 Aufhebung einer zukünftigen Zuordnung wegen Auszug
des Kunden
 Aufhebung einer zukünftigen Zuordnung wegen
Stilllegung""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="3"),
                    result_code=None,
                    note=None,
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="6"),
                    result_code=None,
                    note="""Hinweis: Es liegt einer der folgenden
Transaktionsgründe vor:
 Ein-/Auszug (Umzug)
 Auszug wegen Stilllegung""",
                ),
            ],
        ),
        EbdTableRow(
            step_number="3",
            description="""Liegt das Abmeldedatum mindestens einen Tag nach dem
Eingangsdatum der Abmeldung?""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A01",
                    note="""Cluster: Ablehnung
Fristüberschreitung bei Aufhebung einer zu-
künftigen Zuordnung wegen Auszug oder Still-
legung.""",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="9"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="4",
            description="""Liegt das Eingangsdatum mindestens 6 WT vor dem
Abmeldedatum?""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A02",
                    note="""Cluster: Ablehnung
Fristüberschreitung bei Transaktionsgründen für
eine Abmeldung in der Zukunft.""",
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
            description="""Liegt der Transaktionsgrund
• Aufhebung einer zukünftigen Zuordnung wegen auf-
gehobenem Vertragsverhältnis
vor?""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="9"),
                    result_code=None,
                    note=None,
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="10"),
                    result_code=None,
                    note="""Hinweis: Es liegt einer der folgenden
Transaktionsgründe vor:
• Wechsel
• Ende der ESV ohne Folgelieferung""",
                ),
            ],
        ),
        EbdTableRow(
            step_number="6",
            description="""Handelt es sich um eine Marktlokation, deren Mess-
lokationen vollständig mit iMS ausgestattet sind oder/und
deren Prognosegrundlage auf Basis von Werten erfolgt?""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="7"),
                    result_code=None,
                    note=None,
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="8"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="7",
            description="""Liegt das Abmeldedatum mindestens einen Tag nach dem
Eingangsdatum der Abmeldung?""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A03",
                    note="""Cluster: Ablehnung
Eingangsfrist bei iMS/kME mit RLM nicht ein-
gehalten.""",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="10"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="8",
            description="""Liegt das Eingangsdatum der Abmeldung mehr als sechs
Wochen nach dem Abmeldedatum der Abmeldung?""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A04",
                    note="""Cluster: Ablehnung
Fristüberschreitung bei kME ohne RLM/mME/
Pauschalanlage.""",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="10"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="9",
            description="""Erfolgt die Aufhebung einer zukünftigen Zuordnung zu dem
gleichen Datum (Zeitpunkt), welcher dem Lieferanten im
Lieferbeginn bestätigt wurde?""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A05",
                    note="""Cluster: Ablehnung
Die Aufhebung einer zukünftigen Zuordnung
muss zum Datum (Zeitpunkt) angegeben werden,
wie im Lieferbeginn bestätigt.""",
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
            description="""Wurde die Zuordnung des anfragenden Lieferanten zur
Marktlokation zum identischen Abmeldedatum bereits durch
eine Bestätigung in den folgenden Prozessschritten beendet?
Fall:
 SD: Lieferende von LF an NB, Prozessschritt 2 "Antwort
auf Abmeldung"
 SD: Lieferende von NB an LF, Prozessschritt 2 "Antwort
auf Abmeldung"
 SD: Lieferbeginn, Prozessschritt 4 "Beantwortung der
Abmeldeanfrage" oder die Bestätigung erfolgt durch
die Fristverstreichung""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="11"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A06",
                    note="""Cluster: Zustimmung
                    Bestätigung der Abmeldung""",
                ),
            ],
        ),
        EbdTableRow(
            step_number="11",
            description="""Ist der anfragende LF am Folgetag des Abmeldungsdatum der
Marktlokation noch zugeordnet?""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="12"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A06",
                    note="""Cluster: Zustimmung
                    Bestätigung der Abmeldung""",
                ),
            ],
        ),
        EbdTableRow(
            step_number="12",
            description="""Liegt ein Transaktionsgrund vor, aus welchem hervorgeht,
dass der Anschlussnutzer ausgezogen ist?
Das ist bei den folgenden Transaktionsgründen der Fall:
 Ein-/Auszug (Umzug)
 Auszug wegen Stilllegung""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A07",
                    note="""Cluster: Ablehnung
Lieferende zum Abmeldedatum wurde bereits
bestätigt""",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="13"), result_code=None, note=None
                ),
            ],
        ),
        EbdTableRow(
            step_number="13",
            description="""Liegt in der bereits bestätigten Abmeldung ein
Transaktionsgrund vor, aus welchem nicht hervorgeht, dass
der Anschlussnutzer ausgezogen ist?
Das ist bei den folgenden Transaktionsgründen der Fall:
 Ein-/Auszug (Umzug)
 Auszug wegen Stilllegung
 Aufhebung einer zukünftigen Zuordnung wegen
Stilllegung""",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A08",
                    note="""Cluster: Ablehnung
Lieferende zum Abmeldedatum wurde aus
gleichem Grund bereits bestätigt.""",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A09",
                    note="""Cluster: Zustimmung
Erneute Bestätigung der Abmeldung aufgrund der
Information, dass der Anschlussnutzer nicht mehr
an der Marktlokation vorhanden ist.
Hinweis: Das bisher bestätigte Bilanzierungsende
bleibt unverändert bestehen.""",
                ),
            ],
        ),
    ],
)

# for further even harder examples of graphs (not trees), please see E_0462
# https://www.entscheidungsbaumdiagramm.de/diagram?ebdKey=E_0462&formatVersion=FV2204
