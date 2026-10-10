
from collections.abc import Iterable
from dataclasses import dataclass, field
import re


# Only map aliases whose meaning is sufficiently clear.
# We can add platform-specific rules after examining real reports.
COLUMN_ALIASES = {
    "campaign_name": {
        "campaign name",
        "campaign",
    },
    "campaign_id": {
        "campaign id",
    },
    "date": {
        "date",
        "reporting date",
    },
    "impressions": {
        "impressions",
    },
    "clicks": {
        "clicks",
    },
    "spend": {
        "spend",
        "amount spent",
        "spent"
    },
    "conversions": {
        "conversions",
        "total conversion"
    },
    "revenue": {
        "revenue",
    },
    "currency": {
        "currency",
        "currency code",
    },
}


# These names may refer to different metrics depending on
# the advertising platform or report configuration.
HEADERS_REQUIRING_REVIEW = {
    "link clicks": "Confirm whether link clicks should be treated separately from clicks.",
    "outbound clicks": "Outbound clicks may differ from the platform's general click metric.",
    "results": "Results can represent different actions depending on the report.",
    "actions": "Actions may contain multiple conversion or engagement types.",
    "cost": "Confirm what this cost field measures before mapping it to spend.",
    "conversion value": "Confirm the definition and currency before mapping to revenue.",
}


@dataclass
class ColumnMappingResult:
    """Describes proposed mappings without changing the source data."""

    mapping: dict[str, str] = field(default_factory=dict)
    unmapped_columns: list[str] = field(default_factory=list)
    conflicts: dict[str, list[str]] = field(default_factory=dict)
    review_columns: dict[str, str] = field(default_factory=dict)


def normalize_header(header: object) -> str:
    """Normalize case, surrounding whitespace, and repeated spaces/underscores."""
    text = str(header).strip().casefold()
    return re.sub(r"[\s_]+", " ", text)


def map_columns(columns: Iterable[str]) -> ColumnMappingResult:
    """
    Match source headers to known CampaignIQ fields.

    Ambiguous headers are flagged for review. If multiple source columns
    match the same canonical field, that field is left unmapped.

    The function only examines column names; it does not change data values.
    """
    aliases_to_fields = {
        normalize_header(alias): canonical_field
        for canonical_field, aliases in COLUMN_ALIASES.items()
        for alias in aliases
    }

    result = ColumnMappingResult()
    candidates: dict[str, list[str]] = {}

    for original_header in columns:
        normalized = normalize_header(original_header)

        if normalized in HEADERS_REQUIRING_REVIEW:
            result.review_columns[str(original_header)] = (
                HEADERS_REQUIRING_REVIEW[normalized]
            )
            continue

        canonical_field = aliases_to_fields.get(normalized)

        if canonical_field is None:
            result.unmapped_columns.append(str(original_header))
            continue

        candidates.setdefault(canonical_field, []).append(
            str(original_header)
        )

    for canonical_field, source_headers in candidates.items():
        if len(source_headers) == 1:
            result.mapping[canonical_field] = source_headers[0]
        else:
            result.conflicts[canonical_field] = source_headers

    return result