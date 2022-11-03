"""
This module contains models that represent the data from the edi@energy documents.
The central class in this module is the EbdTable.
An EbdTable is the EDI@Energy raw representation of an "Entscheidungsbaum".
"""
from typing import List, Optional

import attrs


@attrs.define(auto_attribs=True, kw_only=True)
class EbdTableMetaData:
    """
    metadata about an EBD table
    """

    ebd_code: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    ID of the EBD; e.g. 'E_0053'
    """
    chapter: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    Chapter from the EDI@Energy Document
    e.g. '7.24 AD:  Übermittlung Datenstatus für die Bilanzierungsgebietssummenzeitreihe vom BIKO an ÜNB und NB'
    """
    sub_chapter: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    Sub Chapter from the EDI@Energy Document
    e.g. '7.24.1 Datenstatus nach erfolgter Bilanzkreisabrechnung vergeben'
    """
    role: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    e.g. 'BIKO' for "Prüfende Rolle: 'BIKO'"
    """


@attrs.define(auto_attribs=True, kw_only=True)
class EbdCheckResult:
    """
    This describes the result of a Prüfschritt in the EBD.
    The outcome can be either the final leaf of the graph or the key/number of the next Prüfschritt.
    The German column header is 'Prüfergebnis'.

    To model "ja": use result=True, subsequent_step_number=None
    To model "nein🠖2": use result=False, subsequent_step_number="2"
    """

    result: bool = attrs.field(validator=attrs.validators.instance_of(bool))
    """
    Either "ja"=True or "nein"=False
    """

    subsequent_step_number: Optional[str] = attrs.field(
        validator=attrs.validators.optional(attrs.validators.matches_re(r"^\d+\*?$"))
    )
    """
    Key of the following/subsequent step, e.g. '2', or '6*' or None, if there is no follow up step
    """


@attrs.define(auto_attribs=True, kw_only=True)
class EbdTableSubRow:
    """
    A sub row describes the outer right 3 columns of a EbdTableRow.
    In most cases there are two sub rows for each TableRow (one for "ja", one for "nein").
    The German column headers are 'Prüfergebnis', 'Code' and 'Hinweis'
    """

    check_result: EbdCheckResult = attrs.field(validator=attrs.validators.instance_of(EbdCheckResult))
    """
    The column 'Prüfergebnis'
    """
    result_code: Optional[str] = attrs.field(
        validator=attrs.validators.optional(attrs.validators.matches_re(r"^[A-Z]\d+$"))
    )
    """
    The outcome if no subsequent step was defined in the CheckResult.
    The German column header is 'Code'.
    """

    note: Optional[str] = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
    """
    An optional note for this outcome.
    E.g. 'Cluster:Ablehnung\nFristüberschreitung'
    The German column header is 'Hinweis'.
    """


@attrs.define(auto_attribs=True, kw_only=True)
class EbdTableRow:
    """
    A single row inside the Prüfschritt-Tabelle
    """

    step_number: str = attrs.field(validator=attrs.validators.matches_re(r"\d+\*?"))
    """
    number of the Prüfschritt, e.g. '1', '2' or '6*'
    The German column header is 'Nr'.
    """
    description: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    A free text description of the 'Prüfschritt'. It usually ends with a question mark.
    E.g. 'Erfolgt die Aktivierung nach Ablauf der Clearingfrist für die KBKA?'
    The German column header is 'Prüfschritt'.
    """
    check_results: List[EbdTableSubRow] = attrs.field(
        validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(EbdTableSubRow),
            iterable_validator=attrs.validators.min_len(2),
        ),
    )
    """
    One table row splits into multiple sub rows: one sub row for each check result (ja/nein)
    """


@attrs.define(auto_attribs=True, kw_only=True)
class EbdTable:
    """
    A Table is a list of rows + some metadata
    """

    metadata: EbdTableMetaData = attrs.field(validator=attrs.validators.instance_of(EbdTableMetaData))
    """
    meta data about the table
    """
    rows: List[EbdTableRow] = attrs.field(
        validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(EbdTableRow), iterable_validator=attrs.validators.min_len(1)
        ),
    )
