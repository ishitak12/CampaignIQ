
from pathlib import Path

import pandas as pd

from src.campaign_iq.data_validator import validate_campaign_data


DATASET_PATH = Path("data/KAG_conversion_data_raw.csv")


def test_real_dataset_loads_and_validates():
    """Check that the real advertising dataset can be validated."""
    df = pd.read_csv(DATASET_PATH)

    issues = validate_campaign_data(df)

    assert len(df) == 1143
    assert len(df.columns) == 11
    assert isinstance(issues, list)


def test_fault_injection_detects_negative_ad_spend():
    """Inject a negative spend value into a copy and check detection."""
    df = pd.read_csv(DATASET_PATH)

    # Work on a copy so the original dataset remains unchanged.
    faulty_df = df.copy(deep=True)

    # Deliberately introduce a data-quality error.
    faulty_df.loc[faulty_df.index[0], "Spent"] = -100.0

    issues = validate_campaign_data(faulty_df)

    assert any(
        issue.code == "negative_value"
        and issue.column == "Spent"
        and issue.row_index == faulty_df.index[0]
        for issue in issues
    )


def test_fault_injection_detects_clicks_exceeding_impressions():
    """Inject an impossible metric relationship and check detection."""
    df = pd.read_csv(DATASET_PATH)
    faulty_df = df.copy(deep=True)

    faulty_df.loc[faulty_df.index[0], "Clicks"] = (
        faulty_df.loc[faulty_df.index[0], "Impressions"] + 100
    )

    issues = validate_campaign_data(faulty_df)

    assert any(
        issue.code == "clicks_exceed_impressions"
        and issue.row_index == faulty_df.index[0]
        for issue in issues
    )


def test_fault_injection_does_not_modify_original_dataset():
    """Confirm injected errors do not affect the loaded source DataFrame."""
    df = pd.read_csv(DATASET_PATH)
    original_df = df.copy(deep=True)

    faulty_df = df.copy(deep=True)
    faulty_df.loc[faulty_df.index[0], "Spent"] = -100.0

    pd.testing.assert_frame_equal(df, original_df)
    assert faulty_df.loc[faulty_df.index[0], "Spent"] == -100.0