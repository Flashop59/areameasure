import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from shapely.geometry import Polygon
from shapely.ops import transform
from pyproj import Proj, transform
import geopy.distance
from io import BytesIO

# Constants
in_proj = Proj(init='epsg:4326')
out_proj = Proj(proj='aea', lat_1=29.5, lat_2=45.5)

# Function to calculate the convex hull area
def calculate_convex_hull_area(coords):
    try:
        polygon = Polygon(coords)
        area = transform(in_proj, out_proj, polygon).area
        return area
    except Exception as e:
        print(f"Error calculating convex hull area: {e}")
        return 0

# Function to process the uploaded file
def process_file(uploaded_file):
    # Read the CSV file
    df = pd.read_csv(uploaded_file)

    # Calculate field areas
    field_areas = df.groupby('field_id').apply(
        lambda df: calculate_convex_hull_area(df[['lat', 'lng']].values)
    )
    field_areas_m2 = field_areas / 10000  # Convert from m^2 to hectares

    # Calculate centroids
    field_centroids = df.groupby('field_id')[['lat', 'lng']].mean()

    # Calculate travel distances
    distances = []
    for i in range(len(field_centroids) - 1):
        centroid1 = field_centroids.iloc[i]
        centroid2 = field_centroids.iloc[i + 1]
        distance = geopy.distance.geodesic((centroid1['lat'], centroid1['lng']), (centroid2['lat'], centroid2['lng'])).kilometers
        distances.append(distance)
    
    total_distance = np.sum(distances)
    
    # Prepare the results dataframe
    combined_df = pd.DataFrame({
        'field_id': field_areas.index,
        'area_hectares': field_areas_m2,
        'centroid_lat': field_centroids['lat'],
        'centroid_lng': field_centroids['lng']
    })
    
    # Create the map
    m = folium.Map(location=[df['lat'].mean(), df['lng'].mean()], zoom_start=10)
    
    # Add the field areas to the map
    for _, row in combined_df.iterrows():
        folium.Marker(location=[row['centroid_lat'], row['centroid_lng']], 
                      popup=f"Field ID: {row['field_id']}<br>Area: {row['area_hectares']:.2f} ha").add_to(m)

    # Save the map to an HTML file
    map_file_path = '/mnt/data/map.html'
    m.save(map_file_path)
    
    return map_file_path, combined_df

# Streamlit app layout
st.title("Field Area and Distance Calculator")
st.write("Upload a CSV file containing 'field_id', 'lat', and 'lng' columns.")

uploaded_file = st.file_uploader("Choose a file...", type="csv")

if uploaded_file is not None:
    map_file_path, combined_df = process_file(uploaded_file)
    
    st.write("### Field Areas and Centroids")
    st.dataframe(combined_df)
    
    st.write("### Total Travel Distance")
    total_distance = combined_df.apply(
        lambda row: geopy.distance.geodesic(
            (row['centroid_lat'], row['centroid_lng']),
            (combined_df.iloc[0]['centroid_lat'], combined_df.iloc[0]['centroid_lng'])
        ).km, axis=1).sum()
    st.write(f"Total distance to cover all fields: {total_distance:.2f} km")
    
    st.write("### Map of Fields")
    st.write("You can download the map below.")
    with open(map_file_path, "rb") as file:
        btn = st.download_button(
            label="Download Map as HTML",
            data=file,
            file_name="map.html",
            mime="text/html"
        )
