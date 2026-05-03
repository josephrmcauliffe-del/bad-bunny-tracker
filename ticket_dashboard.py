import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Bad Bunny Tracker", layout="wide")
st.title("🎟️ Bad Bunny Ticket Price Dashboard")

# Load data
conn = sqlite3.connect('bad_bunny_tickets.db')
df = pd.read_sql_query("SELECT * FROM price_log", conn)
conn.close()

if df.empty:
    st.warning("No data found in the database yet.")
else:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['event_date'] = pd.to_datetime(df['event_date']).dt.tz_localize(None)
    df['hours_to_show'] = (df['event_date'] - df['timestamp']).dt.total_seconds() / 3600

    st.markdown("### 📉 72-Hour vs 1-Hour Price Validation")
    results = []
    for event_id, group in df.groupby('event_id'):
        event_title = group['event_title'].iloc[0]
        t_72_data = group.iloc[(group['hours_to_show'] - 72).abs().argsort()[:1]]
        t_1_data = group.iloc[(group['hours_to_show'] - 1).abs().argsort()[:1]]
        
        if not t_72_data.empty and not t_1_data.empty:
            price_72h = t_72_data['lowest_price'].values[0]
            price_1h = t_1_data['lowest_price'].values[0]
            change_pct = ((price_1h - price_72h) / price_72h) * 100
            trend = "📉 Dropped" if change_pct < 0 else "📈 Rose" if change_pct > 0 else "➖ Flat"
            results.append({
                'Event': event_title, 'T-72h Price ($)': price_72h, 'T-1h Price ($)': price_1h,
                'Change (%)': round(change_pct, 2), 'Trend': trend
            })
    
    if results:
        report_df = pd.DataFrame(results)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Shows Validated", len(report_df))
        col2.metric("Average Price Change", f"{report_df['Change (%)'].mean():.2f}%")
        col3.metric("Shows Dropped", f"{len(report_df[report_df['Change (%)'] < 0])}")
        st.dataframe(report_df, use_container_width=True)

    st.markdown("### 📊 Price Timeline (Final 7 Days)")
    chart_data = df[df['hours_to_show'] <= 168].copy()
    if not chart_data.empty:
        fig = px.line(chart_data, x='hours_to_show', y='lowest_price', color='event_title', markers=True)
        fig.update_xaxes(autorange="reversed") 
        st.plotly_chart(fig, use_container_width=True)

