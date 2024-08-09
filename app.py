import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# API key
API_KEY = "3330d953-7abc-4bac-b862-ac315c8e2387-6252fa58-d2c2-4c13-b23e-59cefafa4d7d"

# Function to fetch data from the API
def fetch_data(vehicle, start_time, end_time):
    url = f"https://admintestapi.ensuresystem.in/api/locationpull/orbit?vehicle={vehicle}&from={start_time}&to={end_time}"
    headers = {"token": API_KEY}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Error fetching data: {response.status_code}")
        return None

    data = response.json()
    if not isinstance(data, list):
        st.error(f"Unexpected data format: {data}")
        return None
    
    # Sort data by time
    data.sort(key=lambda x: x['time'])
    return data

# Function to convert UTC to IST
def convert_to_ist(utc_time):
    date = datetime.fromtimestamp(utc_time / 1000)
    ist_time = date + timedelta(minutes=330)  # Adding 5 hours 30 minutes
    return ist_time.strftime('%Y-%m-%d %H:%M:%S')

# Function to process data and calculate area
def process_data(data):
    df = pd.DataFrame(data)
    df['Timestamp'] = df['time'].apply(convert_to_ist)
    df['lat'] = df['lat']
    df['lng'] = df['lon']
    df['Odometer'] = df['odometer']
    df['State'] = df['state']
    df['Point'] = df.index + 1
    
    # Additional calculations like distance, speed, and area estimation here
    # ...

    return df

# Streamlit UI
st.title("IoT Data Fetching and Area Calculation")

vehicle = st.text_input("Enter Vehicle ID (e.g., BR1):")
start_time = st.text_input("Enter Start Time (e.g., 2024-07-30 00:00:00):")
end_time = st.text_input("Enter End Time (e.g., 2024-07-30 23:59:59):")

if st.button("Fetch Data"):
    if vehicle and start_time and end_time:
        # Convert times to milliseconds since epoch
        start_time_epoch = int(datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
        end_time_epoch = int(datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)

        data = fetch_data(vehicle, start_time_epoch, end_time_epoch)
        if data:
            df = process_data(data)
            st.write("Fetched Data:")
            st.dataframe(df)
            
            # Area calculation can be implemented here
            # ...
        else:
            st.error("No data fetched or error occurred.")
    else:
        st.error("Please fill in all fields.")

