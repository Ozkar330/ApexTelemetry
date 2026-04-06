import livef1
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.analysis import get_lap_times_table, analyze_tire_degradation

def plot_lap_times(laps_df, drivers=None, title="Lap Time Comparison"):
    """
    Generate an interactive line chart for lap times by driver.
    """
    df = get_lap_times_table(laps_df, drivers=drivers)
    
    # Drop NaT/NaN values for clean plotting
    df = df.dropna(subset=['LapTime_Seconds'])
    
    fig = px.line(
        df, 
        x="LapNo", 
        y="LapTime_Seconds", 
        color="DriverNo",
        title=title,
        labels={"LapTime_Seconds": "Lap Time (s)", "LapNo": "Lap Number", "DriverNo": "Driver #"},
        markers=True,
        template="plotly_dark"
    )
    
    fig.update_layout(hovermode="x unified")
    return fig

def plot_tire_degradation(laps_df, title="Tire Degradation Analysis"):
    """
    Generate an interactive scatter plot with trend lines for tire degradation.
    """
    df = analyze_tire_degradation(laps_df)
    
    fig = px.scatter(
        df, 
        x="TyreAge", 
        y="Median_Seconds", 
        color="Compound",
        size="LapCount", # Larger points = more data
        trendline="lowess", # Locally Weighted Scatterplot Smoothing
        title=title,
        labels={"Median_Seconds": "Median Lap Time (s)", "TyreAge": "Tire Age (Laps)", "LapCount": "Sample Size"},
        template="plotly_dark"
    )
    
    fig.update_layout(hovermode="closest")
    return fig

if __name__ == "__main__":
    # Settings for debugging
    YEAR = 2023
    GP = "Spanish"
    SESSION = "Race"

    print(f"Fetching data for {GP} {YEAR} {SESSION}...")
    race = livef1.get_session(YEAR, GP, SESSION)
    race.generate(silver=True)
    laps_data = race.laps

    
    # 1. Plot Lap Times for top 5 drivers
    # Fetching top 5 from session results for accuracy
    top_5 = race.sessionResults['No.'].head(5).astype(str).tolist()
    print(f"Generating Lap Time chart for drivers: {top_5}...")
    fig_laps = plot_lap_times(laps_data, drivers=top_5, title="Spanish 2023: Top 5 Driver Lap Times")
    fig_laps.write_html("lap_times.html")
    print("Saved: lap_times.html")

    # 2. Plot Tire Degradation
    print("Generating Tire Degradation chart...")
    fig_tire = plot_tire_degradation(laps_data, title=f"{GP} {YEAR}: Tire Degradation Trends")
    fig_tire.write_html("tire_degradation.html")
    print("Saved: tire_degradation.html")


    print("\nVisualizations complete! Open the .html files in your browser to view.")
