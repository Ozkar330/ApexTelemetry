# 🏎️ ApexTelemetry

An interactive, real-time-capable Formula 1 data analytics dashboard. This project provides a sophisticated interface for visualizing historical race data and live telemetry using the `livef1` ecosystem.

## 🚀 Project Overview

**ApexTelemetry** is designed to bridge the gap between raw timing data and actionable insights. Whether analyzing historical races for performance trends or tracking a live session, the application provides a high-fidelity, interactive experience for F1 enthusiasts and data analysts.

### Key Features
- **Interactive Dashboard:** Built with Dash and Plotly for a modern, responsive user experience.
- **Historical Session Replay:** Load any session from 2018 onwards and "replay" it with full telemetry sync.
- **Live Track Map:** Visualize car positions on a dynamically generated track layout with sector highlights.
- **Sector Performance Analysis:** Real-time tracking of S1, S2, and S3 times with performance-based color coding (Purple/Green).
- **Advanced Telemetry:** Integrated charts for lap times and gaps to the leader.
- **Driver Filtering:** Focus on specific drivers to analyze head-to-head performance.

## 🛠️ Tech Stack

- **Backend/Analytics:** Python, Pandas, NumPy, Scipy
- **Visualization:** Plotly, Dash, Dash Bootstrap Components
- **Data Source:** [livef1](https://github.com/GoktugOcal/LiveF1) (API wrapper for F1 timing data)
- **Testing:** Pytest

## 🏛️ System Architecture

The application is modularly designed to separate data acquisition, processing, and visualization:

1.  **Data Layer (`livef1`):** Handles communication with F1's SignalR and REST APIs.
2.  **Analysis Engine (`src/analysis.py`):** Processes raw telemetry into high-level metrics like delta-to-leader, pit status, and tire degradation.
3.  **UI Layer (`src/dashboard_app.py`):** A Dash-based web application that manages state, user interactions, and real-time updates.
4.  **CLI Utilities:** Helper scripts for exploring the F1 calendar and generating standalone reports.

## 🧠 AI-Assisted Workflow

This project was developed using a modern **AI-Assisted Workflow** via the Gemini CLI.
- **Planning:** Utilized structured `plans/` for architectural decisions and feature roadmaps.
- **Execution:** Leveraged Gemini for surgical code updates, debugging complex data transformations, and generating comprehensive test suites.
- **Validation:** Automated testing and codebase analysis were integral to maintaining high engineering standards throughout development.

## 🏁 Getting Started

### Prerequisites
- Python 3.13+
- A stable internet connection (for data fetching)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/[YOUR-USERNAME]/f1-data-companion.git
   cd f1-data-companion
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Dashboard
You can start the main interactive dashboard using the provided script:
```bash
./scripts/run_dashboard.sh
```
Or directly via Python:
```bash
export PYTHONPATH=$PYTHONPATH:.
python src/dashboard_app.py
```
Then navigate to `http://127.0.0.1:8050` in your web browser.

### CLI Utilities
Explore the F1 calendar and sessions directly from your terminal:
```bash
# List all races in 2023
python src/browse_f1.py 2023

# List sessions for the Spanish Grand Prix
python src/browse_f1.py 2023 Spanish
```

## 🧪 Testing
Run the test suite to verify data processing logic:
```bash
pytest
```

## 🗺️ Roadmap

Future enhancements and features currently in the pipeline:

- [ ] **Enhanced Replay Navigation:**
    - Refine the timeline slider to support discrete navigation by **Laps** or **Qualifying Segments** (Q1, Q2, Q3) instead of raw timestamps.
    - Implement a **Floating Playback Controller** (sticky UI) to allow seamless session control while scrolling through deep data visualizations.

- [ ] **Dedicated Qualification Mode:**
    - **Session Intelligence:** Display current session phase (Q1/Q2, Q3) and the official remaining session clock.
    - **Quali-Specific Standings:** Transition standings logic to prioritize **Fastest Lap Time** and delta-to-pole instead of lap count.
    - **Pit Presence Tracking:** Real-time visual indicators to distinguish between drivers on "Flying Laps" vs. those currently in the pits.

- [ ] **Advanced Sector Insights:**
    - **Delta Tracking:** Improve sector color-coding to detect "Yellow" sectors (personal non-improvement) in addition to current Green/Purple logic.
    - **Traffic Awareness:** Correlate sector performance with track position to identify where traffic may have impacted a lap.

---
*Disclaimer: This project is an unofficial fan-made tool and is not affiliated with Formula 1.*
