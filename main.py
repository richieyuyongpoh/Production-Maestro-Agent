# Production Maestro Agent - A Streamlit Demonstration

import streamlit as st
import pandas as pd
import numpy as np
import random

# --- App Configuration ---
st.set_page_config(
    page_title="Production Maestro Agent",
    page_icon="🎼",
    layout="wide"
)

# --- App Header ---
st.title("🎼 Production Maestro Agent - Live Demo")
st.markdown("""
This application demonstrates the core functionality of the **Production Maestro Agent**.

The agent's goal is to maximize factory throughput and profitability by optimizing the daily production schedule. It achieves this by:
1.  **Perceiving** the entire list of daily orders and their requirements.
2.  **Reasoning** to find the most efficient sequence by grouping similar jobs.
3.  **Acting** by re-ordering the production queue to minimize costly setup/changeover time.

*This demo is based on the concepts presented in the AI Transformation Workshop.*
""")

# --- Attribution and License ---
st.sidebar.title("About")
st.sidebar.markdown("""
**Designed by Richie, TAR UMT**
<a href="mailto:yuyp@tarc.edu.my">yuyp@tarc.edu.my</a>
""", unsafe_allow_html=True)
st.sidebar.info("""
**Disclaimer:** This is a demonstration application for illustrative purposes only. The data is simulated.
""")
st.sidebar.markdown("""
**License:** This work is licensed under a
<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Attribution-NonCommercial 4.0 International License</a>.
<br/><br/>
<a rel="license" href="http://creativecommons.org/l/by-nc/4.0/88x31.png" />
""", unsafe_allow_html=True)


# --- Data Simulation & Constants ---
SETUP_TIME_MINS = 60 # Time in minutes for a major line changeover (e.g., new chassis type)
MINS_PER_SHIFT = 480 # 8-hour shift

def get_production_orders():
    """Creates a DataFrame simulating a list of daily production orders."""
    orders = []
    num_orders = 10
    chassis_types = ['Gaming Tower', 'Office Mini', 'All-in-One']
    for i in range(num_orders):
        chassis = random.choice(chassis_types)
        quantity = random.randint(10, 50)
        profit = random.randint(150, 400) if chassis == 'Gaming Tower' else random.randint(80, 120)
        
        orders.append({
            'OrderID': f"WO-0{i+1}",
            'Chassis_Type': chassis,
            'Quantity': quantity,
            'Profit_Per_Unit': profit,
            'Production_Time_Mins': quantity * 2 # 2 minutes per unit
        })
    return pd.DataFrame(orders)

# --- Agent & Calculation Logic ---
def calculate_schedule_metrics(schedule_df):
    """Calculates total time, setup time, and other metrics for a given schedule."""
    total_production_time = schedule_df['Production_Time_Mins'].sum()
    total_setup_time = 0
    
    # Iterate through the schedule to calculate setup time
    last_chassis = None
    for index, row in schedule_df.iterrows():
        if last_chassis is not None and row['Chassis_Type'] != last_chassis:
            total_setup_time += SETUP_TIME_MINS
        last_chassis = row['Chassis_Type']
        
    total_time = total_production_time + total_setup_time
    return {
        "total_time": total_time,
        "setup_time": total_setup_time,
        "production_time": total_production_time
    }

def run_maestro_agent(df):
    """The agent's logic: sort by the primary constraint (Chassis_Type) to minimize setup."""
    # This is a heuristic for the optimization problem.
    # It sorts by the most time-consuming changeover factor.
    optimized_df = df.sort_values(by='Chassis_Type', kind='mergesort').reset_index(drop=True)
    
    reasoning = "Agent analyzed all orders and identified **Chassis Type** as the primary driver of setup time. It has re-sequenced the queue to group similar chassis builds together, minimizing line changeovers."
    
    return optimized_df, reasoning

# --- Main App UI ---
if 'orders' not in st.session_state:
    st.session_state.orders = get_production_orders()
    st.session_state.optimized_schedule = None
    st.session_state.history = []

st.header("Daily Production Schedule Simulation")
st.markdown("Comparing a standard 'First-In, First-Out' (FIFO) schedule with the agent's optimized sequence.")

col1, col2 = st.columns(2)

