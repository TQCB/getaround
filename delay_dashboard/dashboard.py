import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np

### Config
st.set_page_config(
    page_title="E-commerce",
    page_icon="💸 ",
    layout="wide"
)

if __name__ == '__main__':
    ############################################################################
    # DATA IMPORT AND PROCESSING
    ############################################################################
    @st.cache_data
    def import_data(path):
        return pd.read_excel(path)
    
    data = import_data('../data/get_around_delay_analysis.xlsx')
    data.rename(columns={
        'rental_id' : 'id',
        'checkin_type' : 'type',
        'delay_at_checkout_in_minutes' : 'delay',
        'previous_ended_rental_id' : 'last_id',
        'time_delta_with_previous_rental_in_minutes' : 'last_delta'
        }, inplace=True)
    
    data_affected = data[['id', 'delay', 'type', 'state']].rename(columns={
        'id':'last_id',
        'delay':'last_delay',
        'type':'last_type',
        'state':'last_state'
        })
    
    data_affected = data.merge(data_affected, how='inner', on='last_id')
    
    ############################################################################
    ############################################################################
    # TABS
    ############################################################################
    ############################################################################
    dashboard_tab, prediction_tab = st.tabs(['Dashboard', 'Predictions']) 

    ############################################################################
    # DASHBOARD
    ############################################################################
    with dashboard_tab:
        st.header("Statistics")
        
        st.caption("Note: We filter our data to trips that contain information\
                   about a previous trip.")
        
        metric_col_1, metric_col_2, metric_col_3, metric_col_4 = st.columns(4)
        
        #NOTE: MAKE THESE VALUES VARIABLES AND CALL THEM BACK LATER
        metric_col_1.metric(label='Average Delay',value=f"{round(np.mean(data_affected['delay']), 1)} mins")
        metric_col_2.metric(label='Average Time Between Rentals',value=f"{round(np.mean(data_affected['last_delta']), 1)} mins")
        metric_col_3.metric(label='Average Time Between Rentals',value=f"{round(np.mean(data_affected['last_delta']), 1)} mins")
        metric_col_4.metric(label='Average Time Between Rentals',value=f"{round(np.mean(data_affected['last_delta']), 1)} mins")
        
        st.write(data_affected.head())
    ############################################################################
    # PREDICTION
    ############################################################################
    # with prediction_tab:@