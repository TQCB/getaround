import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

### Config
st.set_page_config(
    page_title="E-commerce",
    page_icon="💸 ",
    layout="wide"
)

def categorize(value, n_interval):
            interval_size = 720/n_interval
            bin_edges = np.arange(0, 721, interval_size)
            
            for edge in bin_edges:
                if value < edge:
                    return edge
        
        
def plot_interval_cancels(df, n_interval):
    # Create df with mean cancel rate by delay interval
    df = df.copy()
    df['interval'] = df['last_delay'].apply(categorize, args=(n_interval,))
    df['state'] = df['state'].map({'ended':0, 'canceled':1})
    df = df.groupby(['interval', 'type'])['state'].agg(['mean', 'count']).reset_index()
    
    # Create figure
    fig = px.line(df, x='interval', y='mean', color='type')
    fig.add_trace(go.Bar(x=df['interval'], y=df['count']/2e3, marker_color='#888'))
    
    # Update axes and legend
    fig.update_xaxes(title_text='Delay (minutes)')
    fig.update_yaxes(title_text='Cancellation Rate')
    fig.update_traces(selector={'type':'bar'}, name='Amount of rentals')
    
    return fig

def min_delay(df, threshold, scope='all'):
    # Filter data to find trips to drop
    df_delay = df[(df['last_delta'] < threshold)]
    if scope != 'all':
        df_delay = df_delay[df_delay['type'] == scope]
    
    state_mask = df_delay['state'] == 'ended'
    
    # Dropped ended trips and canceled trips
    dt_e = df_delay[state_mask]
    dt_c = df_delay[~state_mask]
    
    return dt_e.shape[0], dt_c.shape[0]

if __name__ == '__main__':
    # DATA IMPORT AND PROCESSING
    @st.cache_data
    def load_data(path):
        return pd.read_excel(path)
    data = load_data('get_around_delay_analysis.xlsx')
    
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
    
    statistics_tab, prediction_tab = st.tabs(['Statistics', 'Predictions']) 
    
    # STATISTICS
    with statistics_tab:
        st.header("Statistics")
        
        st.caption("Note: We filter our data to trips that contain information\
                   about a previous trip.")
        
        metric_col_1, metric_col_2, metric_col_3, metric_col_4 = st.columns(4)
        
        average_checkout_delay = np.mean(data_affected['delay'])
        average_rental_delta = np.mean(data_affected['last_delta'])
        amount_total_rentals = data.shape[0]
        amount_consecutive_rentals = data_affected.shape[0] / data.shape[0] * 100
        
        metric_col_1.metric(label='Average Delay',value=f"{average_checkout_delay:.1f} mins")
        metric_col_2.metric(label='Average Time Between Rentals',value=f"{average_rental_delta:.1f} mins")
        metric_col_3.metric(label='Total Amount of Rentals',value=f"{amount_total_rentals}")
        metric_col_4.metric(label='Amount of consecutive rentals',value=f"{amount_consecutive_rentals:.2f}%")

        
        # Line plot of cancel rate in function of last trip's delay
        st.plotly_chart(plot_interval_cancels(data_affected, 7), use_container_width=True)
        
        delay_threshold = 360
        data_affected['had_delay'] = data_affected['last_delay'].apply(lambda x: 1 if x > delay_threshold else 0)
        
        fig = make_subplots(rows=2, cols=2,
                            column_titles=['Without Delay', 'With Delay'],
                            row_titles=['Type of Rental', 'State of Rental'],
                            specs=[[{'type': 'pie'}, {'type': 'pie'}],
                                   [{'type': 'pie'}, {'type': 'pie'}]])
        for x in [1,2]:
            for y in [1,2]:
                match y:
                    case 1:
                        delay_bool = False
                    case 2:
                        delay_bool = True
                
                match x:
                    case 1:
                        col_bool = 'type'
                    case 2:
                        col_bool = 'state'
                        
                fig.add_trace(go.Pie(
                    labels=data_affected.loc[data_affected['had_delay'] == delay_bool, col_bool]
                ),row=x, col=y
                )
        
        fig.update_layout(height=800)
        st.plotly_chart(fig, use_container_width=True)
    
    # PREDICTION
    with prediction_tab:
        with st.form(key='prediction_form'):
            pred_form_cols = st.columns([10, 10, 30, 20, 20])
            
            with pred_form_cols[0]:
                pred_threshold = st.number_input(label='Threshold (minutes)', min_value=0)
            with pred_form_cols[1]:
                pred_scope = st.radio(label='Scope', options=['all', 'connect', 'mobile'])
            
            submitted = st.form_submit_button(label='Predict impact')
            if submitted:
                dropped_ended_trips, dropped_canceled_trips = min_delay(data_affected, pred_threshold, pred_scope)
                
                # % of dropped trips that would've succesfully completed
                revenue_loss = (dropped_ended_trips - dropped_canceled_trips) / data.shape[0] * 100
                # % of canceled trips that were avoided
                friction_loss = dropped_ended_trips / data_affected[data_affected['state'] == 'canceled'].shape[0]
                                
                with pred_form_cols[3]:
                    st.metric(label='Unnecessarily Canceled Trips',
                              value=f'{revenue_loss:.2f}%',
                              delta='Revenue Loss',
                              delta_color='inverse')
                
                with pred_form_cols[4]:
                    st.metric(label='Canceled Trips Avoided',
                              value=f'{friction_loss:.2f}%',
                              delta='Friction Loss',
                              delta_color='normal')
            st.caption(
                'With more information on customer behaviour following\
                a trip they had to cancel, GetAround could estimate the cost\
                they would be willing to incur to avoid canceled trips caused\
                by delays.'
                )