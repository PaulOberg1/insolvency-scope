import pandas as pd
import geopandas as gpd

def load_data():
    """
    Loads data from file paths into GeoDataFrame and DataFrame objects.

    Returns:
        tuple: A tuple containing:
            - GeoDataFrame: Contains the geographical boundaries data.
            - DataFrame: Contains the case data from the CSV.
    """
    geojson_path = 'app/data/ukboundarylines.geojson'
    excel_path = 'app/data/finalcases.csv'
    
    # Load geographic data from GeoJSON file
    geojson_data = gpd.read_file(geojson_path)
    
    # Load tabular data from CSV file
    excel_data = pd.read_csv(excel_path)
    
    return geojson_data, excel_data

def process_data():
    """
    Processes and merges geographic and tabular data.

    Returns:
        dict: A dictionary containing:
            - 'aggregated_data': DataFrame with aggregated death counts per area.
            - 'geojson_data': Original GeoDataFrame.
            - 'valid_geojson_data': GeoDataFrame with valid geometries only.
    """
    # Load data
    geojson_data, excel_data = load_data()
    
    # Copy original GeoDataFrame
    original_geojson_data = geojson_data.copy()
    
    # Filter out rows with missing or invalid geometries
    valid_geojson_data = geojson_data.dropna(subset=['geometry'])
    valid_geojson_data = valid_geojson_data[valid_geojson_data['geometry'].is_valid]
    
    # Merge geographic data with case data based on common area names
    merged_data = pd.merge(valid_geojson_data, excel_data, how='left', left_on='LAD21NM', right_on='Area name')
    
    # Merge the original GeoDataFrame with the newly merged data
    merged_geojson_data = pd.merge(original_geojson_data, merged_data, how='left', left_on='LAD21NM', right_on='LAD21NM')
    
    # Aggregate death counts and store them in a DataFrame
    aggregated_data = merged_geojson_data.groupby('LAD21NM').agg(
        total_deaths=('Deaths', 'sum'),
        specific_deaths=('Deaths', lambda x: list(x))  # Collect individual deaths into a list
    ).reset_index()
    
    # Return the processed data
    return {
        "aggregated_data": aggregated_data,
        "geojson_data": geojson_data,
        "valid_geojson_data": valid_geojson_data
    }
