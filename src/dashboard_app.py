import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import livef1
import datetime
import json
import numpy as np
import time
from src.analysis import get_lap_times_table, calculate_delta_to_leader

# Initialize App with Dark Theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# --- DATA CACHE ---
DATA = {
    'laps': None,
    'delta': None,
    'status': None,
    'pos': None, 
    'timing': None, # New: To track InPit status
    'track_layout': None, 
    'drivers': {},
    'session_info': "No session loaded",
    'max_seconds': 0,
    'time_offset': 0 
}

def format_seconds(seconds):
    return str(datetime.timedelta(seconds=int(seconds)))

def format_lap_time(seconds):
    if seconds <= 0 or pd.isna(seconds): return "-"
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:06.3f}" if m > 0 else f"{s:.3f}"

def fetch_and_cache_session(year, gp, session_type):
    print(f"Loading {gp} {year} {session_type}...")
    race = livef1.get_session(int(year), gp, session_type)
    race.generate(silver=True)
    
    laps_raw = race.laps.copy()
    laps_raw = laps_raw.dropna(subset=['LapStartTime', 'LapTime'])
    laps_raw['DriverNo'] = laps_raw['DriverNo'].astype(str)
    
    min_start = laps_raw['LapStartTime'].dt.total_seconds().min()
    DATA['time_offset'] = min_start
    
    laps_raw['RelativeStart'] = laps_raw['LapStartTime'].dt.total_seconds() - min_start
    laps_raw['RelativeEnd'] = (laps_raw['LapStartTime'] + laps_raw['LapTime']).dt.total_seconds() - min_start
    laps_raw['LapTime_val'] = laps_raw['LapTime'].dt.total_seconds()
    
    for s in ['Sector1_Time', 'Sector2_Time', 'Sector3_Time']:
        laps_raw[f'{s}_val'] = laps_raw[s].dt.total_seconds().fillna(0)
    laps_raw['S1_End'] = laps_raw['RelativeStart'] + laps_raw['Sector1_Time_val']
    laps_raw['S2_End'] = laps_raw['S1_End'] + laps_raw['Sector2_Time_val']
    
    DATA['laps'] = laps_raw
    DATA['delta'] = calculate_delta_to_leader(race.laps)
    DATA['status'] = {
        'track': race.get_data("TrackStatus"),
        'session': race.get_data("SessionStatus")
    }
    DATA['status']['track']['RelativeTime'] = DATA['status']['track']['timestamp'].dt.total_seconds() - min_start
    DATA['drivers'] = {str(k): v.Tla for k, v in race.drivers.items()}
    
    # --- POSITION DATA ---
    pos_data = race.get_data("Position.z")
    pos_data['RelativeTime'] = pos_data['timestamp'].dt.total_seconds() - min_start
    pos_data['DriverNo'] = pos_data['DriverNo'].astype(str)
    DATA['pos'] = pos_data

    # --- TIMING DATA (For Pit Status) ---
    print("Fetching timing data...")
    timing_data = race.get_data("TimingData")
    timing_data['RelativeTime'] = timing_data['timestamp'].dt.total_seconds() - min_start
    timing_data['DriverNo'] = timing_data['DriverNo'].astype(str)
    DATA['timing'] = timing_data

    # --- TRACK SECTOR DISCOVERY ---
    valid_pos = pos_data[pos_data['X'] != 0]
    if not valid_pos.empty:
        first_driver = laps_raw['DriverNo'].iloc[0]
        ref_lap = laps_raw[laps_raw['DriverNo'] == first_driver].iloc[1]
        lap_path = valid_pos[(valid_pos['DriverNo'] == first_driver) & 
                             (valid_pos['RelativeTime'] >= ref_lap['RelativeStart']) & 
                             (valid_pos['RelativeTime'] <= ref_lap['RelativeEnd'])].copy()
        s1_path = lap_path[lap_path['RelativeTime'] <= ref_lap['S1_End']]
        s2_path = lap_path[(lap_path['RelativeTime'] > ref_lap['S1_End']) & (lap_path['RelativeTime'] <= ref_lap['S2_End'])]
        s3_path = lap_path[lap_path['RelativeTime'] > ref_lap['S2_End']]
        DATA['track_layout'] = {'S1': s1_path[['X', 'Y']], 'S2': s2_path[['X', 'Y']], 'S3': s3_path[['X', 'Y']]}
    else: DATA['track_layout'] = None

    DATA['session_info'] = f"{gp} {year} - {session_type}"
    DATA['max_seconds'] = int(laps_raw['RelativeEnd'].max())
    return DATA['session_info']

