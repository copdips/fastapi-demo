"""Both layouts must describe the same database schema.

There is one database and it is migrated from the domain-based metadata
(migrations/env.py). If the layer-based models drift, the running app would
silently disagree with the tables it reads, so this test fails on any
difference in table names, column names, types, nullability, primary keys or
column order.
"""

from typing import TYPE_CHECKING

import app_domain_based_sqlalchemy.app_email.models
import app_domain_based_sqlalchemy.app_tag.models
import app_domain_based_sqlalchemy.app_task.models
import app_domain_based_sqlalchemy.app_team.models
import app_domain_based_sqlalchemy.app_user.models  # noqa: F401
from app_domain_based_sqlalchemy.app_common.models import Base
from app_layer_based_sqlmodel.models.db import SQLModel

if TYPE_CHECKING:
    from sqlalchemy import MetaData


def _describe(
    metadata: MetaData,
) -> dict[str, list[tuple[str, str, bool | None, bool]]]:
    return {
        table.name: [
            (column.name, str(column.type), column.nullable, column.primary_key)
            for column in table.columns
        ]
        for table in metadata.sorted_tables
    }


def test_both_layouts_describe_the_same_schema():
    assert _describe(SQLModel.metadata) == _describe(Base.metadata)
