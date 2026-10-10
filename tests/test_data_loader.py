
import pandas as pd
import pytest

from src.campaign_iq.data_loader import load_csv


def test_load_csv_successfully(tmp_path):
    csv_file = tmp_path / "campaign.csv"
    csv_file.write_text(
        "Campaign name,Impressions,Clicks\n"
        "Campaign A,1000,50\n"
        "Campaign B,2000,80\n",
        encoding="utf-8",
    )

    df = load_csv(csv_file)

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["Campaign name", "Impressions", "Clicks"]
    assert len(df) == 2
    assert df.iloc[0]["Campaign name"] == "Campaign A"


def test_load_csv_preserves_platform_specific_columns(tmp_path):
    csv_file = tmp_path / "meta_report.csv"
    csv_file.write_text(
        "Campaign name,Amount spent,Impressions\n"
        "Campaign A,125.50,1000\n",
        encoding="utf-8",
    )

    df = load_csv(csv_file)

    assert "Amount spent" in df.columns
    assert "Impressions" in df.columns


def test_load_csv_rejects_non_csv_file(tmp_path):
    file_path = tmp_path / "campaign.txt"
    file_path.write_text("example", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported file type"):
        load_csv(file_path)


def test_load_csv_rejects_missing_file(tmp_path):
    file_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_csv(file_path)


def test_load_csv_rejects_empty_file(tmp_path):
    file_path = tmp_path / "empty.csv"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        load_csv(file_path)


def test_load_csv_rejects_file_without_data_rows(tmp_path):
    file_path = tmp_path / "headers_only.csv"
    file_path.write_text("Campaign name,Clicks\n", encoding="utf-8")

    with pytest.raises(ValueError, match="no data rows"):
        load_csv(file_path)