# --- LAYOUT ---
app.layout = dbc.Container([
    dcc.Store(id='selected-drivers-store', data=[]),
    dcc.Store(id='sync-store', data={'start_sys': None, 'start_dash': 0, 'is_playing': False}),
    
    dbc.Row([
        dbc.Col(html.H1("🏎️ ApexTelemetry"), width=8),
        dbc.Col(html.H5(id="session-title", className="text-danger"), width=4, className="text-end")
    ], className="mt-4 mb-2"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("1. Session Selection"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Year"),
                            dcc.Dropdown(id='year-dropdown', options=[{'label': str(y), 'value': y} for y in range(2026, 2017, -1)], value=2023, clearable=False, className="text-dark")
                        ], width=3),
                        dbc.Col([
                            html.Label("Grand Prix"),
                            dcc.Dropdown(id='gp-dropdown', clearable=False, className="text-dark")
                        ], width=4),
                        dbc.Col([
                            html.Label("Session"),
                            dcc.Dropdown(id='session-dropdown', clearable=False, className="text-dark")
                        ], width=3),
                        dbc.Col([
                            html.Label("\u00A0", className="d-block"),
                            dbc.Button("Load", id="btn-load", color="danger", className="w-100")
                        ], width=2),
                    ]),
                    dbc.Row([dbc.Col(dbc.Spinner(html.Div(id="load-status"), color="danger"), width=12, className="mt-2")])
                ])
            ], className="mb-4")
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("2. Replay Sync Controls"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([html.H2(id="current-time-display", children="00:00:00", className="text-center text-success")], width=3),
                        dbc.Col([
                            dbc.ButtonGroup([
                                dbc.Button("⏪ -30s", id="btn-back", color="secondary"),
                                dbc.Button("▶️ Play", id="btn-play", color="success"),
                                dbc.Button("⏸️ Pause", id="btn-pause", color="warning"),
                                dbc.Button("+30s ⏩", id="btn-next", color="danger"),
                            ], className="w-100")
                        ], width=6),
                        dbc.Col([
                            html.Label("Playback Speed:"),
                            dcc.Dropdown(id='speed-dropdown', options=[{'label': f'{s}x', 'value': s} for s in [0.5, 1.0, 2.0, 5.0, 10.0]], value=1.0, clearable=False, className="text-dark")
                        ], width=3),
                    ]),
                    html.Hr(),
                    dcc.Slider(0, 1, 1, value=0, id='time-slider', tooltip={"placement": "bottom", "always_visible": True}),
                    dcc.Interval(id='timer', interval=500, n_intervals=0, disabled=True),
                ])
            ], className="mb-4")
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("3. Driver Filters"),
                dbc.CardBody(id="driver-selection-container", className="d-flex flex-wrap gap-2")
            ], className="mb-4")
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Race Highlights"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([html.Small("FASTEST LAP"), html.H3(id="fastest-lap-val", className="text-success", children="--:--.---"), html.P(id="fastest-lap-driver", children="None")], width=4),
                        dbc.Col([html.Small("LEADER"), html.H3(id="leader-val", className="text-danger", children="None"), html.P(id="lap-counter", children="Waiting...")], width=4),
                        dbc.Col([html.Small("TRACK STATUS"), html.Div(id="race-status-container", className="mt-2")], width=4),
                    ])
                ])
            ])
        ], width=12),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Live Track Map"),
                dbc.CardBody([dcc.Graph(id='track-map', style={"height": "500px"})])
            ])
        ], width=7),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Sector Performance"),
                dbc.CardBody(id="sector-performance-container", style={"height": "500px", "overflowY": "auto"})
            ])
        ], width=5)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([dcc.Graph(id='lap-time-chart', className="mb-4"), dcc.Graph(id='delta-chart')], width=7),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Live Standings"),
                dbc.CardBody(id="standings-table-container", style={"padding": "0px"})
            ])
        ], width=5)
    ], className="mb-4")
], fluid=True)

