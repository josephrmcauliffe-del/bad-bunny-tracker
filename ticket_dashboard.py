import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Bad Bunny Tracker", layout="wide")
st.title("🎟️ Bad Bunny Ticket Price Dashboard")

# Load data
@st.cache_data(ttl=60)
def load_data():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_FILE)
    try:
        # Try to read the table
        df = pd.read_sql_query("SELECT * FROM price_log", conn)
    except Exception as e:
        # If the table doesn't exist yet, don't crash, just return empty data
        df = pd.DataFrame() 
    finally:
        conn.close()
        
    if df.empty:
        return df
        
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['event_date'] = pd.to_datetime(df['event_date']).dt.tz_localize(None)
    df['hours_to_show'] = (df['event_date'] - df['timestamp']).dt.total_seconds() / 3600
    return df
