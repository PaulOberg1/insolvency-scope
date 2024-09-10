import React, { useState } from "react";
import MapComponent from "./MapComponent";
import PlanningComponent from "./PlanningComponent";
import "../styles/MapPage.css";

const MapPage = () => {
    // Log to indicate that the MapPage component is being loaded
    console.log("map page loading");

    // State variables to manage positions, loading state, and map source
    const [startPos, setStartPos] = useState("52.3793,1.5615"); // Default start position
    const [endPos, setEndPos] = useState("51.5759,0.4212");     // Default end position
    const [loading, setLoading] = useState(true);                // Indicates if the map is loading
    const [latitude, setLatitude] = useState(null);              // Latitude coordinate
    const [longitude, setLongitude] = useState(null);            // Longitude coordinate
    const [mapSrc, setMapSrc] = useState("http://localhost:5000/static/map.html"); // Initial map source

    // Retrieve JWT token from local storage for potential authentication
    const token = localStorage.getItem("jwt");

    return (
        <div id="MainPage">
            {/* MapComponent: Displays the map */}
            <div id="MapComponent">
                <MapComponent 
                    mapSrc={mapSrc}          // Source URL for the map
                    setMapSrc={setMapSrc}    // Function to update the map source
                    startPos={startPos}      // Start position for the route
                    setStartPos={setStartPos} // Function to update the start position
                    setEndPos={setEndPos}    // Function to update the end position
                    loading={loading}        // Loading state for the map
                    setLoading={setLoading}  // Function to update the loading state
                    latitude={latitude}      // Latitude coordinate
                    setLatitude={setLatitude} // Function to update the latitude
                    longitude={longitude}    // Longitude coordinate
                    setLongitude={setLongitude} // Function to update the longitude
                />
            </div>

            {/* PlanningComponent: Allows user to plan a route and interact with the map */}
            <div id="RouteBar">
                <PlanningComponent
                    mapSrc={mapSrc}          // Source URL for the map
                    setMapSrc={setMapSrc}    // Function to update the map source
                    startPos={startPos}      // Start position for the route
                    setStartPos={setStartPos} // Function to update the start position
                    endPos={endPos}          // End position for the route
                    setEndPos={setEndPos}    // Function to update the end position
                    latitude={latitude}      // Latitude coordinate
                    setLatitude={setLatitude} // Function to update the latitude
                    longitude={longitude}    // Longitude coordinate
                    setLongitude={setLongitude} // Function to update the longitude
                />
            </div>
        </div>
    );
}

export default MapPage;
