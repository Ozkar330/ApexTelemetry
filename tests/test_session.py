import pytest
import livef1
import pandas as pd

@pytest.fixture
def sample_session():
    # Use a small session or a well-known one for testing
    # Note: This will perform actual network requests.
    # In a real CI environment, we should mock these.
    return livef1.get_session(2023, "Monaco", "Race")

def test_session_loading(sample_session):
    assert sample_session is not None
    assert sample_session.name == "Race"
    assert sample_session.meeting.name == "Monaco Grand Prix"

def test_drivers_loading(sample_session):
    assert len(sample_session.drivers) > 0
    # Verstappen's number is 1
    assert "1" in sample_session.drivers

def test_generate_silver_tables(sample_session):
    # This might be slow as it downloads several MBs of data
    sample_session.generate(silver=True)
    
    assert sample_session.laps is not None
    assert isinstance(sample_session.laps, pd.DataFrame)
    assert not sample_session.laps.empty
    
    assert sample_session.carTelemetry is not None
    assert isinstance(sample_session.carTelemetry, pd.DataFrame)
    assert not sample_session.carTelemetry.empty

def test_lap_data_columns(sample_session):
    if sample_session.laps is None:
        sample_session.generate(silver=True)
    
    expected_cols = ["DriverNo", "LapNo", "LapTime"]
    for col in expected_cols:
        assert col in sample_session.laps.columns