# --- Naive FIFO Schedule ---
with col1:
    st.subheader("Standard FIFO Schedule")
    naive_schedule = st.session_state.orders
    # CORRECTED LINE: Ensured the st.dataframe call is syntactically correct.
    st.dataframe(naive_schedule, use_container_width=True, hide_index=True)
    naive_metrics = calculate_schedule_metrics(naive_schedule)
    st.info(f"**Total Time Required:** {naive_metrics['total_time']} mins ({naive_metrics['total_time']/60:.2f} hours)\n\n**Total Setup Time:** {naive_metrics['setup_time']} mins")

# --- Optimized Schedule ---
with col2:
    st.subheader("🎼 Agent's Optimized Schedule")
    if st.session_state.optimized_schedule is not None:
        optimized_schedule = st.session_state.optimized_schedule
        st.dataframe(optimized_schedule, use_container_width=True, hide_index=True)
        optimized_metrics = calculate_schedule_metrics(optimized_schedule)
        st.success(f"**Total Time Required:** {optimized_metrics['total_time']} mins ({optimized_metrics['total_time']/60:.2f} hours)\n\n**Total Setup Time:** {optimized_metrics['setup_time']} mins")
    else:
        st.info("Run the agent to see the optimized schedule.")

st.divider()

# --- Control & Agent Log ---
st.header("Agent Control & Reasoning")
if st.button("🎼 Run Production Maestro Agent", type="primary"):
    optimized_df, reasoning = run_maestro_agent(st.session_state.orders)
    st.session_state.optimized_schedule = optimized_df
    st.session_state.reasoning = reasoning
    
    # Calculate impact for history
    naive_metrics = calculate_schedule_metrics(st.session_state.orders)
    optimized_metrics = calculate_schedule_metrics(optimized_df)
    time_saved = naive_metrics['total_time'] - optimized_metrics['total_time']
    # Assume average profit and time per unit for extra production
    avg_profit_per_min = st.session_state.orders['Profit_Per_Unit'].mean() / 2
    additional_profit = time_saved * avg_profit_per_min
    
    run_number = len(st.session_state.history) + 1
    st.session_state.history.append({
        'Run': run_number,
        'Time Saved (Mins)': time_saved,
        'Additional Profit': additional_profit if additional_profit > 0 else 0
    })
    st.rerun()

if st.button("🔄 Generate New Order List"):
    st.session_state.orders = get_production_orders()
    st.session_state.optimized_schedule = None
    st.session_state.reasoning = None
    st.session_state.history = []
    st.rerun()

if 'reasoning' in st.session_state and st.session_state.reasoning:
    st.info(f"**Agent's Reasoning:** {st.session_state.reasoning}")

st.divider()

# --- Tangible Benefit Simulation Section ---
st.header("📈 Tangible Benefit Simulation")
if st.session_state.optimized_schedule is not None:
    naive_metrics = calculate_schedule_metrics(st.session_state.orders)
    optimized_metrics = calculate_schedule_metrics(st.session_state.optimized_schedule)
    
    time_saved = naive_metrics['total_time'] - optimized_metrics['total_time']
    units_per_min = st.session_state.orders['Quantity'].sum() / st.session_state.orders['Production_Time_Mins'].sum()
    additional_units = int(time_saved * units_per_min)
    avg_profit_per_unit = st.session_state.orders['Profit_Per_Unit'].mean()
    additional_profit = additional_units * avg_profit_per_unit

    st.subheader("Latest Simulation Run Analysis")
    if time_saved > 0:
        c1, c2, c3 = st.columns(3)
        c1.metric("Time Saved by Agent", f"{time_saved} Mins", delta=f"{time_saved} Mins Saved")
        c2.metric("Additional Production Capacity", f"~{additional_units} Units", help="Estimated additional units that can be produced in the time saved.")
        c3.metric("Additional Profit Opportunity", f"${additional_profit:,.0f}", help="Estimated profit from producing additional units.")
    else:
        st.success("The initial schedule was already optimal. No time savings identified in this run.")
        
    # --- Cumulative & Trend Analysis ---
    if len(st.session_state.history) > 0:
        st.subheader("Cumulative & Trend Analysis (All Runs)")
        history_df = pd.DataFrame(st.session_state.history)
        
        c4, c5 = st.columns(2)
        with c4:
            total_profit = history_df['Additional Profit'].sum()
            st.metric("Total Additional Profit (All Runs)", f"${total_profit:,.0f}")
        with c5:
            st.markdown("**Additional Profit Trend**")
            st.bar_chart(history_df.set_index('Run')['Additional Profit'])
else:
    st.info("Run the agent to see the financial impact analysis.")
