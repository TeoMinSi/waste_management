import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime 
from streamlit_pills import pills
import plotly.graph_objects as go
import data_generation
import boto3
from dotenv import load_dotenv
import os
import time
import datetime
from streamlit_autorefresh import st_autorefresh


st.set_page_config(layout="wide")

def configure():
    load_dotenv()

# uploading fake data to s3
# fake_data_df = data_generation.data_generation()
# fake_data_df['DateTime']  = pd.to_datetime(fake_data_df['DateTime'])

# joined_df = pd.concat([fake_data_df, df], ignore_index=True, sort=False)
# joined_df.to_csv('user2.csv')
# s3.Bucket('wastesortingbucket').upload_file(Filename='user2.csv',Key='user2.csv')
# st.write(joined_df)

# df_columns=["DateTime", "Main_Owner", "2nd_Owner","Bin_ID","Load(KG)","Full(Y/N)"]
# df = pd.read_csv('user1.csv', names=df_columns)

# df.columns = ["Empty","DateTime", "Main_Owner", "2nd_Owner","Bin_ID","Load(KG)","Full(Y/N)"]
# s3.Bucket('wastesortingbucket').upload_file(Filename='user2.csv',Key='user2.csv')
# st.write(joined_df)

configure()

s3 = boto3.resource(
    service_name='s3',
    region_name="ap-southeast-1",
    aws_access_key_id =os.getenv('aws_access_key_id'),
    aws_secret_access_key = os.getenv('aws_secret_access_key'),
)


def load_data():
    obj = s3.Bucket('wastesortingbucket').Object("user2.csv").get()
    df = pd.read_csv(obj["Body"], on_bad_lines='skip')
    # st.write(df)
    # df = pd.read_csv('user2.csv')
    # s3.Bucket('wastesortingbucket').upload_file(Filename='user2.csv',Key='user2.csv')
    return df    

placeholder = st.empty()

df = load_data()

with st.sidebar:
    st.image("full_logo.png")
    st.title('Waste Management Dashboard')
    st.image("Waste-management.svg", width=250)
    st.write('''The Trash Management Dashboard is a digital platform designed to empower individuals, businesses, and government to monitor, manage, and reduce their waste effectively. 

By tracking trash levels in real-time and calculating waste emissions, the dashboard serves as a vital tool to help organizations work towards carbon-neutral goals.''')

st_autorefresh(interval=30000)

# The function returns a counter for number of refreshes. This allows the
# ability to make special requests at different intervals based on the count

st.write(f"The data was last refreshed on {datetime.datetime.now()}.")

def realtime_charts(realtime_df):
    realtime_fig = px.line(realtime_df, x="DateTime", y="Load(KG)", title='Total Waste Load in Bins', hover_data=["Load(KG)"], color="Bin_ID") 
    realtime_fig.update_traces(mode="lines")
    realtime_fig.update_layout(hovermode="x unified")
    realtime_fig.add_hline(y=100, line_dash="dot",
            annotation_text="outliers", 
            annotation_position="top right",
            annotation_font_size=15,
            annotation_font_color="blue"
            )
    return realtime_fig

def hourly_charts(hourly_df):
    hourly_fig = px.line(hourly_df, x="DateTime", y="Load(KG)", title='Total Waste Load in Bins', hover_data=["Load(KG)"], color="Bin_ID")
    hourly_fig.update_traces(mode="lines")
    hourly_fig.update_layout(hovermode="x unified")
    hourly_fig.add_hline(y=100, line_dash="dot",
            annotation_text="outliers", 
            annotation_position="top right",
            annotation_font_size=15,
            annotation_font_color="blue"
            )
    return hourly_fig

def daily_charts(daily_df):
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
    return daily_fig

def weekly_charts(weekly_df):
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
    return weekly_fig

def monthly_charts(monthly_df):
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
    return monthly_fig

def bin_labels(row):
    if row["Bin_ID"] == "bin1":
        row["Material"] = "Plastic"
    if row["Bin_ID"] == "bin2":
        row["Material"] = "Cardboard"
    if row["Bin_ID"] == "bin3":
        row["Material"] = "Metal"
    return row

def bar_charts(realtime_df):
    new_monthly_df = realtime_df.groupby(["Bin_ID", pd.Grouper(key='DateTime', axis=0, freq='1m')]).sum().reset_index()
    new_monthly_df = new_monthly_df.apply(bin_labels, axis=1)
    new_monthly_df['ym-date'] = new_monthly_df['DateTime'].dt.strftime('%B-%Y')
    fig = px.histogram(new_monthly_df, x='ym-date', y='Load(KG)',color="Material",barmode='group',title='Breakdown of Recyclables')
    return fig

