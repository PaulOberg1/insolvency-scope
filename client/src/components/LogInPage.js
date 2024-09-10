import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Authenticate.css";
import "../styles/HomePage.css";

const LogInPage = () => {
    // State variables to manage username, password, and error messages
    const [username, setUsername] = useState("");  // Stores the username input
    const [password, setPassword] = useState("");  // Stores the password input
    const [error, setError] = useState(false);     // Manages error state (e.g., invalid login)

    // Hook for programmatic navigation
    const navigate = useNavigate();

    // Function to handle the login process
    const handleLogIn = async () => {
        // Send a POST request to the login endpoint with username and password
        const response = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                "username": username,
                "password": password
            })
        });

        // Check if the response is successful
        if (response.ok) {
            const result = await response.json();
            const token = result.access_token;
            // Store the JWT token in local storage
            localStorage.setItem("jwt", token);
            // Navigate to the map page upon successful login
            navigate("/map");
        } else {
            // Set error state if login fails
            setError(true);
        }
    };

    return (
        <div>
            {/* Container for background map */}
            <div id="MapBackgroundContainer">
                <iframe
                    src="http://localhost:5000/static/homeMap.html"
                    allowFullScreen
                    title="Home Map"
                ></iframe>
            </div>

            {/* Login form */}
            <div id="login_page">
                <label>Enter username</label>
                <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <br />
                <label>Enter password</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button onClick={handleLogIn}>Log in</button>
                {/* Display error message if login fails */}
                {error && <p>Incorrect login details, try again</p>}
            </div>
        </div>
    );
};

export default LogInPage;
