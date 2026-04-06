import livef1
import sys
import pandas as pd

def list_meetings(year):
    """
    List all Grand Prix meetings for a specific year.
    """
    try:
        print(f"\n--- F1 Calendar for {year} ---")
        season = livef1.get_season(int(year))
        
        # Select and format columns for better display
        df = season.meetings_table.copy()
        
        # Basic columns to show
        cols = ['Meeting Key', 'Meeting Name', 'Meeting Circuit Shortname', 'Race Startdate']
        # Filter to only show columns that actually exist in this season's data
        existing_cols = [c for c in cols if c in df.columns]
        
        print(df[existing_cols].to_string(index=False))
        return True
    except Exception as e:
        print(f"Error fetching season {year}: {e}")
        return False

def list_sessions(year, meeting_id):
    """
    List all sessions (Practice, Quali, Race) for a specific GP.
    """
    try:
        print(f"\n--- Sessions for {meeting_id} {year} ---")
        meeting = livef1.get_meeting(int(year), meeting_id)

        # Display the sessions table
        df = meeting.sessions_table.copy()

        # Format columns - lowercase keys in the dataframe
        cols = ['session_name', 'session_startDate', 'session_endDate']
        existing_cols = [c for c in cols if c in df.columns]

        print(df[existing_cols].to_string(index=False))
    except Exception as e:

        print(f"Error fetching sessions for {meeting_id} {year}: {e}")

if __name__ == "__main__":
    # Usage: 
    # python src/browse_f1.py 2023           <- Lists meetings
    # python src/browse_f1.py 2023 Monaco    <- Lists sessions
    
    args = sys.argv[1:]
    
    if len(args) == 0:
        print("Usage:")
        print("  python src/browse_f1.py <year>            (e.g., 2023)")
        print("  python src/browse_f1.py <year> <meeting>  (e.g., 2023 Monaco)")
        sys.exit(1)
        
    year = args[0]
    
    if len(args) == 1:
        list_meetings(year)
    else:
        meeting_id = args[1]
        list_sessions(year, meeting_id)
