import geopandas as gpd
import folium
import os
import webbrowser




import pandas as pd
import numpy as np
import geopandas as gpd
import json
import folium
from xgboost import XGBRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
import warnings

warnings.filterwarnings("ignore")

# --- Step 1: Load and preprocess insolvency data ---
df_wide = pd.read_excel("C:/covidapp/flask-server/app/static/Insolvencies.xlsx", sheet_name="Table_1b", header=4)

pattern = r'^[A-Za-z][1-9]'
df_wide = df_wide[~df_wide['Code'].astype(str).str.match(pattern)]

df_wide = df_wide.drop(columns=['Code', 'Geography', 'Notes'], errors='ignore')

# Melt to long format
df_long = df_wide.melt(id_vars='Name', var_name='year', value_name='insolvency_rate')
df_long['year'] = df_long['year'].astype(int)

# Feature engineering
df = df_long.copy()
df['Name'] = df['Name'].astype('category')
df = df.sort_values(['Name', 'year'])

for lag in [1, 2, 3]:
    df[f'lag_{lag}'] = df.groupby('Name')['insolvency_rate'].shift(lag)

df['year_sin'] = np.sin(2 * np.pi * df['year'] / 12)
df['year_cos'] = np.cos(2 * np.pi * df['year'] / 12)

df = df.dropna()

# Train/test split
last_train_year = df['year'].max() - 1
train = df[df['year'] <= last_train_year]
features = ['year', 'year_sin', 'year_cos', 'lag_1', 'lag_2', 'lag_3', 'Name']
target = 'insolvency_rate'

# Pipeline
cat_features = ['Name']
num_features = [col for col in features if col not in cat_features]

preprocessor = ColumnTransformer([
    ('num', 'passthrough', num_features),
    ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features)
])

pipeline = Pipeline([
    ('preprocess', preprocessor),
    ('xgb', XGBRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=3,
        objective='reg:squarederror',
        random_state=42
    ))
])

pipeline.fit(train[features], train[target])

# Predict next year
latest_year = df['year'].max()
next_year = latest_year + 1
latest = df[df['year'] == latest_year].copy()

forecast = latest.copy()
forecast['year'] = next_year
forecast['lag_1'] = latest['insolvency_rate']
forecast['lag_2'] = latest['lag_1']
forecast['lag_3'] = latest['lag_2']
forecast['year_sin'] = np.sin(2 * np.pi * next_year / 12)
forecast['year_cos'] = np.cos(2 * np.pi * next_year / 12)

forecast['predicted_insolvency_rate'] = pipeline.predict(forecast[features])

result = forecast[['Name', 'predicted_insolvency_rate']].sort_values('predicted_insolvency_rate', ascending=False)

# --- Step 2: Load and fix GeoJSON CRS ---
gdf = gpd.read_file("C:/covidapp/flask-server/app/data/ukboundarylines.geojson")

if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs(epsg=4326)

fixed_geojson_path = "C:/covidapp/flask-server/app/data/ukboundarylines_wgs84.geojson"
gdf.to_file(fixed_geojson_path, driver='GeoJSON')

with open(fixed_geojson_path) as f:
    geojson_data = json.load(f)

# --- Step 3: Prepare for merge and merge ---
gdf['region'] = gdf['LAD21NM'].str.strip().str.lower()
result['region'] = result['Name'].str.strip().str.lower()

merged = gdf.merge(result[['region', 'predicted_insolvency_rate']], on='region', how='left')

# Update geojson_data with predicted values for each feature
region_to_score = dict(zip(merged['region'], merged['predicted_insolvency_rate'].fillna(0)))

for feature in geojson_data['features']:
    name = feature['properties']['LAD21NM'].strip().lower()
    feature['properties']['region'] = name
    feature['properties']['predicted_insolvency_rate'] = region_to_score.get(name, 0)

# --- Step 4: Create and save the map ---
center = [merged.geometry.centroid.y.mean(), merged.geometry.centroid.x.mean()]
m = folium.Map(location=center, zoom_start=6)

folium.Choropleth(
    geo_data=geojson_data,
    data=result,
    columns=['region', 'predicted_insolvency_rate'],
    key_on='feature.properties.region',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    nan_fill_color='white',
    legend_name='Predicted Insolvency Rate',
    bins=[0, 5, 10, 15, 20, 25, 30, 100],  # Adjust bins as needed
).add_to(m)

folium.GeoJson(
    geojson_data,
    name="regions",
    tooltip=folium.GeoJsonTooltip(fields=["region", "predicted_insolvency_rate"])
).add_to(m)

m.save("C:/covidapp/flask-server/app/static/insolvency_map.html")

print("Map saved at C:/covidapp/flask-server/app/static/insolvency_map.html")



#
