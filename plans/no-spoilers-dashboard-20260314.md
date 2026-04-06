# Implementation Plan: No-Spoilers Data Companion

## Approach A: Dash Web Application (Recommended)
### ## Approach
- **Why this solution:** Dash is built directly on Plotly. It allows for a robust "Timer" component and complex state management (e.g., tracking the "Current Lap" and updating all charts simultaneously).
- **Interactivity:** Uses `dcc.Interval` for automatic playback or `html.Button` for manual "Next Lap" progression.

### ## Steps
1. **Install Dependencies** (5 min)
   ```bash
   pip install dash dash-bootstrap-components
   ```
2. **Core Implementation** (40 min)
   - `src/dashboard/app.py`: Main entry point.
   - `src/dashboard/state.py`: Manages the "Emulated Time" and data gating logic.
   - `src/dashboard/components.py`: Reusable chart/card generators.
3. **Integration** (15 min)
   - Import functions from `src/analysis.py` to process data before gating.

---

## Approach B: Streamlit Application
### ## Approach
- **Why this solution:** Extreme speed of development. Uses a simple "Slider" or "Button" to progress through laps.
- **Alternatives considered:** Manual CLI script generating static HTML (Too clunky for "live" feel).

### ## Steps
1. **Install Dependencies** (5 min)
   ```bash
   pip install streamlit
   ```
2. **Core Implementation** (20 min)
   - `src/companion_ui.py`: Single file implementation using `st.slider` to control the "current lap".
3. **Integration** (10 min)
   - Direct calls to `src/analysis.py`.

---

## Comparison Table
| Criteria | Approach A (Dash) | Approach B (Streamlit) |
|----------|-------------------|------------------------|
| **Effort** | ⭐⭐⭐ (High) | ⭐ (Low) |
| **Interactivity** | ⭐⭐⭐ (Full control) | ⭐⭐ (Limited but easy) |
| **"Live" Feel** | ⭐⭐⭐ (Timer native) | ⭐ (Requires full rerun) |
| **Scalability** | ⭐⭐⭐ (Best for complex UIs) | ⭐⭐ (Gets messy) |

## Recommendation
**Choose Approach A (Dash).** 
Since you want a "companion" feel while watching a replay, Dash's ability to have a background timer that updates the dashboard every few seconds without refreshing the whole page is superior. It also allows for more professional "Card" layouts for Fastest Lap and Tire Info.

---

## Steps for Approach A
1. **Setup Dashboard Skeleton**
   - Create `src/dashboard/app.py`.
   - Implement a "Lap Gating" function: `get_visible_data(full_df, current_lap)`.
2. **Implement UI Layout**
   - Header: Session Info + Play/Pause/Next Lap controls.
   - Row 1: Fastest Lap Card | Current Tire Table.
   - Row 2: Lap Time Chart (Filtered).
   - Row 3: Delta to Leader Chart.
3. **Timer Logic**
   - Hook `dcc.Interval` to a callback that increments `current_lap`.

## Timeline
| Phase | Duration |
|-------|----------|
| Dependencies | 5 min |
| State/Gating Logic | 20 min |
| Dashboard UI | 40 min |
| Integration | 15 min |
| **Total** | **1.5 hours** |

## Rollback Plan
- Revert to `src/visualize.py` static HTML generation if Dash overhead is too high for the current environment.

## Security Checklist
- [x] Input validation (Ensure year/GP inputs are sanitized).
- [x] Error handling (Graceful degradation if F1 API is down).
