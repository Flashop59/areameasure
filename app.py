import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def fetch_data(vehicle_id, start_time, end_time):
    url = 'https://admintestapi.ensuresystem.in/api/locationpull/orbit'
    headers = {"token": "3330d953-7abc-4bac-b862-ac315c8e2387-6252fa58-d2c2-4c13-b23e-59cefafa4d7d"}
    params = {
        'vehicle': vehicle_id,
        'from': start_time,
        'to': end_time
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        json_response = response.json()
        if isinstance(json_response, list):
            return json_response
        else:
            st.error(f"Unexpected data format: {json_response}")
            return None
    else:
        st.error(f"API request failed with status code {response.status_code}")
        return None

def convert_to_ist(utc_time):
    try:
        utc_datetime = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        utc_datetime = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    ist_datetime = utc_datetime + timedelta(hours=5, minutes=30)
    return ist_datetime

def process_data(data):
    processed_data = []
    for entry in data:
        try:
            ist_time = convert_to_ist(entry['time'])
            processed_data.append([
                ist_time.strftime('%Y-%m-%d %H:%M:%S'),
                entry['lat'],
                entry['lng'],
                entry['odometer'],
                entry['state'],
                entry.get('point', 'N/A')
            ])
        except Exception as e:
            st.error(f"Error processing entry: {e}")
    return pd.DataFrame(processed_data, columns=["Timestamp", "Latitude", "Longitude", "Odometer", "State", "Point"])

def plot_data(df):
    if not df.empty:
        plt.figure(figsize=(10, 6))
        plt.scatter(df['Longitude'], df['Latitude'], c='blue', label='Location')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Machine Locations')
        plt.legend()
        st.pyplot(plt)
    else:
        st.warning("No data to plot.")

st.title("Fetch and Visualize IoT Data")

vehicle_id = st.text_input("Vehicle ID")
start_time = st.date_input("Start Time", datetime.now())
end_time = st.date_input("End Time", datetime.now())

if st.button("Fetch Data"):
    # Format the dates as required by the API
    try:
        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S.000000Z')
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S.000000Z')
        
        st.write(f"Fetching data for vehicle: {vehicle_id} from {start_time_str} to {end_time_str}")
        
        data = fetch_data(vehicle_id, start_time_str, end_time_str)
        
        if data:
            df = process_data(data)
            st.write(df)
            plot_data(df)
    except Exception as e:
        st.error(f"Error: {e}")
