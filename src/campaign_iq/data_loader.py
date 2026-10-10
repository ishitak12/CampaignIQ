
from pathlib import Path

import pandas as pd


def load_csv(file_path: str | Path) -> pd.DataFrame:
    """
    Load a campaign report from a CSV file.

    Returns the raw data as a pandas DataFrame.
    Platform-specific column mapping and data validation
    are handled separately.
    """
    path = Path(file_path)

    if path.suffix.lower() != ".csv":
        raise ValueError("Unsupported file type. Please provide a CSV file.")

    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError as exc:
        raise ValueError("The CSV file is empty or has no readable columns.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError("The CSV file could not be parsed. Check its format.") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(
            "The CSV file encoding could not be read. Please check the file encoding."
        ) from exc

    if df.empty:
        raise ValueError("The CSV file contains no data rows.")

    if len(df.columns) == 0:
        raise ValueError("The CSV file has no columns.")

    return df