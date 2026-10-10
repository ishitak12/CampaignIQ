
import pandas as pd

from src.campaign_iq.data_validator import validate_campaign_data


def test_valid_data_has_no_issues():
    df = pd.DataFrame(
        {
            "Impressions": [100, 200],
            "Clicks": [10, 20],
            "Spent": [5.0, 10.0],
            "Total_Conversion": [2, 4],
            "Approved_Conversion": [1, 3],
        }
    )

    issues = validate_campaign_data(df)

    assert issues == []


def test_flags_negative_metrics():
    df = pd.DataFrame(
        {
            "Impressions": [100],
            "Clicks": [-1],
            "Spent": [-5.0],
            "Total_Conversion": [2],
            "Approved_Conversion": [1],
        }
    )

    issues = validate_campaign_data(df)
    codes = {issue.code for issue in issues}

    assert "negative_value" in codes


def test_flags_clicks_greater_than_impressions():
    df = pd.DataFrame(
        {
            "Impressions": [10],
            "Clicks": [15],
        }
    )

    issues = validate_campaign_data(df)

    assert any(issue.code == "clicks_exceed_impressions" for issue in issues)


def test_flags_approved_conversions_greater_than_total():
    df = pd.DataFrame(
        {
            "Total_Conversion": [2],
            "Approved_Conversion": [3],
        }
    )

    issues = validate_campaign_data(df)

    assert any(
        issue.code == "approved_exceed_total" for issue in issues
    )


def test_missing_metric_values_are_reported():
    df = pd.DataFrame(
        {
            "Impressions": [100, None],
            "Clicks": [10, 5],
        }
    )

    issues = validate_campaign_data(df)

    assert any(issue.code == "missing_value" for issue in issues)


def test_zero_clicks_with_conversions_is_a_warning():
    df = pd.DataFrame(
        {
            "Clicks": [0],
            "Total_Conversion": [1],
        }
    )

    issues = validate_campaign_data(df)

    assert any(
        issue.code == "conversions_without_clicks"
        and issue.severity == "warning"
        for issue in issues
    )


def test_validation_does_not_modify_source_data():
    df = pd.DataFrame(
        {
            "Impressions": [100],
            "Clicks": [150],
        }
    )
    original = df.copy(deep=True)

    validate_campaign_data(df)

    pd.testing.assert_frame_equal(df, original)