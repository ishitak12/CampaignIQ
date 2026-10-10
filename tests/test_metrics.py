
import pandas as pd
import pytest

from src.campaign_iq.metrics import calculate_campaign_metrics


def test_calculates_campaign_metrics_correctly():
    df = pd.DataFrame(
        {
            "impressions": [1000],
            "clicks": [100],
            "spend": [50.0],
            "conversions": [10],
        }
    )

    result = calculate_campaign_metrics(df)

    assert result.loc[0, "ctr"] == pytest.approx(10.0)
    assert result.loc[0, "cpc"] == pytest.approx(0.5)
    assert result.loc[0, "conversion_rate"] == pytest.approx(10.0)
    assert result.loc[0, "cpa"] == pytest.approx(5.0)


def test_zero_impressions_returns_nan_ctr():
    df = pd.DataFrame(
        {
            "impressions": [0],
            "clicks": [0],
            "spend": [0.0],
            "conversions": [0],
        }
    )

    result = calculate_campaign_metrics(df)

    assert pd.isna(result.loc[0, "ctr"])


def test_zero_clicks_returns_nan_cpc_and_conversion_rate():
    df = pd.DataFrame(
        {
            "impressions": [1000],
            "clicks": [0],
            "spend": [20.0],
            "conversions": [0],
        }
    )

    result = calculate_campaign_metrics(df)

    assert pd.isna(result.loc[0, "cpc"])
    assert pd.isna(result.loc[0, "conversion_rate"])


def test_zero_conversions_returns_nan_cpa():
    df = pd.DataFrame(
        {
            "impressions": [1000],
            "clicks": [100],
            "spend": [20.0],
            "conversions": [0],
        }
    )

    result = calculate_campaign_metrics(df)

    assert pd.isna(result.loc[0, "cpa"])


def test_missing_required_column_raises_error():
    df = pd.DataFrame(
        {
            "impressions": [1000],
            "clicks": [100],
            "spend": [50.0],
        }
    )

    with pytest.raises(ValueError, match="conversions"):
        calculate_campaign_metrics(df)


def test_original_dataframe_is_not_modified():
    df = pd.DataFrame(
        {
            "impressions": [1000],
            "clicks": [100],
            "spend": [50.0],
            "conversions": [10],
        }
    )
    original = df.copy(deep=True)

    calculate_campaign_metrics(df)

    pd.testing.assert_frame_equal(df, original)