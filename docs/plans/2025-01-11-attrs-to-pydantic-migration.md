# Migration from attrs to Pydantic v2

## Overview

Migrate all data models from `attrs` to `Pydantic v2` for:
- Ecosystem alignment with other projects
- Built-in JSON serialization (replacing cattrs)
- Better validation features
- Performance improvements from Pydantic v2's Rust core

## Constraints

- **Full JSON compatibility**: Existing JSON files must work unchanged
- **Hard switch**: Remove attrs/cattrs entirely in one PR
- **Snapshots regenerated**: Accept snapshot changes, update via `tox -e snapshots`
- **Pydantic version**: Latest stable v2.x

## Design

### Base Configuration

Shared base class for consistent behavior:

```python
from pydantic import BaseModel, ConfigDict

class RebdhuhnBaseModel(BaseModel):
    model_config = ConfigDict(
        frozen=False,
        strict=True,
        extra="forbid",
    )
```

For frozen/hashable graph nodes (required by networkx):

```python
class FrozenBaseModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        strict=True,
        extra="forbid",
    )
```

### Abstract Base Class Pattern

`EbdGraphNode` remains an ABC with abstract `get_key()`:

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict

class EbdGraphNode(BaseModel, ABC):
    model_config = ConfigDict(frozen=True, extra="forbid")

    @abstractmethod
    def get_key(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.get_key()
```

### Validator Migration

| attrs | Pydantic v2 |
|-------|-------------|
| `@attrs.define` | `class Foo(BaseModel)` |
| `frozen=True` | `ConfigDict(frozen=True)` |
| `attrs.field(validator=matches_re(...))` | `Field(pattern=...)` or `Annotated[str, Field(pattern=...)]` |
| `attrs.validators.instance_of(str)` | Type annotation `str` |
| Complex cross-field validators | `@model_validator(mode="after")` |

Example regex validator:

```python
from typing import Annotated
from pydantic import Field

StepNumber = Annotated[str, Field(pattern=r"^\d+\*?$")]
```

Example cross-field validator:

```python
from pydantic import model_validator

class EbdTableRow(RebdhuhnBaseModel):
    sub_rows: list[EbdTableSubRow]

    @model_validator(mode="after")
    def check_sub_rows_coverage(self) -> "EbdTableRow":
        if len(self.sub_rows) == 2:
            results = {sr.check_result.result for sr in self.sub_rows}
            if results != {True, False}:
                raise ValueError("Sub rows must cover both True and False")
        elif len(self.sub_rows) == 1:
            if self.sub_rows[0].check_result.result is not None:
                raise ValueError("Single sub_row must have result=None")
        else:
            raise ValueError("Must have 1 or 2 sub_rows")
        return self
```

### JSON Serialization

```python
# Deserialization (JSON -> Model)
# Before: cattrs.structure(data, EbdTable)
# After:
table = EbdTable.model_validate(data)

# Serialization (Model -> JSON)
# Before: cattrs.unstructure(table)
# After:
data = table.model_dump(mode="json")
```

## Files to Modify

### Core models
- `src/rebdhuhn/models/ebd_table.py` - Convert all classes
- `src/rebdhuhn/models/ebd_graph.py` - Convert all classes
- `src/rebdhuhn/models/__init__.py` - Update imports if needed

### Dependencies
- `pyproject.toml` - Remove `attrs`, `cattrs`; add `pydantic>=2.0`
- `requirements.txt` - Run `pip-compile pyproject.toml`

### Tests
- `unittests/test_ebd_table_models.py` - Replace cattrs calls
- `unittests/test_malo_ident.py` - Replace cattrs calls
- `unittests/test_transitional_outcome.py` - Replace cattrs calls
- `unittests/test_e0055.py` - Replace cattrs calls

## Migration Steps

1. Update `pyproject.toml` - Remove `attrs`, `cattrs`; add `pydantic>=2.0`
2. Run `pip-compile pyproject.toml` - Regenerate `requirements.txt`
3. Migrate `ebd_table.py` - Convert all table models
4. Migrate `ebd_graph.py` - Convert all graph models
5. Update test files - Replace cattrs usage with Pydantic methods
6. Run `tox -e tests` - Verify tests pass (except snapshot mismatches)
7. Run `tox -e snapshots` - Regenerate all snapshots
8. Final verification - Run full test suite
