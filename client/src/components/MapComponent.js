import React, { useEffect } from "react";
import "../styles/MapComponent.css";

// Helper function to get the user's current location
const getLocation = async () => {
    return new Promise((resolve, reject) => {
        // Check if geolocation is available in the browser
        if ("geolocation" in navigator) {
            // Request the current position
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    // Resolve the promise with latitude and longitude
                    resolve({
                        "latitude": pos.coords.latitude,
                        "longitude": pos.coords.longitude
                    });
                },
                (error) => {
                    // Reject the promise with an error
                    reject(error);
                }
            );
        } else {
            // Reject if geolocation is not supported
            reject(new Error("Geolocation is not supported by this browser"));
        }
    });
};

const MapComponent = ({
    mapSrc, setMapSrc, startPos, setStartPos, setEndPos, loading, setLoading, latitude, setLatitude, longitude, setLongitude
}) => {

    // Handler to set start and end positions based on map clicks
    const getCoords = (e) => {
        if (startPos) {
            // Set the end position if start position is already set
            setEndPos(e.latlng.lat + "," + e.latlng.lng);
        } else {
            // Set the start position if not set
            setStartPos(e.latlng.lat + "," + e.latlng.lng);
        }
    };

    // Effect to update loading state when latitude and longitude are set
    useEffect(() => {
        if (latitude && longitude && loading) {
            setLoading(false); // Set loading to false when coordinates are available
        }
    }, [latitude, longitude, loading]);

    // Effect to fetch and set the current location on component mount
    useEffect(() => {
        const fetchLocation = async () => {
            try {
                const response = await getLocation(); // Get the current location
                setLatitude(response.latitude); // Set latitude
                setLongitude(response.longitude); // Set longitude
            } catch (error) {
                console.error("Error fetching location:", error);
            }
        };
        fetchLocation();
    }, []); // Empty dependency array means this effect runs once on mount

    return (
        <div>
            {!loading && ( // Render the map only when loading is complete
                <div>
                    <iframe
                        id="Map"
                        title="Map of Local Area"
                        src={mapSrc} // Source URL for the map
                        // Additional attributes for iframe, e.g., for interactivity, can be added here
                    ></iframe>
                </div>
            )}
        </div>
    );
};

export default MapComponent;
