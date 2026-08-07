"""
Column Mapper

Responsibilities:
- Load column aliases from config/aliases.yaml.
- Map uploaded column names to the application's canonical names.
- Return a DataFrame with standardized column names.

Validation is handled separately by validator.py.
"""

# Standard library imports
from config.settings import ALIASES_FILE

# Third-party imports
import pandas as pd
import yaml



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
    alias -> canonical name.
    """

    lookup = {}

    for canonical, alias_list in aliases.items():

        lookup[canonical.lower()] = canonical

        for alias in alias_list:
            lookup[alias.lower()] = canonical

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

        canonical = lookup.get(column.lower())

        if canonical:
            renamed_columns[column] = canonical

    dataframe = dataframe.rename(columns=renamed_columns)

    return dataframe