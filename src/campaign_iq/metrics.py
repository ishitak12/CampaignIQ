
import pandas as pd


def _safe_divide(
    numerator: pd.Series,
    denominator: pd.Series,
) -> pd.Series:
    """Divide safely, returning NaN when the denominator is zero."""
    result = numerator.div(denominator)
    return result.where(denominator.ne(0))


def calculate_campaign_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate campaign performance metrics without modifying the input."""

    required_columns = {
        "impressions",
        "clicks",
        "spend",
        "conversions",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    metrics = pd.DataFrame(index=df.index)

    # Click-through rate (CTR), expressed as a percentage.
    metrics["ctr"] = (
        _safe_divide(df["clicks"], df["impressions"]) * 100
    )

    # Cost per click (CPC).
    metrics["cpc"] = _safe_divide(
        df["spend"],
        df["clicks"],
    )

    # Conversion rate, expressed as a percentage.
    metrics["conversion_rate"] = (
        _safe_divide(df["conversions"], df["clicks"]) * 100
    )

    # Cost per acquisition (CPA).
    metrics["cpa"] = _safe_divide(
        df["spend"],
        df["conversions"],
    )

    return metrics