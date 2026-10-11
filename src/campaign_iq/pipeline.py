
from dataclasses import dataclass

import pandas as pd

from src.campaign_iq.column_mapper import map_columns
from src.campaign_iq.data_loader import load_csv
from src.campaign_iq.data_validator import ValidationIssue, validate_campaign_data
from src.campaign_iq.metrics import calculate_campaign_metrics


@dataclass
class CampaignAnalysisResult:
    """Store the outputs of a complete campaign analysis."""

    raw_data: pd.DataFrame
    canonical_data: pd.DataFrame
    column_mapping: dict[str, str]
    unmapped_columns: list[str]
    review_columns: dict[str, str]
    validation_issues: list[ValidationIssue]
    metrics: pd.DataFrame


def analyze_campaign_csv(file_path: str) -> CampaignAnalysisResult:
    """
    Load, map, validate, and calculate metrics for a campaign CSV.

    The original dataset is preserved, while analysis uses a separate
    DataFrame with standardized metric column names.
    """

    # 1. Load the original CSV.
    raw_data = load_csv(file_path)

    # 2. Detect recognized columns and possible mapping problems.
    mapping_result = map_columns(raw_data.columns)

    required_columns = {
        "impressions",
        "clicks",
        "spend",
        "conversions",
    }

    missing_columns = required_columns - set(mapping_result.mapping)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Cannot calculate campaign metrics. "
            f"Required columns could not be mapped: {missing}"
        )

    if mapping_result.conflicts:
        raise ValueError(
            "Ambiguous column mapping detected. "
            "Resolve the mapping conflicts before analysis."
        )

    # 3. Rename recognized columns in a separate DataFrame.
    rename_map = {
        source_column: canonical_column
        for canonical_column, source_column
        in mapping_result.mapping.items()
    }

    canonical_data = raw_data.rename( columns={
        source_column: canonical_column
        for canonical_column, source_column
        in mapping_result.mapping.items()
    }).copy()

    # 4. Validate the standardized data.
    validation_issues = validate_campaign_data(canonical_data)

    # 5. Calculate performance metrics.
    metrics_input = canonical_data.copy()

    metrics = calculate_campaign_metrics(metrics_input)

    return CampaignAnalysisResult(
        raw_data=raw_data,
        canonical_data=canonical_data,
        column_mapping=mapping_result.mapping,
        unmapped_columns=mapping_result.unmapped_columns,
        review_columns=mapping_result.review_columns,
        validation_issues=validation_issues,
        metrics=metrics,
    )

