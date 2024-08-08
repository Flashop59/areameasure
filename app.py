import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# Function to convert UTC to IST
def convert_to_ist(utc_time):
    try:
        utc_datetime = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        # Handle formats without microseconds
        utc_datetime = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S')
    ist_datetime = utc_datetime + timedelta(hours=5, minutes=30)
    return ist_datetime.strftime('%Y-%m-%d %H:%M:%S')

# Function to process the fetched data
def process_data(data):
    processed_data = []
    if isinstance(data, list):
        for index, entry in enumerate(data):
            try:
                timestamp = entry.get('time')
                lat = entry.get('lat', 'N/A')
                lon = entry.get('lon', 'N/A')
                odometer = entry.get('odometer', 'N/A')
                state = entry.get('state', 'N/A')

                if timestamp:
                    ist_time = convert_to_ist(timestamp)
                else:
                    ist_time = 'Invalid Timestamp'

                processed_data.append([
                    ist_time,
                    lat,
                    lon,
                    odometer,
                    state,
                    index + 1
                ])
            except Exception as e:
                st.error(f"Error processing entry {index}: {e}")
                continue
    else:
        st.error("Unexpected data format. Expected a list.")
    
    return pd.DataFrame(processed_data, columns=["Timestamp", "lat", "lng", "Odometer", "State", "Point"])

# Function to fetch data from API
def fetch_data(vehicle, start_time, end_time):
    api_url = f"https://admintestapi.ensuresystem.in/api/locationpull/orbit?vehicle={vehicle}&from={start_time}&to={end_time}"
    headers = {
        "token": "3330d953-7abc-4bac-b862-ac315c8e2387-6252fa58-d2c2-4c13-b23e-59cefafa4d7d"
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad HTTP status codes
        data = response.json()
        
        if not isinstance(data, list):
            st.error("API response is not a list. Response received: {}".format(data))
            return []
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"HTTP Request failed: {e}")
        return []

# Streamlit UI
st.title("Vehicle Data Fetcher")

# Input fields
vehicle = st.text_input("Vehicle ID", value="BR1")
start_timestamp = st.date_input("Start Date", value=datetime(2024, 7, 30))
start_time = st.time_input("Start Time", value=datetime.strptime('00:00:00', '%H:%M:%S').time())
end_timestamp = st.date_input("End Date", value=datetime(2024, 7, 30))
end_time = st.time_input("End Time", value=datetime.strptime('23:59:59', '%H:%M:%S').time())

# Combine date and time for API request
start_datetime = datetime.combine(start_timestamp, start_time)
end_datetime = datetime.combine(end_timestamp, end_time)

# Fetch data button
if st.button("Fetch Data"):
    start_time_str = start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    end_time_str = end_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
    st.write(f"Fetching data for vehicle: {vehicle} from {start_time_str} to {end_time_str}")
    
    data = fetch_data(vehicle, start_time_str, end_time_str)
    if data:
        df = process_data(data)
        if not df.empty:
            st.write("Fetched Data:")
            st.dataframe(df)
        else:
            st.warning("No valid data available after processing.")
    else:
        st.warning("No data fetched or error occurred.")
