# API Reference

Detailed documentation for the `livef1` library API as used in this project.

## `livef1` Core Functions

### `get_session`
Retrieves a specific F1 session's data.

**Parameters:**
- `season` (int): Year of the season (e.g., `2023`).
- `meeting_identifier` (str): Name of the Grand Prix or circuit (e.g., `"Monaco"`).
- `session_identifier` (str): Type of session (e.g., `"Race"`, `"Qualifying"`).

**Returns:** `Session` object.

---

## `Session` Class

### `generate`
Processes raw data into higher-level tables.

**Parameters:**
- `silver` (bool): If `True`, generate silver tables (`laps`, `carTelemetry`, etc.). Default `True`.
- `gold` (bool): If `True`, generate gold tables. Default `False`.

### `get_data`
Retrieves raw data frames for specified topics.

**Parameters:**
- `dataNames` (str or list): Name(s) of the topics to fetch (e.g., `["CarData.z", "Position.z"]`).
- `parallel` (bool): Whether to fetch in parallel. Default `False`.

---

## `RealF1Client` Class

Located in `livef1.adapters.realtime_client`.

### `__init__`
Initializes the live timing client.

**Parameters:**
- `topics` (list): Data feeds to subscribe to.
- `log_file_name` (str): Path to save incoming data (JSON format).

### `run`
Starts the real-time client connection. This call is blocking until interrupted.
