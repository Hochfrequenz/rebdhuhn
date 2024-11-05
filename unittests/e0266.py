"""
Contains the raw data for E_0266 in the form of an EbdTable.
"""

from rebdhuhn.models import EbdCheckResult, EbdTable, EbdTableMetaData, EbdTableRow, EbdTableSubRow
from rebdhuhn.models.ebd_table import MultiStepInstruction

table_e0266 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0266",
        chapter="WiM Strom",
        section="9.26.3: AD Abrechnung einer für den ESA erbrachten Leistung",
        role="ESA",
    ),
    rows=[
        EbdTableRow(
            step_number="1",
            description="Konnte der MSB alle Einwände des Rechnungsempfängers entkräften?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A25",
                    note="Cluster: Ablehnung auf Kopfebene\nDer Rechnungsempfänger lehnt die Zahlung der Rechnung weiterhin ab, da der MSB nicht alle Einwände des Rechnungsempfängers entkräften konnte. \nHinweis: Der Einwand ist in der Antwort zu beschreiben.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="10"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="10",
            description="Entspricht die Rechnung den Anforderungen gem. §14 Abs. 4 UStG?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A01",
                    note="Cluster: Ablehnung auf Kopfebene\nRechnung entspricht nicht §14 UstG",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="20"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="20",
            description="Ist das Rechnungsdatum ≤ dem Eingangsdatum?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A02",
                    note="Cluster: Ablehnung auf Kopfebene\nRechnungsdatum liegt in der Zukunft",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="30"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="30",
            description="Ist das Rechnungsdatum < dem Ausführungsdatum/Leistungszeitraum?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A03",
                    note="Cluster: Ablehnung auf Kopfebene\nDas Rechnungsdatum liegt vor dem Ausführungsdatum/Leistungszeitraum.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="40"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="40",
            description="Basiert die Rechnung auf einer Bestellung?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A04",
                    note="Cluster: Ablehnung auf Kopfebene\nDer Rechnungsempfänger lehnt die Zahlung ab, da die Rechnung auf keiner Bestellung basiert.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="50"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="50",
            description="Liegt vom Rechnungssteller, die in dieser Rechnung verwendete Rechnungsnummer, bereits vor?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A05",
                    note="Cluster: Ablehnung auf Kopfebene\nRechnungsnummer wurde bereits verwendet",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="60"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="60",
            description="Ist der fällige Betrag ≥ Null?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A06",
                    note="Cluster: Ablehnung auf Kopfebene\nBei der Abrechnung des MSB kann es nicht zu einer Rückerstattung kommen.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="70"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="70",
            description="Ist die Frist der Fälligkeit unterschritten?\nHinweis: Fälligkeit unterschritten bedeutet: Zahlungsziel\xa0≤\xa010 WT zum Rechnungseingangsdatum",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A07",
                    note="Cluster: Ablehnung auf Kopfebene\nDas Zahlungsziel ist unterschritten.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="90"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="90",
            description="Ist ein zuvor nicht spezifizierter Fehler im Kopfteil der Rechnung aufgetreten?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A90",
                    note="Cluster: Ablehnung auf Kopfebene\nSonstiger Fehler auf Kopfebene.\nHinweis: Das identifizierte Problem ist in der Antwort zu beschreiben/benennen. Nutzungsmöglichkeit Ende: 01.10.2024 00:00 Uhr",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="300"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="300",
            description="Wurde in der Rechnungsposition die Artikel-ID aus der Bestellung verwendet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="440"),
                    result_code="A09",
                    note="Cluster: Ablehnung auf Positionsebene\n\nEs wurde in der Rechnungsposition nicht die Artikel-ID aus der Bestellung verwendet.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="310"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="310",
            description="Wurde die abzurechnende Leistung vom MSB durchgeführt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="320"),
                    result_code="A10",
                    note="Cluster: Ablehnung auf Positionsebene\nDer Rechnungsempfänger lehnt die Zahlung ab, da die Leistung nicht erfolgreich vom MSB durchgeführt wurde.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="320"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="320",
            description="Entspricht der Preis in der Rechnungsposition dem Preis aus dem Angebot, dass zum Zeitpunkt des Ausführungsdatums/zum Abrechnungszeitraum der Leistung gültig ist?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="330"),
                    result_code="A11",
                    note="Cluster: Ablehnung auf Positionsebene\nDer Preis in der Rechnungsposition entspricht nicht dem Preis aus dem Angebot.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="330"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="330",
            description="Wird für die Rechnungsposition der für diesen Zeitpunkt/Zeitraum korrekte gültige Umsatzsteuersatz angegeben?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="350"),
                    result_code="A12",
                    note="Cluster: Ablehnung auf Positionsebene\nDer gültige Umsatzsteuersatz für die Rechnungsposition für diesen Zeitpunkt/Zeitraum wurde nicht korrekt angegeben.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="350"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="350",
            description="Liegt der Leistungszeitraum bzw. das Ausführungsdatum der Rechnungsposition innerhalb des angegebenen Leistungszeitraums der Kopfebene?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="360"),
                    result_code="A13",
                    note="Cluster: Ablehnung auf Positionsebene\nDer Leistungszeitraum bzw. das Ausführungsdatum der Rechnungsposition ist nicht identisch mit dem Leistungszeitraum aus dem Kopfteil.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="360"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="360",
            description="Existiert in dieser Rechnung eine weitere Rechnungsposition mit identischer Artikel-ID und identischem oder überschneidendem Leistungszeitraum bzw. identischem Ausführungsdatum?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="370"),
                    result_code="A14",
                    note="Cluster: Ablehnung auf Positionsebene\nEs existiert in dieser Rechnung eine weitere Rechnungsposition mit identischer Artikel-ID und identischem oder überschneidendem Leistungszeitraum bzw. identischem Ausführungsdatum.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="370"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="370",
            description="Wurde die Artikel-ID bereits in einer vorherigen nicht stornierten Rechnung für den identischen Leistungszeitraum bzw. identischen Ausführungsdatum bereits abgerechnet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="420"),
                    result_code="A15",
                    note="Cluster: Ablehnung auf Positionsebene\nDie Artikel-ID wurde bereits in einer vorherigen nicht stornierten Rechnung für den identischen Leistungszeitraum bzw. identischem Ausführungsdatum bereits abgerechnet.\nHinweis: Rechnungsnummer ist anzugeben",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="420"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="420",
            description="Liegt ein Rechenfehler in der Rechnungsposition vor?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="430"),
                    result_code="A20",
                    note="Cluster: Ablehnung auf Positionsebene\nRechenfehler liegt vor",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="430"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="430",
            description="Ist in der Rechnungsposition ein zuvor nicht spezifizierter Fehler aufgetreten?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="440"),
                    result_code="A99",
                    note="Cluster: Ablehnung auf Positionsebene \nSonstiger Fehler auf Positionsebene.\nHinweis: Das identifizierte Problem ist in der Antwort zu beschreiben/benennen. Nutzungsmöglichkeit Ende: 01.10.2024 00:00 Uhr",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="440"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="440",
            description="Sind noch weitere Rechnungspositionen zu prüfen?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="300"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="450"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="450",
            description="Ist in mindestens einer Rechnungspositionen ein Fehler aufgetreten?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="Ende"),
                    result_code=None,
                    note="Hinweis: Alle erkannten Antwortcodes aus der Positionsebene sind für jeden fehlerhaft identifizierten Positionsteil unter Angabe der Positionsnummer zu übermitteln.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="500"),
                    result_code=None,
                    note="Die Prüfung des EBD wird im Summenteil fortgesetzt.",
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="500",
            description="Fehlen noch Positionen, die über das bestätigte Angebot vereinbart sind und somit in der Rechnung erwartet werden?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="Ende"),
                    result_code="A21",
                    note="Cluster: Ablehnung auf Summenebene\nErwartete Position nicht vorhanden\nHinweis: Die nicht enthaltenen Positionen aus dem Angebot sind unter Angabe der Positionsnummer aus dem bestätigten Angebot zu nennen.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="510"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="510",
            description="Entspricht für den genannten Steuersatz die Besteuerungsgrundlage der Summen der Einzelpositionen dieser Rechnung mit diesem Steuersatz?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="520"),
                    result_code="A22",
                    note="Cluster: Ablehnung auf Summenebene\nGenannter Steuersatz passt nicht zu der Summe\nder Einzelpositionen des Steuersatzes.\nHinweis: Es ist der Steuersatz (aus DE5278) und die Steuerkategorie (aus DE5305) des SG52 TAX zu nennen.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="520"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="520",
            description="Entspricht für diesen Steuersatz die Angabe des Steuerbetrages der Summe aller Rechnungspositionen (Netto) dieser Rechnung, denen dieser Steuersatz zugeordnet ist, multipliziert mit diesem Steuersatz?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="530"),
                    result_code="A23",
                    note="Cluster: Ablehnung auf Summenebene \nSumme aller Rechnungspositionen (Netto) dieser Rechnung, denen dieser Steuersatz zugeordnet ist, multipliziert mit diesem Steuersatz entspricht nicht der Angabe des Steuerbetrages für diesen Steuersatz.\nHinweis: Es ist der Steuersatz (aus DE5278) und die Steuerkategorie (aus DE5305) des SG52 TAX zu nennen.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="530"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="530",
            description="Sind noch weitere Steuersätze zu prüfen?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="510"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="540"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="540",
            description="Entspricht der Rechnungsbetrag der Summe aller Rechnungspositionen (Besteuerungsgrundlage) zzgl. dem jeweiligen Steuerbetrag?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="550"),
                    result_code="A24",
                    note="Cluster: Ablehnung auf Summenebene\nRechnungsbetrag (Besteuerungsgrundlage inklusive Steuerbetrag) der Summe ist nicht korrekt.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="550"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="550",
            description="Ist ein zuvor nicht spezifizierter Fehler im Summenteil aufgetreten?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="560"),
                    result_code="A96",
                    note="Cluster: Ablehnung auf Summenebene\nSonstiges\nHinweis: Das identifizierte Problem ist in der Antwort zu beschreiben/benennen.\nNutzungsmöglichkeit Ende: 01.10.2024 00:00 Uhr",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="560"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="560",
            description="Ist mindestens ein Fehler in der Summenebene aufgetreten?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="Ende"),
                    result_code=None,
                    note="Cluster: Ablehnung auf Summenebene\nHinweis: Alle erkannten Antwortcodes aus der Summenebene sind zu übermitteln.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="Ende"),
                    result_code=None,
                    note="Cluster: Zustimmung \nZahlung der Rechnung avisieren und im Zahlungslauf berücksichtigen.",
                ),
            ],
            use_cases=None,
        ),
    ],
    multi_step_instructions=[
        MultiStepInstruction(
            first_step_number_affected="300",
            instruction_text="Die nachfolgenden Prüfungen werden, beginnend mit der ersten Positionszeile, für jede Positionszeile durchgeführt. Tritt in einer Positionszeile der erste Fehler auf, so sind die weiteren Prüfungen, so dies noch möglich ist, auch durchzuführen. Alle im Positionsteil gefundenen Fehler sind, unter Nennung der jeweiligen Positionszeile, zu nennen.",
        ),
        MultiStepInstruction(
            first_step_number_affected="500",
            instruction_text="Die nachfolgende Prüfung erfolgt auf Summenebene des EBD, obwohl es sich um eine summarische Prüfung der Positionsebene handelt, da bei fehlenden Positionsnummer aus dem bestätigten Angebot keine Positionsnummer genannt werden kann, muss zur Übermittlung des Fehlers die REMADV Struktur zur Übermittlung von Fehlern auf Summenebene genutzt werden.",
        ),
    ],
)
