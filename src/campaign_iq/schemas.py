from __future__ import annotations

from dataclasses import dataclass
from datetime import date as date_type

@dataclass
class CampaignRecord:
    """
    Standard internal representation of an advertising campaign record.
    """

    # Identify the platform that supplied the data.
    source_platform: str

    # Campaign identifiers and reporting period.
    campaign_name: str | None = None
    campaign_id: str | None = None
    date: date_type | None = None

    # Performance metrics.
    impressions: int | None = None
    clicks: int | None = None
    spend: float | None = None
    conversions: float | None = None
    revenue: float | None = None

    # Currency used for monetary metrics.
    currency: str | None = None