def gauge_visual(df):
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
                padding: 16px;
                margin-right:24px;
                min-height: 36px;
                min-width: 36px;
                color: #ffffff;
                background: #142c1c;
                border-radius: 4px;
                font-weight: 500;
                font-size: 24px;
                box-shadow: rgba(0, 0, 0, 0.05) 0px 1px 0px 0px;
            }

            .button_unselected{
                display: inline-block;
                outline: 0;
                text-align: center;
                border: 1px solid #babfc3;
                padding: 16px;
                margin-right:24px;
                min-height: 36px;
                min-width: 36px;
                color: #142c1c;
                background: #e8f3f5;
                border-radius: 4px;
                font-weight: 500;
                font-size: 24px;
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
    gauge_fig = go.Figure(go.Indicator(
        mode = "gauge+number",
            number = {'suffix':"%"},
        gauge = {'bar': {'color': "#142c1c"},'axis': {'range': [None, 100]}},
        value = percent_filled,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Bin Capacity (Percentage)"}))
            
    return gauge_fig


df['DateTime']  = pd.to_datetime(df['DateTime'])
cleaned_df = df.drop(columns=['Main_Owner', '2nd_Owner',"Full(Y/N)","EmptyCol"], axis=1)
# cleaned_df['Labels'] = ['Loaded' if x > 0 else 'Unloaded' for x in cleaned_df['Load(KG)']]
realtime_df = cleaned_df.groupby(["Bin_ID", pd.Grouper(key='DateTime', axis=0, freq='1min')]).last().reset_index()
hourly_df = realtime_df.groupby(["Bin_ID", pd.Grouper(key='DateTime', axis=0, freq='60min')]).last().reset_index()
daily_df = realtime_df.groupby(["Bin_ID", pd.Grouper(key='DateTime', axis=0, freq='24h')]).last().reset_index()
weekly_df = realtime_df.groupby(["Bin_ID", pd.Grouper(key='DateTime', axis=0, freq='7d')]).last().reset_index()
monthly_df = realtime_df.groupby(["Bin_ID", pd.Grouper(key='DateTime', axis=0, freq='1m')]).last().reset_index()



realtime_df.fillna(method='ffill', inplace=True)
realtime_df = realtime_df[realtime_df['DateTime'] > realtime_df['DateTime'].max() - pd.Timedelta(minutes=60)]

hourly_df.fillna(method='ffill', inplace=True)
hourly_df = hourly_df[hourly_df['DateTime'] > hourly_df['DateTime'].max() - pd.Timedelta(hours=165)]

daily_df.fillna(method='ffill', inplace=True)
daily_df = daily_df[daily_df['DateTime'] > daily_df['DateTime'].max() - pd.Timedelta(days=30)]

weekly_df.fillna(method='ffill', inplace=True)
weekly_df = weekly_df[weekly_df['DateTime'] > weekly_df['DateTime'].max() - pd.Timedelta(weeks=52)]

monthly_df.fillna(method='ffill', inplace=True)
monthly_df = monthly_df[monthly_df['DateTime'] > weekly_df['DateTime'].max() - pd.Timedelta(weeks=150)]


col1, col2 = st.columns(2)

with col1:
    st.header("Waste Data")
    time_period = pills("Select your time period", ["Real-time", "Hourly", "Daily", "Weekly", "Monthly"], index=0)
    if time_period == "Real-time":
        st.subheader("Real Time Chart")
        realtime_fig = realtime_charts(realtime_df)
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
            hourly_fig = hourly_charts(hourly_df)
            st.plotly_chart(hourly_fig, use_container_width=True)
        with tab2:
            st.dataframe(hourly_df, use_container_width =True)


    elif time_period == "Daily":
        st.subheader("Daily Time Chart")
        tab1, tab2 = st.tabs(["Chart", "Data"])
        with tab1:
            st.write("Bin 1 is for General Waste while Bin 2 is for Recyclables.")
            daily_fig = daily_charts(daily_df)
            st.plotly_chart(daily_fig, use_container_width=True)
        with tab2:
            st.dataframe(daily_df, use_container_width =True)


    elif time_period == "Weekly":
        st.subheader("Weekly Time Chart")
        tab1, tab2 = st.tabs(["Chart", "Data"])
        with tab1:
            st.write("Bin 1 is for General Waste while Bin 2 is for Recyclables.")
            weekly_fig = weekly_charts(weekly_df)
            st.plotly_chart(weekly_fig, use_container_width=True)
        with tab2:
            st.dataframe(weekly_df, use_container_width =True)


    else:
        st.subheader("Monthly Time Chart")
        tab1, tab2 = st.tabs(["Chart", "Data"])
        with tab1:
            st.write("Bin 1 is for Recyclables while Bin 2 is for Others.")
            monthly_fig = monthly_charts(monthly_df)
            st.plotly_chart(monthly_fig, use_container_width=True)
        with tab2:
            st.dataframe(monthly_df, use_container_width =True)

    st.divider()

    st.header("Collection Data")
    gauge_fig = gauge_visual(df)
    st.plotly_chart(gauge_fig)

with col2:
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

    st.header("Activity Table")
    realtime_activity = df.groupby(pd.Grouper(key='DateTime', axis=0, freq='1min')).last().reset_index()
    realtime_activity = realtime_activity.drop(['EmptyCol'], axis=1)
    cleaned_realtime_activity = realtime_activity.dropna(thresh=2)
    cleaned_realtime_activity['activity'] = cleaned_realtime_activity.apply(activity_string, axis=1)
    cleaned_realtime_activity = cleaned_realtime_activity.drop(columns=['Main_Owner', '2nd_Owner',"Bin_ID", "Load(KG)" , "Full(Y/N)"], axis=1)
    re_indexed = cleaned_realtime_activity.reset_index(drop=True)
    st.dataframe(re_indexed, use_container_width =True)

    st.divider()

    #recyclables chart
    fig = bar_charts(realtime_df)
    st.plotly_chart(fig, use_container_width=True)

