
from src.campaign_iq.column_mapper import map_columns, normalize_header


def test_maps_known_column_names():
    result = map_columns(
        [
            "Campaign name",
            "Amount spent",
            "Impressions",
            "Clicks",
            "Conversions",
        ]
    )

    assert result.mapping == {
        "campaign_name": "Campaign name",
        "spend": "Amount spent",
        "impressions": "Impressions",
        "clicks": "Clicks",
        "conversions": "Conversions",
    }
    assert result.unmapped_columns == []
    assert result.conflicts == {}


def test_normalizes_case_spaces_and_underscores():
    assert normalize_header("  Campaign_Name  ") == "campaign name"
    assert normalize_header("AMOUNT   SPENT") == "amount spent"


def test_preserves_unknown_columns():
    result = map_columns(["Campaign name", "Custom metric"])

    assert result.mapping["campaign_name"] == "Campaign name"
    assert result.unmapped_columns == ["Custom metric"]


def test_flags_ambiguous_metric_headers():
    result = map_columns(["Clicks", "Link clicks", "Results"])

    assert result.mapping["clicks"] == "Clicks"
    assert "Link clicks" in result.review_columns
    assert "Results" in result.review_columns


def test_flags_conflicting_columns():
    result = map_columns(["Clicks", "clicks"])

    assert "clicks" not in result.mapping
    assert result.conflicts == {
        "clicks": ["Clicks", "clicks"]
    }


def test_maps_safe_aliases():
    result = map_columns(
        ["Campaign", "Campaign ID", "Reporting date", "Currency code"]
    )

    assert result.mapping == {
        "campaign_name": "Campaign",
        "campaign_id": "Campaign ID",
        "date": "Reporting date",
        "currency": "Currency code",
    }


def test_maps_spent_to_spend():
    result = map_columns(["Spent"])

    assert result.mapping["spend"] == "Spent"
    assert "Spent" not in result.unmapped_columns


def test_maps_total_conversion_to_conversions():
    result = map_columns(["Total_Conversion"])

    assert result.mapping["conversions"] == "Total_Conversion"
    assert "Total_Conversion" not in result.unmapped_columns