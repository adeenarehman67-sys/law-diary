import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from mobile_reader import load_case_database

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Advocate Digital Diary - Sindh Courts Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LOAD DATA ---
cases_data = load_case_database()

if not cases_data:
    st.warning("No case records found or database is currently syncing.")
else:
    df = pd.DataFrame(cases_data)

    # --- DATE CALCULATIONS FOR METRICS ---
    today_str = datetime.now().strftime("%Y-%m-%d")
    tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    total_cases = len(df)
    
    # Calculate counts safely
    fixed_today = len(df[df.get('next_date') == today_str]) if 'next_date' in df.columns else 0
    fixed_tomorrow = len(df[df.get('next_date') == tomorrow_str]) if 'next_date' in df.columns else 0
    
    overdue_count = 0
    if 'next_date' in df.columns:
        try:
            valid_dates = pd.to_datetime(df['next_date'], errors='coerce')
            overdue_count = len(df[valid_dates < pd.to_datetime(today_str)])
        except:
            pass

    disposed_count = len(df[df.astype(str).apply(lambda x: x.str.contains('disposed', case=False)).any(axis=1)])

    # --- SIDEBAR NAVIGATION ---
    st.sidebar.markdown("### 🏛️ LAW DIARY")
    st.sidebar.markdown("---")
    
    nav_tab = st.sidebar.radio(
        "Navigation",
        ["Master List", "Today's Schedule", "Tomorrow's Schedule", "Disposed Cases"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚖️ FILTER BY COURT")
    court_options = ["All Courts"] + sorted(df['court'].dropna().unique().tolist()) if 'court' in df.columns else ["All Courts"]
    selected_court_filter = st.sidebar.selectbox("Select Jurisdiction", court_options)

    # --- MAIN WORKSPACE HEADER ---
    st.title("⚖️ Advocate Digital Diary - Sindh Courts Tracker")
    
    # --- LIVE STATS DASHBOARD BANNER ---
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Active Cases", total_cases)
    col2.metric("Fixed Today", fixed_today)
    col3.metric("Fixed Tomorrow", fixed_tomorrow)
    col4.metric("Overdue", overdue_count)
    col5.metric("Disposed", disposed_count)
    
    st.markdown("---")

    # --- FILTERING LOGIC ---
    working_df = df.copy()
    
    if selected_court_filter != "All Courts":
        working_df = working_df[working_df['court'] == selected_court_filter]

    if nav_tab == "Today's Schedule" and 'next_date' in working_df.columns:
        working_df = working_df[working_df['next_date'] == today_str]
    elif nav_tab == "Tomorrow's Schedule" and 'next_date' in working_df.columns:
        working_df = working_df[working_df['next_date'] == tomorrow_str]
    elif nav_tab == "Disposed Cases":
        working_df = working_df[working_df.astype(str).apply(lambda x: x.str.contains('disposed', case=False)).any(axis=1)]

    # --- SEARCH BAR & CONTROLS ---
    search_query = st.text_input("🔍 Search by Case Number or Party Name...", "")
    
    if search_query:
        working_df = working_df[
            working_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        ]

    # --- DATA GRID DISPLAY ---
    st.subheader(f"📂 {nav_tab} ({len(working_df)} Records)")
    st.dataframe(working_df, use_container_width=True, height=450)