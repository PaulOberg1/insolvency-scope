from flask import Flask, jsonify, render_template, request, session, Response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from bs4 import BeautifulSoup
import requests, folium, logging
from flask_cors import CORS
from flask_jwt_extended import create_access_token, JWTManager
from sqlalchemy.exc import IntegrityError
import pandas as pd
import geopandas as gpd
import random, copy
from flask_mail import Mail, Message
from shapely.geometry import Point,shape,LineString

"""
replace map with external html file

add markers for start/end

figure out safe route algorithm

split into multiple files and add comments ~ 1 hour
"""
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:PASSWORD@127.0.0.1/login_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SECRET'
app.config['JWT_SECRET_KEY'] = 'SECRET'


jwt = JWTManager(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)


# Load GeoJSON data (boundary lines of regions)
geojson_path = 'ukboundarylines.geojson'
geojson_data = gpd.read_file(geojson_path)

# Load Excel dataset (covid deaths)
excel_path = 'finalcases.csv'
excel_data = pd.read_csv(excel_path)

# Create a copy of the original GeoJSON data before cleaning
original_geojson_data = geojson_data.copy()

# Remove rows with missing or invalid geometries before merging
valid_geojson_data = geojson_data.dropna(subset=['geometry'])
valid_geojson_data = valid_geojson_data[valid_geojson_data['geometry'].is_valid]

# Merge data based on region identifier
merged_data = pd.merge(valid_geojson_data, excel_data, how='left', left_on='LAD21NM', right_on='Area name')

# Create a merged GeoJSON dataset
merged_geojson_data = pd.merge(original_geojson_data, merged_data, how='left', left_on='LAD21NM', right_on='LAD21NM')

# Perform aggregation to get the sum of deaths for each region
aggregated_data = merged_geojson_data.groupby('LAD21NM').agg(
    total_deaths=('Deaths', 'sum'),
    specific_deaths=('Deaths', lambda x: list(x))
).reset_index()



def getFastestRoute(routes):
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
    
    # Reproject route_gdf to match the CRS of valid_geojson_data
    route_gdf = route_gdf.to_crs(valid_geojson_data.crs)
    
    # Perform spatial join to determine intersections
    joined_gdf = gpd.sjoin(route_gdf, valid_geojson_data, how='inner', op='intersects')
    
    # Check if the join produced results
    if joined_gdf.empty:
        raise ValueError("No intersecting polygons found for any routes.")
    
    # Ensure 'total_deaths' column is aggregated from `aggregated_data`
    # Merge the joined_gdf with aggregated_data to get the death counts
    joined_gdf = joined_gdf.merge(aggregated_data[['LAD21NM', 'total_deaths']], on='LAD21NM', how='left')
    
    # Aggregate total deaths for each route
    route_deaths = joined_gdf.groupby('route_id').apply(lambda x: x['total_deaths'].sum())
    
    # Find the route with the minimum risk (i.e., total deaths)
    fastest_route_id = route_deaths.idxmin()
    
    # Handle case where there might be no valid routes
    if pd.isna(fastest_route_id):
        raise ValueError("Unable to determine the fastest route with minimum risk.")
    
    fastest_route = next(route for route in routes if route['id'] == fastest_route_id)
    
    return fastest_route



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


app.logger.setLevel(logging.INFO)
logging.basicConfig(filename='app.log', level=logging.DEBUG)

def initialiseDatabase():
    with app.app_context():
        db.create_all()


@app.route("/highlight",methods=["POST"])
def highlight():
    global routeMap
    try:

        copyOfMap = copy.deepcopy(routeMap)
        data = request.json
        if data is None:
            return jsonify({"message":"data is none"})
        geometry = data["geometry"]
        locations = data["locations"]
        if geometry is None or locations is None:
            return jsonify({"message":"geometry or locations is none"})

        folium.Polyline(locations=locations,color="blue",weight=8).add_to(copyOfMap)
        map_html = folium.Figure().add_child(copyOfMap).render()
        return map_html
    except Exception as e:
        return jsonify({f"message":"error highlighting: {e}"}),500



@app.route("/clearHighlights")
def clearHighlights():
    global routeMap
    map_html = folium.Figure().add_child(routeMap).render()
    return map_html

@app.route('/')
def index():
    return "Hello, this is the root of the Flask application!"


@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.json
        username = data["username"]
        password = data["password"]
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        access_token = create_access_token(identity=username)
        app.logger.info("success with sign up info")
        return jsonify({"access_token": access_token}), 200
    except IntegrityError as e:
        # Handle case where a unique constraint (e.g., username) is violated
        app.logger.error(f"Integrity error in signup endpoint: {str(e)}")
        db.session.rollback()
        return jsonify({"message": "Username already exists"}), 400
    except Exception as e:
        # Log the exception for debugging purposes
        app.logger.error(f"Error in signup endpoint: {str(e)}")
        return jsonify({"message": "Signup failure"}), 500

@app.route("/login",methods=["POST"])
def login():
    try:
        data = request.json
        username,password = data["username"],data["password"]
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password,password):
            access_token = create_access_token(identity=username)
            return jsonify({"access_token":access_token}), 200
        else: 
            return jsonify({"message":"login failure"}), 401
    except Exception as e:
        return jsonify({"message":"failure logging in"})