# --- CALLBACKS ---

@app.callback(Output('gp-dropdown', 'options'), Input('year-dropdown', 'value'))
def update_gp_options(selected_year):
    if not selected_year: return []
    season = livef1.get_season(int(selected_year))
    return [{'label': row['Meeting Name'], 'value': row['Meeting Name']} for _, row in season.meetings_table.iterrows()]

@app.callback(Output('session-dropdown', 'options'), [Input('year-dropdown', 'value'), Input('gp-dropdown', 'value')])
def update_session_options(selected_year, selected_gp):
    if not selected_year or not selected_gp: return []
    meeting = livef1.get_meeting(int(selected_year), selected_gp)
    df = meeting.sessions_table
    col = 'session_name' if 'session_name' in df.columns else df.columns[0]
    return [{'label': row[col], 'value': row[col]} for _, row in df.iterrows()]

@app.callback(Output('load-status', 'children'), Input('btn-load', 'n_clicks'), [State('year-dropdown', 'value'), State('gp-dropdown', 'value'), State('session-dropdown', 'value')], prevent_initial_call=True)
def trigger_load_session(n_clicks, year, gp, session):
    if not all([year, gp, session]): return "Select all fields"
    try:
        fetch_and_cache_session(year, gp, session)
        return f"Loaded: {gp} {year}"
    except Exception as e: return f"Error: {e}"

@app.callback([Output('timer', 'disabled'), Output('sync-store', 'data')], [Input('btn-play', 'n_clicks'), Input('btn-pause', 'n_clicks'), Input('btn-load', 'n_clicks'), Input('btn-next', 'n_clicks'), Input('btn-back', 'n_clicks')], [State('time-slider', 'value'), State('sync-store', 'data')])
def manage_sync_state(play, pause, load, nxt, back, current_slider, current_sync):
    ctx = dash.callback_context
    if not ctx.triggered: return True, current_sync
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger == 'btn-play': return False, {'start_sys': time.time(), 'start_dash': current_slider, 'is_playing': True}
    elif trigger in ['btn-pause', 'btn-load', 'btn-next', 'btn-back']: return True, {'start_sys': None, 'start_dash': current_slider, 'is_playing': False}
    return True, current_sync

@app.callback([Output('time-slider', 'value'), Output('time-slider', 'max'), Output('session-title', 'children'), Output('current-time-display', 'children')], [Input('timer', 'n_intervals'), Input('btn-next', 'n_clicks'), Input('btn-back', 'n_clicks'), Input('load-status', 'children')], [State('time-slider', 'value'), State('speed-dropdown', 'value'), State('sync-store', 'data')])
def update_timeline(n, nxt, back, load_msg, current_sec, speed, sync):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    if trigger == 'load-status': return 0, DATA['max_seconds'], DATA['session_info'], "00:00:00"
    new_sec = current_sec
    if trigger == 'timer' and sync['is_playing']:
        elapsed_real = time.time() - sync['start_sys']
        new_sec = min(DATA['max_seconds'], sync['start_dash'] + (elapsed_real * speed))
    elif trigger == 'btn-next': new_sec = min(DATA['max_seconds'], current_sec + 30)
    elif trigger == 'btn-back': new_sec = max(0, current_sec - 30)
    return new_sec, DATA['max_seconds'], DATA['session_info'], format_seconds(new_sec)

@app.callback([Output('driver-selection-container', 'children'), Output('selected-drivers-store', 'data')], [Input({'type': 'driver-btn', 'index': dash.ALL}, 'n_clicks'), Input('load-status', 'children')], [State({'type': 'driver-btn', 'index': dash.ALL}, 'id'), State('selected-drivers-store', 'data')])
def handle_driver_selection(n_clicks, load_msg, btn_ids, current_selection):
    ctx = dash.callback_context
    if not DATA['drivers']: return [], []
    trigger = ctx.triggered[0]['prop_id'] if ctx.triggered else ""
    if 'driver-btn' in trigger:
        clicked_driver = str(json.loads(trigger.split('.')[0])['index'])
        if clicked_driver in current_selection: current_selection.remove(clicked_driver)
        else: current_selection.append(clicked_driver)
    elif trigger == 'load-status.children': current_selection = [] 
    buttons = []
    for d_no in sorted(DATA['drivers'].keys(), key=lambda x: int(x) if x.isdigit() else 999):
        is_active = d_no in current_selection
        buttons.append(dbc.Button(f"{DATA['drivers'][d_no]} ({d_no})", id={'type': 'driver-btn', 'index': d_no}, color="danger" if is_active else "outline-secondary", size="sm", className="me-1 mb-1"))
    return buttons, current_selection

