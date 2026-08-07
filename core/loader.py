"""
Dataset Loader

Responsibilities:
- Load CSV and Excel files into a pandas DataFrame.
- Support CSV (.csv) and Excel (.xlsx) formats.
- Raise descriptive exceptions for unsupported or invalid files.
"""

# Third-party imports
import pandas as pd


SUPPORTED_EXTENSIONS = (".csv", ".xlsx")


def load_dataset(uploaded_file) -> pd.DataFrame:
    """
    Load an uploaded dataset into a pandas DataFrame.

    Parameters
    ----------
    uploaded_file
        Streamlit UploadedFile object.

    Returns
    -------
    pandas.DataFrame
        Loaded dataset.

    Raises
    ------
    ValueError
        If the file format is unsupported or the dataset is empty.

    RuntimeError
        If the dataset cannot be read.
    """

    if uploaded_file is None:
        raise ValueError("No file was provided.")

    filename = uploaded_file.name.lower()

    if not filename.endswith(SUPPORTED_EXTENSIONS):
        raise ValueError(
            "Unsupported file format. Please upload a CSV or XLSX file."
        )

    try:
        if filename.endswith(".csv"):
            dataframe = pd.read_csv(uploaded_file)

        else:
            dataframe = pd.read_excel(uploaded_file)

    except Exception as error:
        raise RuntimeError(
            f"Failed to load dataset: {error}"
        ) from error

    if dataframe.empty:
        raise ValueError("The uploaded dataset is empty.")

    return dataframe