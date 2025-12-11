"""
This module contains models that represent the data from the edi@energy documents.
The central class in this module is the EbdTable.
An EbdTable is the EDI@Energy raw representation of an "Entscheidungsbaum".
"""

from datetime import date
from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

#: regex used to validate step numbers, e.g. '4' or '7*'
_STEP_NUMBER_REGEX = r"^\d+\*?$"

#: regex used to validate result codes, e.g. 'A01', 'A**', 'AA1'
RESULT_CODE_REGEX = r"^((?:[A-Z]\d+)|(?:A\*{2})|(?:A[A-Z]\d))$"

#: Annotated type for step numbers
StepNumber = Annotated[str, Field(pattern=_STEP_NUMBER_REGEX)]

#: Annotated type for result codes
ResultCode = Annotated[str, Field(pattern=RESULT_CODE_REGEX)]

#: Annotated type for subsequent step numbers (includes 'Ende')
SubsequentStepNumber = Annotated[str, Field(pattern=r"^(?:\d+\*?)|(Ende)$")]


class EbdDocumentReleaseInformation(BaseModel):
    """
    Contains information from the title (first) page of the EDI@Energy document which contains all EBDs.
    """

    model_config = ConfigDict(extra="forbid")

    version: str
    """
    the version of the .docx document/file on which this EBD table is based.
    E.g. '4.0b', because (proper) semantic versioning is for loosers ;)
    """
    release_date: Optional[date] = None
    """
    date on which the .docx document/file was released.
    This corresponds to the 'Stand' field in the EDI@Energy document title page, e.g. '2025-06-23'.
    It might be updated even if the version and original_release_date stay the same to indicate there was a
    'Fehlerkorrektur' in the document.
    """
    # https://imgflip.com/i/a2saev

    original_release_date: Optional[date] = None
    """
    date on which the EBD was originally released; It's called 'Ursprüngliches Publikationsdatum' on the EBD document
    title page. E.g. '2024-10-01'.
    """
    # I think that one could validate that if a `release_date` is set, then the `original_release_date` must be set and
    # before it. But we don't add this validation yet, because we all know the data integrity is... to be improved.


# pylint:disable=too-few-public-methods, too-many-instance-attributes
class EbdTableMetaData(BaseModel):
    """
    metadata about an EBD table
    """

    model_config = ConfigDict(extra="forbid")

    ebd_code: str
    """
    ID of the EBD; e.g. 'E_0053'
    """
    chapter: str
    """
    Chapter from the EDI@Energy Document
    e.g. MaBiS
    """
    section: str
    """
    Section from the EDI@Energy Document
    e.g. '7.24.1 Datenstatus nach erfolgter Bilanzkreisabrechnung vergeben'
    """
    role: str
    """
    e.g. 'BIKO' for "Prüfende Rolle: 'BIKO'"
    """
    ebd_name: str
    """
    EBD name from the EDI@Energy Document
    e.g. 'E_0003_Bestellung der Aggregationsebene RZ prüfen'
    """
    remark: Optional[str] = None
    """
    remark for empty ebd sections, e.g. 'Derzeit ist für diese Entscheidung kein Entscheidungsbaum notwendig,
    da keine Antwort gegeben wird und ausschließlich die Liste versandt wird.'
    """

    release_information: Optional[EbdDocumentReleaseInformation] = None
    """
    metadata of the entire EBD document (not the single EBD table)
    """

    note: Optional[str] = None
    """
    Optional note about the source of this EBD table.
    E.g. 'Diese Tabelle stammt aus dem ebd.docx EBD_4.0b_20250606_20250930_20250430'
    """

    link: Optional[str] = None
    """
    Optional link to the source document.
    E.g. 'https://github.com/Hochfrequenz/edi_energy_mirror/blob/.../EBD_4.0b_20250606_....docx'
    """


class EbdCheckResult(BaseModel):
    """
    This describes the result of a Prüfschritt in the EBD.
    The outcome can be either the final leaf of the graph or the key/number of the next Prüfschritt.
    The German column header is 'Prüfergebnis'.

    To model "ja": use result=True, subsequent_step_number=None
    To model "nein🠖2": use result=False, subsequent_step_number="2"
    To model "🠖110": use result=None, subsequent_step_number="110", happens e.g. in E_0594 step_number 105
    """

    model_config = ConfigDict(extra="forbid")

    result: Optional[bool] = None
    """
    Either "ja"=True or "nein"=False
    """

    subsequent_step_number: Optional[SubsequentStepNumber] = None
    """
    Key of the following/subsequent step, e.g. '2', or '6*' or None, if there is no follow up step
    """

    @model_validator(mode="after")
    def validate_only_one_none(self) -> "EbdCheckResult":
        """Validate that result and subsequent_step_number are not both None."""
        if self.result is None and self.subsequent_step_number is None:
            raise ValueError(
                # pylint:disable=line-too-long
                "If the result is not boolean (meaning neither 'ja' nor 'nein' but null), the subsequent step has to be set"
            )
        return self


