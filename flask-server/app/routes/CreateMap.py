from flask import Flask, request, jsonify, Blueprint
import folium
from app.services.DataService import process_data
"""
# Define new Blueprint "CreateMapBP" to register in __init__.py
bp = Blueprint("CreateMapBP", __name__)

@bp.route("/createMap", methods=["POST"])
def createMap():
    
    Route to create a Folium map with choropleth layer based on provided data.

    Expected JSON input format:
    {
        "latitude": float,
        "longitude": float
    }

    Returns:
        JSON response with a message indicating success or failure.
    
    try:
        # Extract latitude and longitude from the incoming JSON request
        data = request.json
        centre_lat, centre_long = data["latitude"], data["longitude"]

        # Create a Folium map centered at the provided latitude and longitude
        m = folium.Map(
            location=[centre_lat, centre_long],  # Center the map at the specified coordinates
            zoom_start=13,                      # Set the initial zoom level
            min_lat=52.3587305,                 # Define latitude bounds for the map
            max_lat=55.0309801,
            min_lon=-5.3973485,                 # Define longitude bounds for the map
            max_lon=6.0082506
        )

        # Retrieve geojson and aggregated data using the process_data function from DataService
        geojson_data = process_data()["geojson_data"]
        aggregated_data = process_data()["aggregated_data"]

        # Add a Choropleth layer to the map, visualizing COVID-19 deaths data
        folium.Choropleth(
            geo_data=geojson_data,                 # GeoJSON data to use for the map features
            data=aggregated_data,                  # Data to visualize on the map
            columns=['LAD21NM', 'total_deaths'],   # Columns to use for features and values
            key_on='feature.properties.LAD21NM',   # Key to match data with GeoJSON features
            fill_color='YlGnBu',                   # Color scheme for the Choropleth layer
            fill_opacity=0.4,                      # Opacity of the fill color
            line_opacity=0.5,                      # Opacity of the border lines
            legend_name='Total COVID-19 Deaths'    # Legend name for the Choropleth layer
        ).add_to(m)

        # Return a success message as JSON
        return jsonify({"message": "success"})

    except Exception as e:
        # Print the error message to the console and return it in the response
        print("Issue with creating map:", e)
        return jsonify({"message": str(e)})
"""