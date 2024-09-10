import folium
from app.services.DataService import process_data

def generateMap(centre_lat, centre_long, lineSeg):
    """
    Generates an interactive map with a choropleth layer showing COVID-19 death counts and a route line.

    Args:
        centre_lat (float): Latitude for the center of the map.
        centre_long (float): Longitude for the center of the map.
        lineSeg (list): List of coordinates defining the route as a LineString.

    Returns:
        None: Saves the generated map as an HTML file.
    """
    # Create a Folium map centered at the specified latitude and longitude
    # with a defined zoom level and bounding box
    map = folium.Map(
        location=[centre_lat, centre_long],
        zoom_start=15,
        min_lat=52.3587305, max_lat=55.0309801,
        min_lon=-5.3973485, max_lon=6.0082506
    )
    
    # Retrieve geojson and aggregated data from the DataService
    geojson_data = process_data()["geojson_data"]
    aggregated_data = process_data()["aggregated_data"]

    # Add a Choropleth layer to the map to visualize total COVID-19 deaths
    folium.Choropleth(
        geo_data=geojson_data,
        data=aggregated_data,
        columns=['LAD21NM', 'total_deaths'],
        key_on='feature.properties.LAD21NM',
        fill_color='YlGnBu',
        fill_opacity=0.4,
        line_opacity=0.5,
        legend_name='Total COVID-19 Deaths'
    ).add_to(map)

    # Define a function to style the route line
    def optimalLineStyle(feature):
        return {
            'fillColor': '#ed980c',  # Color of the line
            'color': '#ed980c',      # Border color of the line
            'weight': 4              # Thickness of the line
        }

    # Create a GeoJSON feature for the route line
    geojson_data = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": lineSeg
        },
        "properties": {}
    }

    # Add the route line to the map with the defined style
    folium.GeoJson(geojson_data, style_function=optimalLineStyle).add_to(map)

    # Add markers for the start and end points of the route
    startPoint = lineSeg[0][::-1]
    endPoint = lineSeg[-1][::-1]
    print(startPoint,endPoint)
    folium.Marker(location=startPoint, popup="Start Point").add_to(map)
    folium.Marker(location=endPoint, popup="End Point").add_to(map)

    # Save the generated map to an HTML file in the 'static' directory
    map.save("app/static/routeMap.html")