class EbdTableSubRow(BaseModel):
    """
    A sub row describes the outer right 3 columns of a EbdTableRow.
    In most cases there are two sub rows for each TableRow (one for "ja", one for "nein").
    The German column headers are 'Prüfergebnis', 'Code' and 'Hinweis'
    """

    model_config = ConfigDict(extra="forbid")

    check_result: EbdCheckResult
    """
    The column 'Prüfergebnis'
    """
    result_code: Optional[ResultCode] = None
    """
    The outcome if no subsequent step was defined in the CheckResult.
    The German column header is 'Code'.
    """

    note: Optional[str] = None
    """
    An optional note for this outcome.
    E.g. 'Cluster:Ablehnung\nFristüberschreitung'
    The German column header is 'Hinweis'.
    """


class EbdTableRow(BaseModel):
    """
    A single row inside the Prüfschritt-Tabelle
    """

    model_config = ConfigDict(extra="forbid")

    step_number: StepNumber
    """
    number of the Prüfschritt, e.g. '1', '2' or '6*'
    The German column header is 'Nr'.
    """
    description: str
    """
    A free text description of the 'Prüfschritt'. It usually ends with a question mark.
    E.g. 'Erfolgt die Aktivierung nach Ablauf der Clearingfrist für die KBKA?'
    The German column header is 'Prüfschritt'.
    """
    sub_rows: List[EbdTableSubRow]
    """
    One table row splits into multiple sub rows: one sub row for each check result (ja/nein)
    """
    use_cases: Optional[List[str]] = None
    """
    If certain rows of the EBD table are only relevant for specific use cases/scenarios, you can denote them here.
    E.g. E_0462 step_number 15 may only be applied for use_cases=["Einzug"].
    and E_0462 step_number 16 is only relevant for use_cases=["Einzug",	"iMS/kME mit RLM"].

    None means, there are no restrictions to when the check from the row shall be performed.
    """

    @model_validator(mode="after")
    def validate_sub_rows(self) -> "EbdTableRow":
        """
        Validate that sub_rows either:
        - Has exactly 2 entries covering both True and False outcomes, OR
        - Has exactly 1 entry with result=None (transition node)
        """
        if len(self.sub_rows) == 2:
            # Check that both True and False occur
            results = {sr.check_result.result for sr in self.sub_rows}
            if results != {True, False}:
                raise ValueError(
                    "Exactly one of the entries in sub_rows has to have check_result.result True and False"
                )
        elif len(self.sub_rows) == 1:
            # Check that it's a transition node (result=None)
            if self.sub_rows[0].check_result.result is not None:
                raise ValueError("The subrow must not have a 'ja' or 'nein' distinction when there is only one subrow")
        else:
            raise ValueError(f"sub_rows must have 1 or 2 entries, got {len(self.sub_rows)}")

        # Validate use_cases if present
        if self.use_cases is not None and len(self.use_cases) == 0:
            raise ValueError("use_cases must have at least one entry if not None")

        return self

    def has_subsequent_steps(self) -> bool:
        """
        return true iff there are any subsequent steps after this row, meaning: this is not a loose end of the graph
        """
        for sub_row in self.sub_rows:
            if sub_row.check_result.subsequent_step_number:
                if sub_row.check_result.subsequent_step_number != "Ende":
                    # "Ende" actually occurs in E_0003 or E_0025
                    return True
        return False


class MultiStepInstruction(BaseModel):
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

    model_config = ConfigDict(extra="forbid")

    first_step_number_affected: StepNumber
    """
    The first step number/row that is affected by the instruction. If the instruction occurs before e.g. step '4',
    then '4' is the first_step_number_affected.
    """
    instruction_text: str
    """
    Contains the instruction as plain text.
    Examples:
    'Alle festgestellten Antworten sind anzugeben, soweit...'
    'Je Marktlokation erfolgen die nachstehenden Prüfungen'
    """


class EbdTable(BaseModel):
    """
    A Table is a list of rows + some metadata
    """

    model_config = ConfigDict(extra="forbid")

    metadata: EbdTableMetaData
    """
    meta data about the table.
    """
    rows: List[EbdTableRow]
    """
    rows are the body of the table;
    might have 0 rows, if the EBD exists but is just a paragraph of text, no real table
    """
    # pylint: disable=duplicate-code
    multi_step_instructions: Optional[List[MultiStepInstruction]] = None
    """
    If this is not None, it means that from some point in the EBD onwards, the user is thought to obey additional
    instructions. There might be more than one of these instructions in one EBD table.
    """

    @model_validator(mode="after")
    def validate_multi_step_instructions(self) -> "EbdTable":
        """Validate that multi_step_instructions has at least one entry if not None."""
        if self.multi_step_instructions is not None and len(self.multi_step_instructions) == 0:
            raise ValueError("multi_step_instructions must have at least one entry if not None")
        return self
