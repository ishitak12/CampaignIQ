
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
    """Calculate campaign metrics without modifying the input DataFrame."""

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

    # Convert a separate copy to numeric values.
    numeric_data = df[list(required_columns)].copy()

    for column in required_columns:
        try:
            numeric_data[column] = pd.to_numeric(
                numeric_data[column],
                errors="raise",
            )
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Column '{column}' must contain numeric values."
            ) from exc

    metrics = pd.DataFrame(index=df.index)

    # Click-through rate, expressed as a percentage.
    metrics["ctr"] = (
        _safe_divide(
            numeric_data["clicks"],
            numeric_data["impressions"],
        )
        * 100
    )

    # Cost per click.
    metrics["cpc"] = _safe_divide(
        numeric_data["spend"],
        numeric_data["clicks"],
    )

    # Conversion rate, expressed as a percentage.
    metrics["conversion_rate"] = (
        _safe_divide(
            numeric_data["conversions"],
            numeric_data["clicks"],
        )
        * 100
    )

    # Cost per acquisition/conversion.
    metrics["cpa"] = _safe_divide(
        numeric_data["spend"],
        numeric_data["conversions"],
    )

    return metrics