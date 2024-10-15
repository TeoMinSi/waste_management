import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime 
from streamlit_pills import pills
import plotly.graph_objects as go
import data_generation


with st.sidebar:
    st.image("full_logo.png")
    st.title('Waste Management Dashboard')

# st.title(":recycle: Waste Management Dashboard")

col1, col2 = st.columns(2, vertical_alignment="center")
with col1:
    st.image("Waste-management.svg", width=300)
with col2:
    st.write('''The Trash Management Dashboard is a digital platform designed to empower individuals, businesses, and government to monitor, manage, and reduce their waste effectively. 
         
By tracking trash levels in real-time and calculating waste emissions, the dashboard serves as a vital tool to help organizations work towards carbon-neutral goals.''')

df_columns=["DateTime", "Main_Owner", "2nd_Owner","Bin_ID","Load(KG)","Full(Y/N)"]
df = pd.read_csv('user1.csv', names=df_columns)
df['DateTime']  = pd.to_datetime(df['DateTime'])

st.subheader("Current Bin Capacity")

#retrieving the latest row in data
last_row = df.iloc[-1]
current_load = last_row["Load(KG)"]

#hardcoded max load
max_load = 150

percent_filled = (current_load / max_load)*100

if current_load > 59.6:
    st.markdown(
        """
        <style>
        .button_selected{
            display: inline-block;
            outline: 0;
            text-align: center;
            border: 1px solid #babfc3;
            padding: 8px;
            min-height: 36px;
            min-width: 36px;
            color: #ffffff;
            background: #142c1c;
            border-radius: 4px;
            font-weight: 500;
            font-size: 14px;
            box-shadow: rgba(0, 0, 0, 0.05) 0px 1px 0px 0px;
        }

        .button_unselected{
            display: inline-block;
            outline: 0;
            text-align: center;
            border: 1px solid #babfc3;
            padding: 8px;
            min-height: 36px;
            min-width: 36px;
            color: #142c1c;
            background: #e8f3f5;
            border-radius: 4px;
            font-weight: 500;
            font-size: 14px;
            box-shadow: rgba(0, 0, 0, 0.05) 0px 1px 0px 0px;
        }    
                        
        </style>             
        <div>
            <p class='button_selected'>Loaded</p>
            <p class='button_unselected'>Unloaded</p>
        </div>
        """,
        unsafe_allow_html=True,
        )
    