@app.callback(
    [Output('lap-time-chart', 'figure'), Output('delta-chart', 'figure'), Output('standings-table-container', 'children'),
     Output('fastest-lap-val', 'children'), Output('fastest-lap-driver', 'children'), Output('leader-val', 'children'),
     Output('lap-counter', 'children'), Output('race-status-container', 'children'), Output('sector-performance-container', 'children'),
     Output('track-map', 'figure')],
    [Input('time-slider', 'value'), Input('selected-drivers-store', 'data')]
)
def update_dashboard(current_sec, selected_drivers):
    if DATA['laps'] is None: return [px.scatter(title="Load session")] * 2 + ["No data", "--", "None", "None", "None", [], "Load data", px.scatter(title="No Map")]
    active_filter = selected_drivers if selected_drivers else list(DATA['drivers'].keys())
    visible_laps = DATA['laps'][DATA['laps']['RelativeEnd'] <= current_sec].copy()
    if visible_laps.empty and DATA['laps'][DATA['laps']['RelativeStart'] <= current_sec].empty: return [px.scatter(title="Race Start...")] * 2 + ["Race Start...", "--:--.---", "None", "None", "Lap 0", [], "Race Start", px.scatter(title="Race Start")]

    # Charts & Standings
    current_lap_max, leader, table = 0, "Race Start", "Waiting..."
    if not visible_laps.empty:
        chart_data = visible_laps[visible_laps['DriverNo'].isin(active_filter)].copy()
        fig_laps = px.line(chart_data, x="LapNo", y="LapTime_val", color="DriverNo", title="Lap Times", template="plotly_dark")
        current_lap_max = visible_laps['LapNo'].max()
        chart_delta = DATA['delta'][(DATA['delta']['DriverNo'].astype(str).isin(active_filter)) & (DATA['delta']['LapNo'] <= current_lap_max)]
        fig_delta = px.line(chart_delta, x="LapNo", y="DeltaToLeader", color="DriverNo", title="Gap to Leader", template="plotly_dark")
        fig_delta.update_yaxes(autorange="reversed")
        latest_standings = visible_laps.sort_values(['LapNo', 'RelativeEnd'], ascending=[False, True]).groupby('DriverNo').first().reset_index().sort_values(['LapNo', 'RelativeEnd'], ascending=[False, True])
        latest_standings['Pos'] = range(1, len(latest_standings) + 1)
        latest_standings['Driver'] = latest_standings['DriverNo'].map(DATA['drivers'])
        table = dash_table.DataTable(data=latest_standings[['Pos', 'Driver', 'Compound', 'TyreAge', 'LapNo']].to_dict('records'), columns=[{"name": i, "id": i} for i in ['Pos', 'Driver', 'Compound', 'TyreAge', 'LapNo']], style_header={'backgroundColor': 'black', 'color': 'white'}, style_data={'backgroundColor': '#222', 'color': 'white'}, page_action='none')
        leader = latest_standings.iloc[0]['Driver']
    else: fig_laps, fig_delta = px.scatter(title="Waiting..."), px.scatter(title="Waiting...")

    # Sector Performance
    best_s1 = visible_laps['Sector1_Time_val'].replace(0, np.nan).min() if not visible_laps.empty else 999
    best_s2 = visible_laps['Sector2_Time_val'].replace(0, np.nan).min() if not visible_laps.empty else 999
    best_s3 = visible_laps['Sector3_Time_val'].replace(0, np.nan).min() if not visible_laps.empty else 999
    best_lap_val = visible_laps['LapTime_val'].replace(0, np.nan).min() if not visible_laps.empty else 999

    theoretical_best_row = html.Div([
        html.Span("BEST", style={"width": "50px", "display": "inline-block", "fontWeight": "bold", "color": "#B15BFF"}),
        html.Span(f"{best_s1:.3f}" if best_s1 < 999 else "-", style={"backgroundColor": "rgba(177, 91, 255, 0.2)", "color": "#B15BFF", "width": "65px", "display": "inline-block", "textAlign": "center", "borderRadius": "3px", "marginRight": "5px"}),
        html.Span(f"{best_s2:.3f}" if best_s2 < 999 else "-", style={"backgroundColor": "rgba(177, 91, 255, 0.2)", "color": "#B15BFF", "width": "65px", "display": "inline-block", "textAlign": "center", "borderRadius": "3px", "marginRight": "5px"}),
        html.Span(f"{best_s3:.3f}" if best_s3 < 999 else "-", style={"backgroundColor": "rgba(177, 91, 255, 0.2)", "color": "#B15BFF", "width": "65px", "display": "inline-block", "textAlign": "center", "borderRadius": "3px", "marginRight": "5px"}),
        html.Span(format_lap_time(best_lap_val) if best_lap_val < 999 else "-", style={"backgroundColor": "rgba(177, 91, 255, 0.2)", "color": "#B15BFF", "width": "100px", "display": "inline-block", "textAlign": "center", "borderRadius": "3px"})
    ], className="mb-3 d-flex align-items-center pb-2 border-bottom border-secondary")

    sector_rows = [theoretical_best_row]
    for d_no in active_filter[:15]:
        d_laps = DATA['laps'][DATA['laps']['DriverNo'] == d_no]
        all_started = d_laps[d_laps['RelativeStart'] <= current_sec].sort_values('LapNo')
        if all_started.empty: continue
        target_lap = all_started.iloc[-1]
        s1_v, s1_s = "-", {"backgroundColor": "#333", "color": "#888"}
        s2_v, s2_s = "-", {"backgroundColor": "#333", "color": "#888"}
        s3_v, s3_s = "-", {"backgroundColor": "#333", "color": "#888"}
        lt_v, lt_s = "-", {"backgroundColor": "#333", "color": "#888"}
        if current_sec >= target_lap['S1_End']:
            s1_v, s1_s = f"{target_lap['Sector1_Time_val']:.3f}", {"backgroundColor": "#B15BFF" if target_lap['Sector1_Time_val'] <= best_s1 else "#00FF00", "color": "white"}
            if current_sec >= target_lap['S2_End']:
                s2_v, s2_s = f"{target_lap['Sector2_Time_val']:.3f}", {"backgroundColor": "#B15BFF" if target_lap['Sector2_Time_val'] <= best_s2 else "#00FF00", "color": "white"}
            if current_sec >= target_lap['RelativeEnd']:
                s3_v, s3_s = f"{target_lap['Sector3_Time_val']:.3f}", {"backgroundColor": "#B15BFF" if target_lap['Sector3_Time_val'] <= best_s3 else "#00FF00", "color": "white"}
                lt_v, lt_s = format_lap_time(target_lap['LapTime_val']), {"backgroundColor": "#B15BFF" if target_lap['LapTime_val'] <= best_lap_val else "#00FF00", "color": "white"}
        elif len(all_started) >= 2:
            prev = all_started.iloc[-2]
            s1_v, s1_s = f"{prev['Sector1_Time_val']:.3f}", {"backgroundColor": "#B15BFF" if prev['Sector1_Time_val'] <= best_s1 else "#00FF00", "color": "white"}
            s2_v, s2_s = f"{prev['Sector2_Time_val']:.3f}", {"backgroundColor": "#B15BFF" if prev['Sector2_Time_val'] <= best_s2 else "#00FF00", "color": "white"}
            s3_v, s3_s = f"{prev['Sector3_Time_val']:.3f}", {"backgroundColor": "#B15BFF" if prev['Sector3_Time_val'] <= best_s3 else "#00FF00", "color": "white"}
            lt_v, lt_s = format_lap_time(prev['LapTime_val']), {"backgroundColor": "#B15BFF" if prev['LapTime_val'] <= best_lap_val else "#00FF00", "color": "white"}
        sector_rows.append(html.Div([html.Span(f"{DATA['drivers'].get(d_no, d_no)}", style={"width": "50px", "display": "inline-block", "fontWeight": "bold", "color": "#CCC"}),
                                     html.Span(s1_v, style={**s1_s, "width": "65px", "display": "inline-block", "textAlign": "center", "borderRadius": "3px", "marginRight": "5px", "fontSize": "0.85rem"}),
                                     html.Span(s2_v, style={**s2_s, "width": "65px", "display": "inline-block", "textAlign": "center", "borderRadius": "3px", "marginRight": "5px", "fontSize": "0.85rem"}),
                                     html.Span(s3_v, style={**s3_s, "width": "65px", "display": "inline-block", "textAlign": "center", "borderRadius": "3px", "marginRight": "5px", "fontSize": "0.85rem"}),
                                     html.Span(lt_v, style={**lt_s, "width": "100px", "display": "inline-block", "textAlign": "center", "borderRadius": "3px", "fontSize": "0.85rem"})], className="mb-2 d-flex align-items-center"))

    # Track Map
    fig_map = go.Figure()
    if DATA['track_layout'] is not None:
        colors = {'S1': '#dc3545', 'S2': '#00FFFF', 'S3': '#FFDB58'}
        for sector, color in colors.items():
            fig_map.add_trace(go.Scatter(x=DATA['track_layout'][sector]['X'], y=DATA['track_layout'][sector]['Y'], mode='lines', line=dict(color=color, width=4), name=sector, hoverinfo='skip', showlegend=False))
    
    if DATA['pos'] is not None:
        latest_pos = DATA['pos'][DATA['pos']['RelativeTime'] <= current_sec]
        if not latest_pos.empty:
            # Group and filter cars in pits
            current_cars = latest_pos.sort_values('RelativeTime').groupby('DriverNo').last().reset_index()
            # Fetch latest pit status
            if DATA['timing'] is not None:
                latest_timing = DATA['timing'][DATA['timing']['RelativeTime'] <= current_sec].sort_values('RelativeTime').groupby('DriverNo').last().reset_index()
                in_pit_drivers = latest_timing[latest_timing['InPit'] == True]['DriverNo'].tolist()
            else: in_pit_drivers = []

            for _, car in current_cars[current_cars['X'] != 0].iterrows():
                if car['DriverNo'] in in_pit_drivers: continue # HIDE CARS IN PIT
                is_sel = car['DriverNo'] in selected_drivers
                fig_map.add_trace(go.Scatter(x=[car['X']], y=[car['Y']], mode='markers+text', marker=dict(size=12 if is_sel else 8, color='#FF0000' if is_sel else '#888'), text=DATA['drivers'].get(car['DriverNo'], car['DriverNo']), textposition="top center", textfont=dict(color="white", size=10), showlegend=False))
    fig_map.update_layout(template="plotly_dark", margin=dict(l=0, r=0, t=0, b=0), xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

    # Status
    status_badges = []
    track_df = DATA['status']['track']
    past_status = track_df[track_df['RelativeTime'] <= current_sec]
    if not past_status.empty:
        mapping = {'1': ("Clear", "success"), '2': ("Yellow", "warning"), '4': ("SC", "danger"), '6': ("VSC", "warning"), '7': ("Red", "dark")}
        label, color = mapping.get(str(past_status.iloc[-1]['Status']), ("Normal", "info"))
        status_badges.append(dbc.Badge(label, color=color, className="me-1 h5"))
    if not visible_laps.empty:
        best_lap_row = visible_laps.loc[visible_laps['LapTime'].idxmin()]
        f_lap, f_driver = format_lap_time(best_lap_row['LapTime_val']), DATA['drivers'].get(str(best_lap_row['DriverNo']), "UNK")
    else: f_lap, f_driver = "--:--.---", "None"

    return fig_laps, fig_delta, table, f_lap, f_driver, leader, f"Lap {int(current_lap_max)}", status_badges, sector_rows, fig_map

if __name__ == "__main__":
    app.run(debug=True, port=8050, host='0.0.0.0')
