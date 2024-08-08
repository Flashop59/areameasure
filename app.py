import streamlit as st
import pandas as pd
import requests
import numpy as np
from datetime import datetime, timedelta
from shapely.geometry import Polygon
from scipy.spatial import ConvexHull
from geopy.distance import geodesic

# Function to fetch data from Ensure IoT API
def fetch_iot_data(api_key, vehicle, start_timestamp, end_timestamp):
    headers = {
        'token': api_key
    }
    url = f"https://admintestapi.ensuresystem.in/api/locationpull/orbit?vehicle={vehicle}&from={start_timestamp}&to={end_timestamp}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return []

# Function to convert UTC to IST
def convert_to_ist(utc_time):
    try:
        utc_datetime = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        utc_datetime = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S.%f')
    ist_datetime = utc_datetime + timedelta(hours=5, minutes=30)
    return ist_datetime.strftime('%Y-%m-%d %H:%M:%S')

# Function to process the data and return a DataFrame
def process_data(data):
    processed_data = []
    for index, entry in enumerate(data):
        try:
            ist_time = convert_to_ist(entry['time'])
            processed_data.append([
                ist_time,
                entry['lat'],
                entry['lon'],
                entry['odometer'],
                entry['state'],
                index + 1
            ])
        except KeyError as e:
            st.error(f"Missing key in data: {e}")
            continue
    return pd.DataFrame(processed_data, columns=["Timestamp", "lat", "lng", "Odometer", "State", "Point"])

# Function to calculate the area of a field in square meters using convex hull
def calculate_convex_hull_area(points):
    if len(points) < 3:  # Not enough points to form a polygon
        return 0
    try:
        hull = ConvexHull(points)
        poly = Polygon(points[hull.vertices])
        return poly.area  # Area in square degrees
    except Exception:
        return 0

# Streamlit app
st.title("IoT Data Fetching, Processing, and Area Calculation")

# Input fields for API Key, Vehicle ID, and date range
api_key = st.text_input("API Key", value="3330d953-7abc-4bac-b862-ac315c8e2387-6252fa58-d2c2-4c13-b23e-59cefafa4d7d")
vehicle = st.text_input("Vehicle ID")
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

if st.button("Fetch Data"):
    if api_key and vehicle and start_date and end_date:
        start_timestamp = int(datetime.combine(start_date, datetime.min.time()).timestamp() * 1000)
        end_timestamp = int(datetime.combine(end_date, datetime.max.time()).timestamp() * 1000)
        
        data = fetch_iot_data(api_key, vehicle, start_timestamp, end_timestamp)
        if data:
            df = process_data(data)
            st.write("Fetched Data:", df)
            
            # Calculate the area using convex hull
            points = df[['lat', 'lng']].values
            area_square_degrees = calculate_convex_hull_area(points)
            area_square_meters = area_square_degrees * (111000 ** 2)  # Conversion to square meters
            
            st.write(f"Calculated Field Area: {area_square_meters:.2f} square meters")
            
            # Optionally, you can further process and visualize the data as needed
    else:
        st.error("Please provide all inputs.")
