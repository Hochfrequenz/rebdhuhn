"""
This module contains models that represent the data from the edi@energy documents.
The central class in this module is the EbdTable.
An EbdTable is the EDI@Energy raw representation of an "Entscheidungsbaum".
"""

from datetime import date
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
    e.g. MaBiS
    """
    section: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    Section from the EDI@Energy Document
    e.g. '7.24.1 Datenstatus nach erfolgter Bilanzkreisabrechnung vergeben'
    """
    role: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    e.g. 'BIKO' for "Prüfende Rolle: 'BIKO'"
    """
    ebd_name: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    EBD name from the EDI@Energy Document
    e.g. 'E_0003_Bestellung der Aggregationsebene RZ prüfen'
    """
    remark: Optional[str] = attrs.field(
        default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str))
    )
    """
    remark for empty ebd sections, e.g. 'Derzeit ist für diese Entscheidung kein Entscheidungsbaum notwendig,
    da keine Antwort gegeben wird und ausschließlich die Liste versandt wird.'
    """
    version: Optional[str] = attrs.field(
        default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str))
    )
    """
    the version of the .docx document/file on which this EBD table is based.
    E.g. '4.0b', because (proper) semantic versioning is for loosers ;)
    """
    release_date: Optional[date] = attrs.field(
        default=None, validator=attrs.validators.optional(attrs.validators.instance_of(date))
    )
    """
    date on which the .docx document/file was released.
    This corresponds to the 'Stand' field in the EDI@Energy document title page, e.g. '2025-06-23'.
    It might be updated even if the version and original_release_date stay the same to indicate there was a 
    'Fehlerkorrektur' in the document.
    """
    # https://imgflip.com/i/a2saev

    original_release_date: Optional[date] = attrs.field(
        default=None, validator=attrs.validators.optional(attrs.validators.instance_of(date))
    )
    """
    date on which the EBD was originally released; It's called 'Ursprüngliches Publikationsdatum' on the EBD document
    title page. E.g. '2024-10-01'.
    """

    # I think that one could validate that if a `release_date` is set, then the `original_release_date` must be set and
    # before it. But we don't add this validation yet, because we all know the data integrity is... to be improved.


@attrs.define(auto_attribs=True, kw_only=True)
class EbdCheckResult:
    """
    This describes the result of a Prüfschritt in the EBD.
    The outcome can be either the final leaf of the graph or the key/number of the next Prüfschritt.
    The German column header is 'Prüfergebnis'.

    To model "ja": use result=True, subsequent_step_number=None
    To model "nein🠖2": use result=False, subsequent_step_number="2"
    To model "🠖110": use result=None, subsequent_step_number="110", happens e.g. in E_0594 step_number 105
    """

    result: Optional[bool] = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(bool)))
    """
    Either "ja"=True or "nein"=False
    """

    subsequent_step_number: Optional[str] = attrs.field(
        validator=attrs.validators.optional(attrs.validators.matches_re(r"^(?:\d+\*?)|(Ende)$"))
    )
    """
    Key of the following/subsequent step, e.g. '2', or '6*' or None, if there is no follow up step
    """

    @result.validator
    def _validate_result(self, attribute, value) -> None:  # type:ignore[no-untyped-def] #pylint:disable=unused-argument
        # This just ensures it's a class-level validation
        self._validate_only_one_none()

    def _validate_only_one_none(self) -> None:
        if self.result is None and self.subsequent_step_number is None:
            raise ValueError(
                # pylint:disable=line-too-long
                "If the result is not boolean (meaning neither 'ja' nor 'nein' but null), the subsequent step has to be set"
            )


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
    Check that the subrows cover both a True and a False outcome. e.g. Ja -> 2 AND Nein -> 3
    """
    # We implicitly assume that the value (list) provided already has exactly two entries.
    # This is enforced by other validators
    for boolean in [True, False]:
        if not any(True for sub_row in value if sub_row.check_result.result is boolean):
            raise ValueError(
                f"Exactly one of the entries in {attribute.name} has to have check_result.result {boolean}"
            )


def _check_that_neither_true_nor_false_occur(  # type:ignore[no-untyped-def]
    instance: EbdTableSubRow, attribute, value: List[EbdTableSubRow]
) -> None:
    """
    Check that the subrows contain neither true nor false but only a reference to a future steps.
    E.g. MaLo Ident E_0594 step_number 105 directly refers to step 110, no ja/nein and only 1 subrow.
    Screenshot here: https://github.com/Hochfrequenz/rebdhuhn/issues/379
    """
    # We implicitly assume that the value (list) provided already has exactly two entries.
    # This is enforced by other validators
    if len(value) != 1:
        raise ValueError("There must be exactly one subrow when the subrows are not a 'ja' or 'nein' distinction")
    if value[0].check_result.result is not None:
        raise ValueError("The subrow must not have a 'ja' or 'nein' distinction")


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
            iterable_validator=attrs.validators.or_(
                attrs.validators.and_(
                    attrs.validators.min_len(2), attrs.validators.max_len(2), _check_that_both_true_and_false_occur
                ),
                attrs.validators.and_(
                    attrs.validators.min_len(1), attrs.validators.max_len(1), _check_that_neither_true_nor_false_occur
                ),
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
    meta data about the table.
    """
    rows: List[EbdTableRow] = attrs.field(
        validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(EbdTableRow), iterable_validator=attrs.validators.min_len(0)
        ),
    )
    """
    rows are the body of the table;
    might have 0 rows, if the EBD exists but is just a paragraph of text, no real table
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
