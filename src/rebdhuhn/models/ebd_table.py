"""
This module contains models that represent the data from the edi@energy documents.
The central class in this module is the EbdTable.
An EbdTable is the EDI@Energy raw representation of an "Entscheidungsbaum".
"""

from typing import List, Optional

import attrs


# pylint:disable=too-few-public-methods
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
        validator=attrs.validators.optional(attrs.validators.matches_re(r"^(?:\d+\*?)|(Ende)$"))
    )
    """
    Key of the following/subsequent step, e.g. '2', or '6*' or None, if there is no follow up step
    """


RESULT_CODE_REGEX = r"^((?:[A-Z]\d+)|(?:A\*{2})|(?:A[A-Z]\d))$"


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
        validator=attrs.validators.optional(attrs.validators.matches_re(RESULT_CODE_REGEX))
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


# pylint: disable=unused-argument
def _check_that_both_true_and_false_occur(  # type:ignore[no-untyped-def]
    instance: EbdTableSubRow, attribute, value: List[EbdTableSubRow]
) -> None:
    """
    Check that the subrows cover both a True and a False outcome
    """
    # We implicitly assume that the value (list) provided already has exactly two entries.
    # This is enforced by other validators
    for boolean in [True, False]:
        if not any(True for sub_row in value if sub_row.check_result.result is boolean):
            raise ValueError(
                f"Exactly one of the entries in {attribute.name} has to have check_result.result {boolean}"
            )


_STEP_NUMBER_REGEX = r"\d+\*?"  #: regex used to validate step numbers, e.g. '4' or '7*'


@attrs.define(auto_attribs=True, kw_only=True)
class EbdTableRow:
    """
    A single row inside the Prüfschritt-Tabelle
    """

    step_number: str = attrs.field(validator=attrs.validators.matches_re(_STEP_NUMBER_REGEX))
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
    sub_rows: List[EbdTableSubRow] = attrs.field(
        validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(EbdTableSubRow),
            iterable_validator=attrs.validators.and_(
                attrs.validators.min_len(2), attrs.validators.max_len(2), _check_that_both_true_and_false_occur
            ),
        ),
    )
    """
    One table row splits into multiple sub rows: one sub row for each check result (ja/nein)
    """
    use_cases: Optional[List[str]] = attrs.field(
        validator=attrs.validators.optional(
            attrs.validators.deep_iterable(  # type:ignore[arg-type]
                member_validator=attrs.validators.instance_of(str),
                iterable_validator=attrs.validators.min_len(1),  # if the list is not None, it has to have entries
            )
        ),
        default=None,
    )
    """
    If certain rows of the EBD table are only relevant for specific use cases/scenarios, you can denote them here.
    E.g. E_0462 step_number 15 may only be applied for use_cases=["Einzug"].
    and E_0462 step_number 16 is only relevant for use_cases=["Einzug",	"iMS/kME mit RLM"].

    None means, there are no restrictions to when the check from the row shall be performed.
    """

    def has_subsequent_steps(self) -> bool:
        """
        return true iff there are any subsequent steps after this row, meaning: this is not a loose end of the graph
        """
        for sub_row in self.sub_rows:
            if sub_row.check_result.subsequent_step_number:
                if sub_row.check_result.subsequent_step_number != "Ende":
                    # "Ende" actually occurs in E_0003 or E_0025 🙈
                    return True
        return False


@attrs.define(auto_attribs=True, kw_only=True)
class MultiStepInstruction:
    """
    This class generally models plain text instructions that shall be applied to multiple steps in an EBD from a
    specified step number onwards. It'll be clearer with two examples.

    Example A:
    Sometimes, the checks described in the EBDs are not thought to be performed once per message, but once per MaLo.
    In German the instruction says: 'Je Marktlokation erfolgen die nachstehenden Prüfungen:'

    Example B:
    Sometimes the EBDs are not though to return only a single answer code but allow to collect multiple answer codes and
    return them all together. Technically this means: Don't exit the tree at the first sub row without a subsequent step
    but continue and perform the following checks as well.
    In German the instruction says:
    'Alle festgestellten Antworten sind anzugeben, soweit im Format möglich (maximal 8 Antwortcodes)*.'
    """

    first_step_number_affected: str = attrs.field(validator=attrs.validators.matches_re(_STEP_NUMBER_REGEX))
    """
    The first step number/row that is affected by the instruction. If the instruction occurs before e.g. step '4',
    then '4' is the first_step_number_affected.
    """
    instruction_text: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    Contains the instruction as plain text.
    Examples:
    'Alle festgestellten Antworten sind anzugeben, soweit...'
    'Je Marktlokation erfolgen die nachstehenden Prüfungen'
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
    """
    rows are the body of the table
    """
    # pylint: disable=duplicate-code
    multi_step_instructions: Optional[List[MultiStepInstruction]] = attrs.field(
        validator=attrs.validators.optional(
            attrs.validators.deep_iterable(  # type:ignore[arg-type]
                member_validator=attrs.validators.instance_of(MultiStepInstruction),
                iterable_validator=attrs.validators.min_len(1),  # if the list is not None, then it has to have entries
            )
        ),
        default=None,
    )
    """
    If this is not None, it means that from some point in the EBD onwards, the user is thought to obey additional
    instructions. There might be more than one of these instructions in one EBD table.
    """
