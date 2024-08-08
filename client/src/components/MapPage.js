import React, {useState} from "react";
import MapComponent from "./MapComponent";
import PlanningComponent from "./PlanningComponent";
import { jwtDecode } from 'jwt-decode';
import { decode } from "polyline";

//Use start/end pos to modify map
function decodeJwt(token) {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map((c) => {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
  
    return JSON.parse(jsonPayload);
}
const MapPage = () => {
    const [startPos,setStartPos] = useState("52.3793,1.5615");
    const [endPos,setEndPos] = useState("51.5759,0.4212");
    const [mapHTML,setMapHTML] = useState("");
    const [loading,setLoading] = useState(true);
    const [isPlanning,setIsPlanning] = useState(false);
    const [latitude,setLatitude] = useState(null);
    const [longitude,setLongitude] = useState(null);


    const token = localStorage.getItem("jwt");
    const username = jwtDecode(token).identity;

    return (
        <div>
            <h1>Hi, {username}!</h1>
            <MapComponent 
            mapHTML={mapHTML} 
            setMapHTML={setMapHTML} 
            startPos={startPos} 
            setStartPos={setStartPos}
            setEndPos={setEndPos}
            loading={loading}
            setLoading={setLoading}
            latitude={latitude}
            setLatitude={setLatitude}
            longitude={longitude}
            setLongitude={setLongitude}
            />
            {!loading && <button onClick={() => setIsPlanning(true)}>Plan a journey?</button>}
            {isPlanning && 
            <PlanningComponent
            setMapHTML={setMapHTML}
            startPos={startPos}
            setStartPos={setStartPos}
            endPos={endPos}
            setEndPos={setEndPos}
            latitude={latitude}
            setLatitude={setLatitude}
            longitude={longitude}
            setLongitude={setLongitude}
            />}

        </div>
    )

}

export default MapPage;