def createMap(centre_lat,centre_long):
    global mapHTML, originalMap, routeMap
    m = folium.Map(location=[centre_lat, centre_long], zoom_start=13,min_lat=52.3587305,max_lat=55.0309801,
                       min_lon=-5.3973485,max_lon=6.0082506)


    
    # Add a TileLayer with JavaScript to handle zoom constraints
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="Map data © OpenStreetMap contributors",
        min_zoom=9,
        max_zoom=16
    ).add_to(m)

    # Add custom JavaScript for zoom constraints
    custom_script = """
    <script>
    var map = {{ this.get_name() }};
    map.on('zoomend', function() {
        if (map.getZoom() < 9) {
            map.setZoom(9);
        }
        if (map.getZoom() > 16) {
            map.setZoom(16);
        }
    });
    </script>
    """

    # Add the custom script to the map
    folium.Element(custom_script).add_to(m)
    
    
    
    folium.Choropleth(
        geo_data=geojson_data,
        data=aggregated_data,
        columns=['LAD21NM', 'total_deaths'],
        key_on='feature.properties.LAD21NM',
        fill_color='YlGnBu',
        fill_opacity=0.4,
        line_opacity=0.5,
        legend_name='Total COVID-19 Deaths'
    ).add_to(m)
    
    mapHTML = folium.Figure().add_child(m).render()
    originalMap = m
    routeMap = m

mapHTML = None
originalMap=None
routeMap = None




@app.route("/modifyMap", methods=["POST"])
def modifyMapHTML():
    app.logger.info("endpoint accessed")
    try:
        print(1)
        output = request.json
        sp = output["startPos"]
        ep = output["endPos"]
        api_url = f"https://router.project-osrm.org/route/v1/driving/{sp};{ep}?steps=true&geometries=geojson&annotations=true&alternatives=1"

        response = requests.get(api_url)
        data = response.json()

        instructions = []

        route = data["routes"][0]

        print(2)

        iMap = {
            "turn":"Take a ",
            "exit roundabout":"At the roundabout, take exit ",
            "roundabout":"At the roundabout, take exit ",
            "exit rotary":"At the circular intersection, take exit ",
            "rotary":"At the circular intersection, take exit ",
            "fork":"At the fork, take a ",
            "straight":"Continue straight along the road",
            "u-turn":"Make a U-Turn",
            "continue":"Continue straight along the road",
            "end of road": "At the end of this road, turn ",
            "new name": "Take a ",
            "depart": "Depart here",
            "arrive": "You have arrived at your destination",
            "off ramp": "Exit the ramp at a "
        }
        
        for step in route["legs"][0]["steps"]:
            
            if "maneuver" in step and "type" in step["maneuver"]:
                i = step["maneuver"]["type"]
                if i in iMap:
                    i = iMap[i]
                if "exit" in step["maneuver"]:
                    i+=str(step["maneuver"]["exit"])
                if "modifier" in step["maneuver"] and not ("roundabout" in i or "intersection" in i or "depart" in i or "arrive" in i):
                    i+=step["maneuver"]["modifier"]
                instructions.append(i)
        #route = getFastestRoute(data["routes"])
     
        def fastLineStyle(feature):
            return {
                'fillColor': 'red',  # Line color
                'color': 'red',      # Line border color
                'weight': 4           # Line thickness
            }
        def safeLineStyle(feature):
            return {
                'fillColor': 'blue',  # Line color
                'color': 'blue',      # Line border color
                'weight': 4           # Line thickness
            }
        def optimalLineStyle(feature):
            return {
                'fillColor': 'yellow',  # Line color
                'color': 'yellow',      # Line border color
                'weight': 4           # Line thickness
            }
            

        coordinates = route['geometry']['coordinates']
        totalCoords = []
        for i,startPoint in enumerate(coordinates[:-1]):
            
            endPoint = coordinates[i+1]

            startPoint = [str(coord) for coord in startPoint]
            endPoint = [str(coord) for coord in endPoint]

            startPoint = ",".join(startPoint)
            endPoint = ",".join(endPoint)

            api_url = f"https://router.project-osrm.org/route/v1/driving/{startPoint};{endPoint}?alternatives=1&steps=true&geometries=geojson"
        
            response = requests.get(api_url)
            data = response.json()
            newRoute = data["routes"][0]

            newCoords = newRoute['geometry']['coordinates']
            totalCoords += newCoords



        geojson_data = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": totalCoords
            },
            "properties": {}
        }

        folium.GeoJson(geojson_data,style_function=optimalLineStyle).add_to(routeMap)

        map_html = folium.Figure().add_child(routeMap).render()
        return jsonify({"mapHTML":map_html,"instructions":instructions})
            

    except Exception as e:
        return jsonify({"message":f"error: {e}"})


@app.route("/map", methods=["POST"])
def getMapHTML():
    try:
        global mapHTML, ogm
        data = request.json
        centre_lat,centre_long = data["latitude"],data["longitude"]
        if not mapHTML:
            createMap(centre_lat,centre_long)
        return mapHTML
    
    except Exception as e:
        app.logger.error(f"error with getMapHTML function: {e}")
        return None

if __name__=="__main__":
    initialiseDatabase()
    app.run(debug=True)