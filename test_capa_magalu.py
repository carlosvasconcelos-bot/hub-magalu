import pytest
import pandas as pd
from unittest.mock import patch
from capa_magalu import extract_sheet_csv_url, carregar_links_google_sheets, LINKS_MAGALU

def test_extract_sheet_csv_url_standard():
    url = "https://docs.google.com/spreadsheets/d/1vcGVtgxeNOIPKYKTCa5Y47UQE-SLvfcAI0S1uQBXXAs/edit?gid=454063207#gid=454063207"
    expected = "https://docs.google.com/spreadsheets/d/1vcGVtgxeNOIPKYKTCa5Y47UQE-SLvfcAI0S1uQBXXAs/export?format=csv&gid=454063207"
    assert extract_sheet_csv_url(url) == expected

def test_extract_sheet_csv_url_no_gid():
    url = "https://docs.google.com/spreadsheets/d/1vcGVtgxeNOIPKYKTCa5Y47UQE-SLvfcAI0S1uQBXXAs/edit"
    expected = "https://docs.google.com/spreadsheets/d/1vcGVtgxeNOIPKYKTCa5Y47UQE-SLvfcAI0S1uQBXXAs/export?format=csv&gid=0"
    assert extract_sheet_csv_url(url) == expected

def test_carregar_links_fallback_on_error():
    # Attempting to load an unaccessible URL should return fallback links and an error message
    links, err = carregar_links_google_sheets("https://invalid-url-that-does-not-exist.com")
    assert links == LINKS_MAGALU
    assert err is not None

def test_carregar_links_google_sheets_success():
    mock_df = pd.DataFrame([
        {"title": "Link 1", "description": "Desc 1", "icon": "⭐", "link": "https://example.com/1"},
        {"title": "Link 2", "description": "Desc 2", "icon": "🚀", "link": "https://example.com/2"}
    ])

    with patch("pandas.read_csv", return_value=mock_df):
        links, err = carregar_links_google_sheets("https://docs.google.com/spreadsheets/d/dummy/edit")
        assert err is None
        assert len(links) == 2
        assert links[0]["titulo"] == "Link 1"
        assert links[0]["desc"] == "Desc 1"
        assert links[0]["icone"] == "⭐"
        assert links[0]["url"] == "https://example.com/1"
