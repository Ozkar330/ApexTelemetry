import pytest
import pandas as pd
import numpy as np
from src.analysis import get_lap_times_table, analyze_tire_degradation

@pytest.fixture
def mock_laps_data():
    data = {
        'DriverNo': ['1', '1', '1', '14', '14', '14'],
        'LapNo': [1.0, 2.0, 3.0, 1.0, 2.0, 3.0],
        'LapTime': pd.to_timedelta(['00:01:20', '00:01:19', '00:01:18', '00:01:21', '00:01:20', '00:01:19']),
        'Compound': ['SOFT', 'SOFT', 'SOFT', 'MEDIUM', 'MEDIUM', 'MEDIUM'],
        'TyreAge': [1.0, 2.0, 3.0, 1.0, 2.0, 3.0],
        'TrackStatus': ['1', '1', '1', '1', '1', '1'],
        'PitIn': [None, None, None, None, None, None],
        'PitOut': [None, None, None, None, None, None]
    }
    return pd.DataFrame(data)

def test_get_lap_times_table_filtering(mock_laps_data):
    # Filter by driver
    res = get_lap_times_table(mock_laps_data, drivers=['1'])
    assert all(res['DriverNo'] == '1')
    assert len(res) == 3
    
    # Filter by lap
    res = get_lap_times_table(mock_laps_data, laps=[1.0, 2.0])
    assert len(res) == 4
    assert 3.0 not in res['LapNo'].values

def test_get_lap_times_table_seconds(mock_laps_data):
    res = get_lap_times_table(mock_laps_data)
    assert 'LapTime_Seconds' in res.columns
    assert res.loc[res['LapNo'] == 1.0, 'LapTime_Seconds'].iloc[0] == 80.0

def test_tire_degradation_filtering(mock_laps_data):
    # Add a "dirty" lap
    dirty_data = mock_laps_data.copy()
    dirty_data.loc[0, 'TrackStatus'] = '2' # Yellow flag
    
    res = analyze_tire_degradation(dirty_data)
    # The first lap should be excluded
    assert not ((res['Compound'] == 'SOFT') & (res['TyreAge'] == 1.0)).any()

def test_tire_degradation_grouping(mock_laps_data):
    res = analyze_tire_degradation(mock_laps_data)
    assert len(res) == 6 # Each lap is unique in our mock data
    assert 'Median_Seconds' in res.columns
