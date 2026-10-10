
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


NON_NEGATIVE_COLUMNS = {
    "Impressions",
    "Clicks",
    "Spent",
    "Total_Conversion",
    "Approved_Conversion",
}


def validate_campaign_data(df: pd.DataFrame) -> list[ValidationIssue]:
    """
    Check campaign data for basic quality issues.

    This function reports problems without modifying the input DataFrame.
    """
    issues: list[ValidationIssue] = []

    # 1. Report missing values in the supplied data.
    for column in df.columns:
        missing_rows = df.index[df[column].isna()].tolist()

        for row_index in missing_rows:
            issues.append(
                ValidationIssue(
                    code="missing_value",
                    message=f"Missing value in column '{column}'.",
                    row_index=int(row_index),
                    column=column,
                )
            )

    # 2. Check that selected advertising metrics are non-negative.
    for column in NON_NEGATIVE_COLUMNS:
        if column not in df.columns:
            continue

        numeric_values = pd.to_numeric(df[column], errors="coerce")

        for row_index in df.index[numeric_values < 0]:
            issues.append(
                ValidationIssue(
                    code="negative_value",
                    message=f"Negative value in column '{column}'.",
                    row_index=int(row_index),
                    column=column,
                )
            )

    # 3. Clicks should not exceed impressions for comparable metrics.
    if {"Clicks", "Impressions"}.issubset(df.columns):
        clicks = pd.to_numeric(df["Clicks"], errors="coerce")
        impressions = pd.to_numeric(df["Impressions"], errors="coerce")

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

    # 4. Approved conversions should not exceed total conversions
    # when both columns use compatible definitions and units.
    if {"Approved_Conversion", "Total_Conversion"}.issubset(df.columns):
        approved = pd.to_numeric(
            df["Approved_Conversion"], errors="coerce"
        )
        total = pd.to_numeric(df["Total_Conversion"], errors="coerce")

        invalid_rows = df.index[
            approved.notna()
            & total.notna()
            & (approved > total)
        ]

        for row_index in invalid_rows:
            issues.append(
                ValidationIssue(
                    code="approved_exceed_total",
                    message="Approved conversions exceed total conversions.",
                    row_index=int(row_index),
                )
            )

    # 5. Flag conversions recorded with zero clicks for review.
    # This is a warning, not proof of invalid data.
    if {"Clicks", "Total_Conversion"}.issubset(df.columns):
        clicks = pd.to_numeric(df["Clicks"], errors="coerce")
        conversions = pd.to_numeric(
            df["Total_Conversion"], errors="coerce"
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
                )
            )

    return issues