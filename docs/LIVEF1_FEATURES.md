# LiveF1 Library Features

The `f1-data-companion-2` project utilizes the `livef1` library to interface with Formula 1 live timing and historical data. This document outlines the core features and data structures provided by the library.

## Core API Functions

The primary entry points for fetching data are:

- `get_season(season: int)`: Retrieves data for an entire F1 season.
- `get_meeting(season: int, meeting_identifier: str)`: Retrieves data for a specific Grand Prix weekend.
- `get_session(season: int, meeting_identifier: str, session_identifier: str)`: Retrieves data for a specific session (e.g., "Practice 1", "Qualifying", "Race").

## Session Object

The `Session` object is the central component for interacting with session data.

### Key Methods

- `session.load_session_data()`: Loads initial session metadata, including driver lists and available data topics.
- `session.generate(silver=True, gold=False)`: Processes raw "bronze" data into structured "silver" tables.
- `session.get_data(topic_names: list, parallel: bool)`: Fetches raw data for the specified topics.

### Data Levels

The library organizes data into three levels:

1.  **Bronze (Raw):** Direct feeds from F1 live timing (e.g., `CarData.z`, `Position.z`, `TimingData`).
2.  **Silver (Structured):** Processed and cleaned data frames (e.g., `laps`, `carTelemetry`).
3.  **Gold (Aggregated):** High-level analysis tables (e.g., driver performance metrics).

## Available Silver Tables

After calling `session.generate(silver=True)`, the following tables become available as Pandas DataFrames:

### 1. `session.laps`
Contains detailed information for every lap completed by every driver.
- **Columns:** `DriverNo`, `LapNo`, `LapTime`, `Compound`, `TyreAge`, `Sector1_Time`, `Sector2_Time`, `Sector3_Time`, `Speed_I1`, `Speed_FL`, etc.

### 2. `session.carTelemetry`
High-frequency sensor data merged with position information.
- **Columns:** `Utc`, `RPM`, `Speed`, `GearNo`, `Throttle`, `Brake`, `DRS`, `X`, `Y`, `Z`, `TrackRegion`, etc.

### 3. `session.raceControlMessages`
Messages issued by Race Control during the session.
- **Columns:** `Utc`, `Category`, `Scope`, `Flag`, `Message`, `Lap`, `RacingNumber`.

## Real-time Client

The library also provides a `RealF1Client` for streaming live data during an active F1 session.

```python
from livef1.adapters.realtime_client import RealF1Client

client = RealF1Client(
    topics=["CarData.z", "SessionInfo", "TrackStatus"],
    log_file_name="live_session.json"
)
client.run()
```

## Data Topics (Bronze)

Commonly used raw topics include:
- `CarData.z`: High-frequency car telemetry (RPM, Speed, Throttle, etc.).
- `Position.z`: GPS position data (X, Y, Z coordinates).
- `TimingData`: Live timing information (lap times, sector times, gaps).
- `SessionStatus`: Session state changes (Started, Finished, Red Flag).
- `TrackStatus`: Track condition updates (Yellow Flag, SC, VSC).
- `TyreStintSeries`: Information on tire compounds and stint lengths.
- `WeatherData`: Ambient and track temperatures, wind speed, etc.
