from shapely.geometry import Point,shape,LineString
import geopandas as gpd
import pandas as pd
from app.services.DataService import process_data

def getSafestRoute(routes):
    """
    Determines the safest route based on aggregated death counts associated with route intersections.

    Input:
        routes (list): A list of route dictionaries, where each dictionary contains:
            - 'geometry': A dictionary with 'coordinates' key representing the route's coordinates.

    Returns:
        The route dictionary with the minimum risk (i.e., the route with the lowest total deaths).

    """

    # Create a GeoDataFrame for routes
    route_lines = []
    for i,route in enumerate(routes):
        route["id"]=i
        coordinates = route['geometry']['coordinates']
        line = LineString(coordinates)
        route_lines.append({'route_id': i, 'geometry': line})
    route_gdf = gpd.GeoDataFrame(route_lines, geometry='geometry')
    
    # Assign a CRS to route_gdf (assuming EPSG:4326 as an example)
    route_gdf.crs = "EPSG:4326"

    #Access relevant data from data stores
    aggregated_data = process_data()["aggregated_data"]
    valid_geojson_data = process_data()["valid_geojson_data"]


    # Reproject route_gdf to match the CRS of valid_geojson_data
    route_gdf = route_gdf.to_crs(valid_geojson_data.crs)
    
    # Perform spatial join to determine intersections
    joined_gdf = gpd.sjoin(route_gdf, valid_geojson_data, how='inner', op='intersects')
    
    # Check if the join produced results
    if joined_gdf.empty:
        raise ValueError("No intersecting polygons found for any routes.")
    
    # Merge the joined_gdf with aggregated_data to get the death counts
    joined_gdf = joined_gdf.merge(aggregated_data[['LAD21NM', 'total_deaths']], on='LAD21NM', how='left')
    
    # Aggregate total deaths for each route
    route_deaths = joined_gdf.groupby('route_id').apply(lambda x: x['total_deaths'].sum())
    
    # Find the route with the minimum risk (total number of deaths)
    safest_route_id = route_deaths.idxmin()
    
    # Handle case where there might be no valid routes
    if pd.isna(safest_route_id):
        raise ValueError("Unable to determine the safest route with minimum risk.")
    
    #Retrieve safest route
    safest_route = next(route for route in routes if route['id'] == safest_route_id)
    
    return safest_route