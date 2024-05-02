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


#Display extra route info
#Click detector on map
#Email verification
#Set up risk calculator

#Split into different files
#Clean up/comment code
#Begin committing

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:PASSWORD@127.0.0.1/login_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '125'
app.config['JWT_SECRET_KEY'] = '125'

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = "587"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = "samueljones26745@gmail.com"
#app.config["MAIL_PASSWORD"] = "PASSWORD"
mail = Mail(app)

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)

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

@app.route("/sendEmail", methods=["POST"])
def sendEmail():
    try:
        data = request.json
        email = data["email"]
        code = random.randint(1000,9999)            
        msg = Message(subject="Account verification",sender="samueljones26745@gmail.com",recipients=[email],body=f"Your code is {code}")
        try:
            mail.send(msg)
            return jsonify({"message":"email sent","code":str(code)}),200
        except Exception as e:
            app.logger.error(f"error sending email: {e}")
            return jsonify({"message":"failure to send email"}),500
    except Exception as e:
        app.logger.error(f"error with email function: {e}")
        return jsonify({"message":"failure to send email"}),500

@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.json
        username = data["username"]
        password = data["password"]
        email = data["email"]
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()
        access_token = create_access_token(identity=username, additional_claims={"email": email})
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
            access_token = create_access_token(identity=username, additional_claims={"email":user.email})
            return jsonify({"access_token":access_token}), 200
        else: 
            return jsonify({"message":"login failure"}), 401
    except Exception as e:
        return jsonify({"message":"failure logging in"})



def createMap(centre_lat,centre_long):
    global mapHTML, originalMap, routeMap
    m = folium.Map(location=[centre_lat, centre_long], zoom_start=13,min_lat=52.3587305,max_lat=55.0309801,
                       min_lon=-5.3973485,max_lon=6.0082506)
    
    
    
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

mapHTML = None
originalMap=None
routeMap = None


@app.route("/modifyMap", methods=["POST"])
def modifyMapHTML():
    try:
        global mapHTML, originalMap, routeMap
        routeMap = copy.deepcopy(originalMap)
        output = request.json
        if not mapHTML:
            createMap(output["centreLat"],output["centreLong"])
        
        newRouteData=output["data"]
        
        


        startLat,startLong = map(float,output["startPos"].split(","))
        folium.Marker(location=[startLat,startLong],popup="Start").add_to(routeMap)
        endLat,endLong = map(float, output["endPos"].split(","))
        folium.Marker(location=[endLat,endLong],popup="End").add_to(routeMap)

        newRouteData = [[float(str(a)[:-1]),float(str(b)[:-1])] for a,b in newRouteData]
        folium.PolyLine(locations=newRouteData,color="red",weight=6).add_to(routeMap)

        map_html = folium.Figure().add_child(routeMap).render()



        return map_html
    except Exception as e:
        app.logger.error(f"error with modifyMapHTML function: {e}")
        return jsonify({"message":f"error: {e}"}),500


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