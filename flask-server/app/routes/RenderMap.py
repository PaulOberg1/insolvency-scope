from flask import Flask, request, jsonify, Blueprint
import requests,folium
import json
from app.utils.GenerateMap import generateMap
from app.utils.OptimiseRoute import getSafestRoute

# Define new Blueprint "RenderMapBP" to register in __init__.py
bp = Blueprint("RenderMapBP",__name__)

@bp.route("/renderRouteMap", methods=["POST"])
def renderRouteMap():
    """
    Route to generate a map to display route data and store corresponding instructions.
    Expected JSON input format:
    {
        "start": list,
        "end": list
    }

    Returns:
        JSON response indicating success or failure.
    """
    try:
        #Access redis object for managing server-side storage
        from .. import r

        #Extract data from incoming JSON request
        output = request.json

        #Reformat start and end fields of JSON payload for compatability with API calls
        sp = ",".join([str(x) for x in output["start"]][::-1])
        ep = ",".join([str(x) for x in output["end"]][::-1])

        #Make request to OSRM API to retrieve route data between start and end points
        api_url = f"https://router.project-osrm.org/route/v1/driving/{sp};{ep}?steps=true&geometries=geojson&annotations=true&alternatives=1"
        response = requests.get(api_url)
        data = response.json()

        #Map instruction types to readable alternatives
        iMap = {
            "turn":"Take a ",
            "exit roundabout":"At the roundabout, take exit ",
            "roundabout":"At the roundabout, take exit ",
            "exit rotary":"At the circular intersection, take exit ",
            "rotary":"At the circular intersection, take exit ",
            "fork":"At the fork, take a ",
            "straight":"Continue straight along the road ",
            "u-turn":"Make a U-Turn",
            "continue":"Continue straight along the road",
            "end of road": "At the end of this road, turn ",
            "new name": "Take a ",
            "off ramp": "Exit the ramp at a ",
            "merge": "Merge into the adjacent road at a "
        }

        #Determine route with minimal COVID exposure
        route = getSafestRoute(data["routes"])

        #Access coordinates of route
        coordinates = route['geometry']['coordinates']

        #Initialise lists to store route instructions and coordinates
        instructions = []
        totalCoords = []

        #Retrieve route data between each adjacent pair of coordinates for increased precision when rendering routes
        for i,startPoint in enumerate(coordinates[:-1]):
            
            
            startPoint = [str(coord) for coord in startPoint]
            endPoint = coordinates[i+1]
            endPoint = [str(coord) for coord in endPoint]

            #Reformat start and end point for compatibility with API request
            startPoint = ",".join(startPoint)
            endPoint = ",".join(endPoint)

            #Make request to OSRM API to retrieve route data between adjacent coordinate pairs
            api_url = f"https://router.project-osrm.org/route/v1/driving/{startPoint};{endPoint}?alternatives=1&steps=true&geometries=geojson"
            response = requests.get(api_url)
            data = response.json()
            newRoute = data["routes"][0]

            #Access coordinates field of the route JSON body and store in totalCoords list
            newCoords = newRoute['geometry']['coordinates']
            totalCoords += newCoords

            #Access list of instructions for given route
            for step in newRoute["legs"][0]["steps"]:

                #Verify correct JSON body structure
                if "maneuver" in step and "type" in step["maneuver"]:

                    #Access instruction type and translate into readable alternative if possible
                    i = step["maneuver"]["type"]
                    if i in iMap:
                        i = iMap[i]

                    #Add exit number if appropriate
                    if "exit" in step["maneuver"]:
                        i+=str(step["maneuver"]["exit"])

                    #Add modifier (e.g., left, right) if appropriate
                    if "modifier" in step["maneuver"] and not ("roundabout" in i or "intersection" in i or "depart" in i or "arrive" in i):
                        i+=step["maneuver"]["modifier"]

                    #Discard instructions indicating arrival or departure
                    if "arrive" not in i and "depart" not in i:
                        instructions.append(i)

        #Store instructions in server-side storage with redis object
        instructionData = json.dumps(instructions)
        r.set("instructions",instructionData)

        #Generate a new map centered around the starting coordinates with the given route data coordinates
        startLat,startLong = output["start"]
        generateMap(startLat,startLong,totalCoords)

        #Return JSON object indicating success with status code 200
        return jsonify({"message":"success"}),200
            
    except Exception as e:
        print(e)
        #Return JSON object indicating failure with status code 500
        return jsonify({"message":f"error: {e}"}),500
