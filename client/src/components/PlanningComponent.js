import { useState } from "react";
import "../styles/PlanningComponent.css";

const PlanningComponent = ({ mapSrc, setMapSrc, startPos, setStartPos, endPos, setEndPos, latitude, setLatitude, longitude, setLongitude }) => {

    // State variable to hold route instructions
    const [instructions, setInstructions] = useState(null);

    // Function to revert the map to the initial view and clear instructions
    const revertMap = () => {
        setMapSrc("http://localhost:5000/static/map.html");
        setInstructions(null);
    }

    // Function to fetch and display route instructions
    const getInstructions = async () => {
        // Fetch instructions from the server
        const response2 = await fetch("/getInstructions");
        if (response2.ok) {
            const data = await response2.json();
            const instructions = data.instructions;
            setInstructions(instructions); // Set the fetched instructions to state
            setMapSrc("http://localhost:5000/static/routeMap.html"); // Update map to show route
        }
        
        return 0;
    }

    // Function to handle highlighting of instructions
    async function highlight(event) {
        const i = event.currentTarget.getAttribute("data-key");
        // Send a POST request to highlight the specific instruction
        const response = await fetch("/highlight", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ "index": i })
        });
        // Additional logic to handle response could be added here
    }

    return (
        <div>
            {instructions && // Check if instructions exist to display them
            <div id="instructionBox">
                <div id="instructions">
                    <h1>Instructions</h1>
                    {instructions.map((x, i) => {
                        return (
                            // Render each instruction with an onClick handler for highlighting
                            <div key={i} data-key={i} onClick={highlight}>
                                <li>{x}</li>
                            </div>
                        );
                    })}
                </div>
                <button onClick={revertMap}>Plan new route?</button>
            </div>
            }
            
            {!instructions && 
            <button onClick={getInstructions}>Get directions</button>
            }
        </div>
    );
};

export default PlanningComponent;
