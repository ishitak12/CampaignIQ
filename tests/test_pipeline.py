
import pandas as pd
import pytest

from src.campaign_iq.pipeline import analyze_campaign_csv


def test_pipeline_analyzes_campaign_csv(tmp_path):
    csv_path = tmp_path / "campaign.csv"

    pd.DataFrame(
        {
            "Impressions": [1000, 2000],
            "Clicks": [50, 100],
            "Spent": [25.0, 60.0],
            "Total_Conversion": [10, 20],
        }
    ).to_csv(csv_path, index=False)

    result = analyze_campaign_csv(str(csv_path))

    assert len(result.raw_data) == 2
    assert result.column_mapping["impressions"] == "Impressions"
    assert result.column_mapping["clicks"] == "Clicks"
    assert list(result.metrics.columns) == [
        "ctr",
        "cpc",
        "conversion_rate",
        "cpa",
    ]

    assert result.metrics.loc[0, "ctr"] == pytest.approx(5.0)
    assert result.metrics.loc[0, "cpc"] == pytest.approx(0.5)
    assert result.metrics.loc[0, "conversion_rate"] == pytest.approx(20.0)
    assert result.metrics.loc[0, "cpa"] == pytest.approx(2.5)


def test_pipeline_rejects_missing_required_columns(tmp_path):
    csv_path = tmp_path / "incomplete.csv"

    pd.DataFrame(
        {
            "Impressions": [1000],
            "Clicks": [50],
        }
    ).to_csv(csv_path, index=False)

    with pytest.raises(
        ValueError,
        match="Required columns could not be mapped",
    ):
        analyze_campaign_csv(str(csv_path))



def test_pipeline_preserves_original_data_and_standardizes_columns(
    tmp_path,
):
    csv_path = tmp_path / "campaign.csv"

    original = pd.DataFrame(
        {
            "Impressions": [1000],
            "Clicks": [50],
            "Spent": [25.0],
            "Total_Conversion": [10],
        }
    )
    original.to_csv(csv_path, index=False)

    result = analyze_campaign_csv(str(csv_path))

    # The original source columns must remain unchanged.
    assert list(result.raw_data.columns) == list(original.columns)
    pd.testing.assert_frame_equal(result.raw_data, original)

    # The canonical data should use standardized column names.
    assert {
        "impressions",
        "clicks",
        "spend",
        "conversions",
    }.issubset(result.canonical_data.columns)

