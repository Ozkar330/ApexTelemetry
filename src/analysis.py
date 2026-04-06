import livef1
import pandas as pd
import numpy as np

def get_lap_times_table(laps_df, drivers=None, laps=None):
    """
    Generate a clean lap time table for specified drivers and laps.
    
    Parameters:
    - laps_df: The session.laps DataFrame.
    - drivers: List of DriverNo (str) to include. If None, all drivers.
    - laps: List of LapNo (int) to include. If None, all laps.
    
    Returns:
    - Long-form DataFrame filtered by drivers and laps.
    """
    df = laps_df.copy()
    
    # Filter drivers
    if drivers:
        df = df[df['DriverNo'].isin(drivers)]
        
    # Filter laps
    if laps:
        df = df[df['LapNo'].isin(laps)]
        
    # Select relevant columns
    df = df[['DriverNo', 'LapNo', 'LapTime']]
    
    # Optional: Convert LapTime (Timedelta) to total seconds for easier charting
    df['LapTime_Seconds'] = df['LapTime'].dt.total_seconds()
    
    return df

def analyze_tire_degradation(laps_df, export_csv=True):
    """
    Analyze lap time trends relative to TyreAge and Compound.
    Filters out "dirty" laps (e.g., pit stops, safety cars, outliers).
    """
    df = laps_df.copy()
    
    # Save raw processed laps for debugging
    if export_csv:
        df.to_csv("debug_laps_full.csv", index=False)
        print("Debug: Full laps data exported to debug_laps_full.csv")

    # 1. Basic filtering for "clean" laps
    # TrackStatus '1' = Green Flag
    df = df[
        (df['TrackStatus'] == '1') & 
        (df['PitIn'].isna()) & 
        (df['PitOut'].isna()) &
        (df['LapTime'].notna())
    ].copy()
    
    # 2. Convert LapTime to seconds for numerical filtering
    df['LapTime_Seconds'] = df['LapTime'].dt.total_seconds()

    # 3. Aggressive Outlier Removal (Z-Score or Percentile)
    # Remove laps that are > 7% slower than the driver's own median
    # (Accounting for the fact that some tracks have more variance)
    driver_medians = df.groupby('DriverNo')['LapTime_Seconds'].transform('median')
    df = df[df['LapTime_Seconds'] < (driver_medians * 1.07)]

    # 4. Group by Compound and TyreAge
    degradation = df.groupby(['Compound', 'TyreAge'])['LapTime_Seconds'].agg(['median', 'mean', 'count']).reset_index()
    degradation.columns = ['Compound', 'TyreAge', 'Median_Seconds', 'Mean_Seconds', 'LapCount']
    
    # Sort for better readability
    degradation = degradation.sort_values(['Compound', 'TyreAge'])
    
    if export_csv:
        degradation.to_csv("debug_tire_degradation.csv", index=False)
        print("Debug: Tire degradation summary exported to debug_tire_degradation.csv")

    return degradation

def calculate_delta_to_leader(laps_df):
    """
    Calculate the gap from each driver to the leader for every lap.
    """
    df = laps_df.copy()
    
    # 1. Clean data: Valid laps only
    df = df[df['LapTime'].notna()].copy()
    df['LapTime_Seconds'] = df['LapTime'].dt.total_seconds()
    
    # 2. Calculate cumulative race time for each driver
    # We sort by Driver and LapNo first to ensure cumsum is correct
    df = df.sort_values(['DriverNo', 'LapNo'])
    df['RaceTime'] = df.groupby('DriverNo')['LapTime_Seconds'].cumsum()
    
    # 3. Identify the leader for each lap (minimum RaceTime)
    leader_times = df.groupby('LapNo')['RaceTime'].min().reset_index()
    leader_times.columns = ['LapNo', 'LeaderTime']
    
    # 4. Merge back and calculate delta
    df = df.merge(leader_times, on='LapNo')
    df['DeltaToLeader'] = df['RaceTime'] - df['LeaderTime']
    
    return df[['DriverNo', 'LapNo', 'RaceTime', 'DeltaToLeader', 'Compound', 'TyreAge']]

if __name__ == "__main__":
    # Example usage:
    print("Loading Monaco 2023 session...")
    race = livef1.get_session(2023, "Monaco", "Race")
    race.generate(silver=True)
    laps_data = race.laps
    
    # 1. Lap Time Table for top drivers
    print("\nLap Time Table (Top 3 Drivers, first 5 laps):")
    top_drivers = ["1", "14", "31"] # Verstappen, Alonso, Ocon
    lap_table = get_lap_times_table(laps_data, drivers=["1"])
    #lap_table = get_lap_times_table(laps_data, drivers=top_drivers, laps=[1, 2, 3, 4, 5])
    print(lap_table)
    
    # 2. Tire Degradation
    print("\nTire Degradation Analysis (Median Lap Time by Compound and Age):")
    tire_deg = analyze_tire_degradation(laps_data)
    print(tire_deg)
