# Implementation Plan: Live Replay Sync Controller

## Suggestions for "Live Feeling"
1. **Time-Based Emulation (Recommended):** Instead of jumping by full laps, the dashboard should progress by "Session Seconds." This allows you to see deltas and positions update gradually, just like the real timing screen.
2. **Variable Playback Speed:** Add a control to change the speed (e.g., 1x for normal viewing, 5x to skip to a specific point, 0.5x for deep analysis).
3. **Manual Sync "Jump":** A field where you can type "45:00" (minutes into race) to instantly align the dashboard with your video player timestamp.

## Approach
I will implement an **Integrated Sync Controller** that switches the logic from `Lap-based` to `Time-based`. The "Current Lap" slider will become a "Timeline" slider, and the dashboard will reveal data based on the elapsed race time (`LapStartTime`).

## Steps
1. **Update Data Cache** (5 min)
   - Add `current_session_time` (float) to the `DATA` object.
2. **UI Refinement** (20 min)
   - Replace Lap Slider with a **Timeline Slider** (Total seconds of race).
   - Add a **Playback Speed Dropdown** (0.5x, 1x, 2x, 5x, 10x).
   - Add a "Current Race Time" display (HH:MM:SS).
3. **Core Logic Implementation** (30 min)
   - Update `update_lap_progression` callback to increment `current_session_time` based on selected speed.
   - Update `update_dashboard` to filter data: `df[df['LapStartTime'] <= current_session_time]`.
4. **Testing** (15 min)
   - Verify that deltas and standings update mid-lap as time progresses.

## Timeline
| Phase | Duration |
|-------|----------|
| State/Cache Update | 5 min |
| UI Controls | 20 min |
| Time-based Filtering | 30 min |
| Validation | 15 min |
| **Total** | **1.1 hours** |

## Rollback Plan
- Revert `src/dashboard_app.py` to the previous lap-based version if time-syncing causes excessive lag or data discrepancies.

## Security Checklist
- [x] No sensitive data exposed.
- [x] Input validation for manual time entry.
