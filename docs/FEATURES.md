# Application Features

This document describes the high-level features provided by the `f1-data-companion-2` application.

## 1. Historical Data Retrieval
- Fetch complete session data from any Formula 1 Grand Prix.
- Support for Practice, Qualifying, and Race sessions.
- Detailed driver information, starting grids, and final results.

## 2. Advanced Analysis Tools
The application provides specialized tools for deep-diving into race data.

### Lap Time Analysis
- Generate clean, filtered lap time tables.
- Convert `Timedelta` lap times to seconds for easier visualization.
- Filter by specific drivers and lap ranges.

### Tire Degradation Tracking
- Analyze the impact of tire age on performance across different compounds.
- Automated data cleaning:
    - Excludes laps under Safety Car or Yellow Flag conditions.
    - Excludes pit entry and exit laps to ensure "clean" data.
- Aggregates performance using median values to minimize the impact of traffic or errors.

## 3. Real-time Telemetry Streaming
- Connect to live F1 timing feeds.
- Stream car telemetry, track status, and session information.
- Save live data to JSON for post-session analysis.
