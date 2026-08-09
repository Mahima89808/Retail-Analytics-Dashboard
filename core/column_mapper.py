"""
Column Mapper

Responsibilities:
- Load column aliases from config/aliases.yaml.
- Map uploaded column names to the application's canonical names.
- Return a DataFrame with standardized column names.

Matching is case-insensitive and ignores spaces, underscores, and
hyphens, so "Order Date", "order_date", "OrderDate", and "order-date"
all resolve to the same canonical column. (Adopted per design review —
previously exact lowercase matching only.)

Validation is handled separately by validator.py.
"""

# Standard library imports
import re

from config.settings import ALIASES_FILE

# Third-party imports
import pandas as pd
import yaml


def _normalize(text: str) -> str:
    """
    Normalize a column name for matching: lowercase, and strip spaces,
    underscores, and hyphens. Used for both alias keys and uploaded
    column names so matching is insensitive to spacing/casing style.
    """

    return re.sub(r"[\s_\-]+", "", text.lower())


def _load_aliases() -> dict[str, list[str]]:
    """
    Load aliases from aliases.yaml.
    """

    with open(ALIASES_FILE, "r", encoding="utf-8") as file:
        aliases = yaml.safe_load(file)

    return aliases


def _build_lookup(aliases: dict[str, list[str]]) -> dict[str, str]:
    """
    Build a lookup dictionary:
    normalized alias -> canonical name.
    """

    lookup = {}

    for canonical, alias_list in aliases.items():

        lookup[_normalize(canonical)] = canonical

        for alias in alias_list:
            lookup[_normalize(alias)] = canonical

    return lookup


def map_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Rename uploaded columns to canonical column names.

    Parameters
    ----------
    dataframe : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
    """

    aliases = _load_aliases()

    lookup = _build_lookup(aliases)

    renamed_columns = {}

    for column in dataframe.columns:

        canonical = lookup.get(_normalize(column))

        if canonical:
            renamed_columns[column] = canonical

    dataframe = dataframe.rename(columns=renamed_columns)

    return dataframe