import React, {useState, useEffect} from "react";

const getLocation = async() => {
    return new Promise((resolve,reject) => {
        if ("geolocation" in navigator){
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    resolve({
                        "latitude":pos.coords.latitude,
                        "longitude":pos.coords.longitude
                    });
                },
                (error) => {
                    reject(error)
                }
            )
        }
        else {
            reject(new Error("Geolocation is not supported by this browser"));
        }  
    });
}

const MapComponent = ({mapHTML,setMapHTML,startPos,setStartPos,setEndPos,loading,setLoading,latitude,setLatitude,longitude,setLongitude}) => {

    const getCoords = (e) => {
        console.log("click detected at " +e.latlng.lat + e.atlng.long)
        if (startPos) {
            setEndPos(e.latlng.lat+","+e.latlng.long);
        }
        else {
            setStartPos(e.latlng.lat+","+e.latlng.long);
        }
    };

    const fetchMapHTML = async () => {
        try {
            const response = await fetch("/map",{
                method:["POST"],
                headers:{"Content-Type":"application/json"},
                body:JSON.stringify({"latitude":latitude,"longitude":longitude})
            });
            if (response.ok) {
                console.log("received map html");
                const result = await response.text();
                setMapHTML(result);
                setLoading(false);
                if (result) {
                    console.log("valid conversion of map to text")
                    
                    if (mapHTML) {
                        console.log("map html succesfully set");
                    }
                    
                }
            }
            else {
                console.log("Error sending/receiving lat/long data");
            }
        }
        catch (error) {
            console.log("Error fetching map data",error);
        }
    }

    useEffect(() => {
        console.log("lat/long change identified");
        if (latitude && longitude) {
            console.log("lat/long valid, now getting map html")
            fetchMapHTML();
        }
    }, [latitude,longitude])

    useEffect(() => {
        const fetchLocation = async() => {
            console.log("fetching loc at start of program")
            try {
                const response = await getLocation();
                setLatitude(response.latitude);
                setLongitude(response.longitude);
            }
            catch (error) {
                console.error("Error fetching location",error?.message);
            }
        };
        fetchLocation();
    },[]);

    return (
        <div>
            {loading && <p>Loading...</p>}
            <div style={{position:"relative",width:"700px",height:"700px"}}>
                <iframe
                    title="Map of Local Area"
                    srcDoc={mapHTML}
                    style={{ width: "700px", height: "700px", border: "none" }}
                    sandbox="allow-scripts"
                ></iframe>
                
            </div>
        </div>
    )
};

export default MapComponent;