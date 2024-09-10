import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/DropDownComponent.css";

// Functional component to display a dropdown with user information and a logout button
const DropDownComponent = ({ username }) => {
    // Hook to programmatically navigate to different routes
    const navigate = useNavigate();

    // Function to handle user logout
    const handleLogOut = () => {
        
        // Send a POST request to the /logout endpoint to log the user out
        fetch("/logout", {
            method: 'POST', // Specify the HTTP method
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json()) // Parse the JSON response
        .then(data => {
            // Navigate to the home page after successful logout
            navigate("/home");
        })
        .catch(error => {
            // Handle any errors that occurred during the fetch
            console.error("Error during logout:", error);
        });
    }

    return (
        <div id="DropDownContent">
            {/* Display the username */}
            <p>{username}</p>
            {/* Button to trigger logout functionality */}
            <button onClick={handleLogOut}>Log Out</button>
        </div>
    );
}

export default DropDownComponent;
