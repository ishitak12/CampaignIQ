
from dataclasses import dataclass
from typing import Literal

import pandas as pd


@dataclass
class ValidationIssue:
    """A data-quality issue found in a campaign report."""

    code: str
    message: str
    severity: Literal["error", "warning"] = "error"
    row_index: int | None = None
    column: str | None = None


COLUMN_ALIASES = {
    "impressions": ("impressions", "Impressions"),
    "clicks": ("clicks", "Clicks"),
    "spend": ("spend", "Spent"),
    "conversions": ("conversions", "Total_Conversion"),
    "approved_conversions": (
        "approved_conversions",
        "Approved_Conversion",
    ),
}


def _find_column(
    df: pd.DataFrame,
    canonical_name: str,
) -> str | None:
    """Find a supported source or canonical column name."""

    for column in COLUMN_ALIASES[canonical_name]:
        if column in df.columns:
            return column

    return None


def validate_campaign_data(
    df: pd.DataFrame,
) -> list[ValidationIssue]:
    """
    Validate campaign data using canonical or recognized legacy names.

    Reports issues without modifying the input DataFrame.
    """

    issues: list[ValidationIssue] = []

    # 1. Report missing values in any supplied column.
    for column in df.columns:
        for row_index in df.index[df[column].isna()]:
            issues.append(
                ValidationIssue(
                    code="missing_value",
                    message=f"Missing value in column '{column}'.",
                    row_index=int(row_index),
                    column=column,
                )
            )

    # 2. Check that advertising metrics are non-negative.
    for name in (
        "impressions",
        "clicks",
        "spend",
        "conversions",
        "approved_conversions",
    ):
        column = _find_column(df, name)

        if column is None:
            continue

        values = pd.to_numeric(df[column], errors="coerce")

        for row_index in df.index[values < 0]:
            issues.append(
                ValidationIssue(
                    code="negative_value",
                    message=f"Negative value in column '{column}'.",
                    row_index=int(row_index),
                    column=column,
                )
            )

    # 3. Clicks should not exceed impressions.
    clicks_column = _find_column(df, "clicks")
    impressions_column = _find_column(df, "impressions")

    if clicks_column and impressions_column:
        clicks = pd.to_numeric(
            df[clicks_column], errors="coerce"
        )
        impressions = pd.to_numeric(
            df[impressions_column], errors="coerce"
        )

        invalid_rows = df.index[
            clicks.notna()
            & impressions.notna()
            & (clicks > impressions)
        ]

        for row_index in invalid_rows:
            issues.append(
                ValidationIssue(
                    code="clicks_exceed_impressions",
                    message="Clicks exceed impressions.",
                    row_index=int(row_index),
                )
            )

    # 4. Approved conversions should not exceed total conversions.
    approved_column = _find_column(df, "approved_conversions")
    conversions_column = _find_column(df, "conversions")

    if approved_column and conversions_column:
        approved = pd.to_numeric(
            df[approved_column], errors="coerce"
        )
        conversions = pd.to_numeric(
            df[conversions_column], errors="coerce"
        )

        invalid_rows = df.index[
            approved.notna()
            & conversions.notna()
            & (approved > conversions)
        ]

        for row_index in invalid_rows:
            issues.append(
                ValidationIssue(
                    code="approved_exceed_total",
                    message="Approved conversions exceed total conversions.",
                    row_index=int(row_index),
                )
            )

    # 5. Flag conversions with zero clicks for review.
    if clicks_column and conversions_column:
        clicks = pd.to_numeric(
            df[clicks_column], errors="coerce"
        )
        conversions = pd.to_numeric(
            df[conversions_column], errors="coerce"
        )

        suspicious_rows = df.index[
            clicks.notna()
            & conversions.notna()
            & (clicks == 0)
            & (conversions > 0)
        ]

        for row_index in suspicious_rows:
            issues.append(
                ValidationIssue(
                    code="conversions_without_clicks",
                    message=(
                        "Conversions are positive despite zero clicks; "
                        "review attribution and metric definitions."
                    ),
                    severity="warning",
                    row_index=int(row_index),
                    column=f"{clicks_column}, {conversions_column}",
                )
            )

    return issues