else:
    st.markdown(
    """
    <style>
    .button_selected{
        display: inline-block;
        outline: 0;
        text-align: center;
        border: 1px solid #babfc3;
        padding: 8px;
        min-height: 36px;
        min-width: 36px;
        color: #ffffff;
        background: #142c1c;
        border-radius: 4px;
        font-weight: 500;
        font-size: 14px;
        box-shadow: rgba(0, 0, 0, 0.05) 0px 1px 0px 0px;
    }

    .button_unselected{
        display: inline-block;
        outline: 0;
        text-align: center;
        border: 1px solid #babfc3;
        padding: 8px;
        min-height: 36px;
        min-width: 36px;
        color: #142c1c;
        background: #e8f3f5;
        border-radius: 4px;
        font-weight: 500;
        font-size: 14px;
        box-shadow: rgba(0, 0, 0, 0.05) 0px 1px 0px 0px;
    }    
                    
    </style>             
    <div>
        <p class='button_unselected'>Loaded</p>
        <p class='button_selected'>Unloaded</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write(f"Bin Capacity as of {pd.to_datetime(last_row["DateTime"]).floor('S')} is {current_load}kg.")
fig = go.Figure(go.Indicator(
    mode = "gauge+number",
        number = {'suffix':"%"},
    gauge = {'bar': {'color': "#142c1c"},},
    value = percent_filled,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "Bin Capacity (Percentage)"}))
    

st.plotly_chart(fig)


cleaned_df = df.drop(columns=['Main_Owner', '2nd_Owner',"Full(Y/N)"], axis=1)
# cleaned_df['Labels'] = ['Loaded' if x > 0 else 'Unloaded' for x in cleaned_df['Load(KG)']]

fake_data_df = data_generation.data_generation()
fake_data_df['DateTime']  = pd.to_datetime(fake_data_df['DateTime'])

joined_df = pd.concat([fake_data_df, cleaned_df], ignore_index=True, sort=False)


realtime_df = joined_df.groupby(["Bin_ID", pd.Grouper(key='DateTime', axis=0, freq='1min')]).last().reset_index()
hourly_df = realtime_df.groupby(["Bin_ID", pd.Grouper(key='DateTime', axis=0, freq='60min')]).last().reset_index()
daily_df = realtime_df.groupby(["Bin_ID", pd.Grouper(key='DateTime', axis=0, freq='24h')]).last().reset_index()
weekly_df = realtime_df.groupby(["Bin_ID", pd.Grouper(key='DateTime', axis=0, freq='7d')]).last().reset_index()
monthly_df = realtime_df.groupby(["Bin_ID", pd.Grouper(key='DateTime', axis=0, freq='1m')]).last().reset_index()



realtime_df.fillna(method='ffill', inplace=True)
realtime_df = realtime_df.tail(60)

hourly_df.fillna(method='ffill', inplace=True)
hourly_df = hourly_df.tail(96)

daily_df.fillna(method='ffill', inplace=True)
daily_df = daily_df.tail(30)

weekly_df.fillna(method='ffill', inplace=True)
weekly_df = weekly_df.tail(52)

monthly_df.fillna(method='ffill', inplace=True)
monthly_df = monthly_df.tail(24)




#charts

#realtime chart
realtime_fig = px.line(realtime_df, x="DateTime", y="Load(KG)", title='Total Waste Load in Bins', hover_data=["Load(KG)"], color="Bin_ID") 
realtime_fig.update_traces(mode="lines")
realtime_fig.update_layout(hovermode="x unified")
realtime_fig.add_hline(y=100, line_dash="dot",
              annotation_text="outliers", 
              annotation_position="top right",
              annotation_font_size=15,
              annotation_font_color="blue"
             )
#hourly chart
# hourly_df['DateTime'] = hourly_df['DateTime'].dt.strftime('%d/%m %H')
hourly_fig = px.line(hourly_df, x="DateTime", y="Load(KG)", title='Total Waste Load in Bins', hover_data=["Load(KG)"], color="Bin_ID")
hourly_fig.update_traces(mode="lines")
hourly_fig.update_layout(hovermode="x unified")
hourly_fig.add_hline(y=100, line_dash="dot",
              annotation_text="outliers", 
              annotation_position="top right",
              annotation_font_size=15,
              annotation_font_color="blue"
             )

#daily charts
daily_df['DateTime'] = daily_df['DateTime'].dt.strftime('%d/%m/%y')
daily_fig = px.line(daily_df, x="DateTime", y="Load(KG)", title='Total Waste Load in Bins', hover_data=["Load(KG)"], color="Bin_ID")
daily_fig.update_traces(mode="markers+lines")
daily_fig.update_layout(hovermode="x unified")
daily_fig.add_hline(y=100, line_dash="dot",
              annotation_text="outliers", 
              annotation_position="top right",
              annotation_font_size=15,
              annotation_font_color="blue"
             )


#weekly charts
weekly_df['DateTime'] = weekly_df['DateTime'].dt.strftime('%d/%m/%y')
weekly_fig = px.line(weekly_df, x="DateTime", y="Load(KG)", title='Total Waste Load in Bins', hover_data=["Load(KG)"], color="Bin_ID")
weekly_fig.update_traces(mode="markers+lines")
weekly_fig.update_layout(hovermode="x unified")
weekly_fig.add_hline(y=100, line_dash="dot",
              annotation_text="outliers", 
              annotation_position="top right",
              annotation_font_size=15,
              annotation_font_color="blue"
             )


#monthly charts
monthly_df['DateTime'] = monthly_df['DateTime'].dt.strftime('%b-%y')
monthly_fig = px.line(monthly_df, x="DateTime", y="Load(KG)", title='Total Waste Load in Bins', hover_data=["Load(KG)"], color="Bin_ID")
monthly_fig.update_layout(xaxis=dict(tickformat="%b-%Y"), hovermode="x unified")
monthly_fig.update_traces(mode="markers+lines")
monthly_fig.add_hline(y=100, line_dash="dot",
              annotation_text="outliers", 
              annotation_position="top right",
              annotation_font_size=15,
              annotation_font_color="blue"
             )


time_period = pills("Select your time period", ["Real-time", "Hourly", "Daily", "Weekly", "Monthly"], index=0)
if time_period == "Real-time":
    st.subheader("Real Time Chart")
    tab1, tab2 = st.tabs(["Chart", "Data"])
    with tab1:
        st.write("Bin 1 is for General Waste while Bin 2 is for Recyclables.")
        st.plotly_chart(realtime_fig, use_container_width=True)
    with tab2:
        st.dataframe(realtime_df, use_container_width =True)


elif time_period == "Hourly":
    st.subheader("Hourly Time Chart")
    tab1, tab2 = st.tabs(["Chart", "Data"])
    with tab1:
        st.write("Bin 1 is for General Waste while Bin 2 is for Recyclables.")

        st.plotly_chart(hourly_fig, use_container_width=True)
    with tab2:
        st.dataframe(hourly_df, use_container_width =True)


elif time_period == "Daily":
    st.subheader("Daily Time Chart")
    tab1, tab2 = st.tabs(["Chart", "Data"])
    with tab1:
        st.write("Bin 1 is for General Waste while Bin 2 is for Recyclables.")

        st.plotly_chart(daily_fig, use_container_width=True)
    with tab2:
        st.dataframe(daily_df, use_container_width =True)


elif time_period == "Weekly":
    st.subheader("Weekly Time Chart")
    tab1, tab2 = st.tabs(["Chart", "Data"])
    with tab1:
        st.write("Bin 1 is for General Waste while Bin 2 is for Recyclables.")

        st.plotly_chart(weekly_fig, use_container_width=True)
    with tab2:
        st.dataframe(weekly_df, use_container_width =True)


else:
    st.subheader("Monthly Time Chart")
    tab1, tab2 = st.tabs(["Chart", "Data"])
    with tab1:
        st.write("Bin 1 is for General Waste while Bin 2 is for Recyclables.")

        st.plotly_chart(monthly_fig, use_container_width=True)
    with tab2:
        st.dataframe(monthly_df, use_container_width =True)

st.divider()

def activity_string(row):
    main_user = row["Main_Owner"]
    second_user = row["2nd_Owner"]
    binID = row["Bin_ID"]
    load = row["Load(KG)"]
    isFull = row["Full(Y/N)"]
    if isFull == "Y":
        full_str = "full"
    else:
        full_str= "not full"
    
    if load != 0:
        activity =  f'{main_user} and {second_user} loaded into {binID}. Total weight of load is {load}kg. Bin is {full_str}.'
    else:
        activity = f'{main_user} and {second_user} unloaded {binID}. Total weight of load is {load}kg.'
    return activity

st.subheader("Activity Table")
realtime_activity = df.groupby(pd.Grouper(key='DateTime', axis=0, freq='1min')).last().reset_index()
cleaned_realtime_activity = realtime_activity.dropna(thresh=2)
# st.write(cleaned_realtime_activity)
cleaned_realtime_activity['activity'] = cleaned_realtime_activity.apply(activity_string, axis=1)
cleaned_realtime_activity = cleaned_realtime_activity.drop(columns=['Main_Owner', '2nd_Owner',"Bin_ID", "Load(KG)" , "Full(Y/N)"], axis=1)
re_indexed = cleaned_realtime_activity.reset_index(drop=True)
st.dataframe(re_indexed, use_container_width =True)

_ ='''
Questions:
    1. Data pull - how often is the data updated in the csv and how often should we call the data refresh from AWS? 
        - Lead time from real time (current time) to the latest time displayed in the charts
        - every minute download a new csv from s3 bucket
    
    2. For the realtime, hourly and maybe the daily chart, need to limit the data entering the chart 
        - e.g for the real time chart, should we only display the last 6 hours of data? 
        - for the hourly chart, display last 24 hours of data?
        - real time - 60 data points, across 1 hour
        - hourly - 3 days 72 hours, 48 hours - see how it looks
        - daily - 30 days of data
        - weekly - 52 points (over a year)
        - month - 3 years

check if its possible to mark points on plotly if it meets a certain condition


    3. Check if current treatment of the grouping of data is correct.
        - e.g if there are multiple rows of data in 1 second, currently grouping all the rows and only taking the latest (or the last row) in each group
    4. Check if treatment of missing data is correct for the line charts
        - For missing days or missing times, currently filling the data with the last identified weight else charts will have many gaps


anomolies
- status - empty, partially filled, filled. Thresholds for the load weight

- above waste deposit time period and below summary. Show image for the status of the bins for the current latest minute (filled, partially filled, empty)
to deploy on streamlit first to use for demo.

wait for logo, images 
'''


_ ='''
Consuming from S3 bucket:
- from the code side, i require the region_name, aws_access_key_id, aws_secret_access_key

On the IAM dashboard. add a new user. configure access type. Give AmazonS3FullAccess permission.
Proceed to complete and create the user. Once user has been created, there should be an access key ID and secret access.
'''