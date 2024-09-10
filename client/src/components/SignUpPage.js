import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Authenticate.css";
import "../styles/HomePage.css";

const SignUpPage = () => {
    // State variables for form fields
    const [username, setUsername] = useState('');         // Stores the username input
    const [password, setPassword] = useState('');         // Stores the password input
    const [secondPassword, setSecondPassword] = useState(''); // Stores the confirmation password input

    // Hook to programmatically navigate between routes
    const navigate = useNavigate();

    // Function to handle the sign-up process
    const handleSignUp = async () => {
        // Check if the password and confirmation password match
        if (password !== secondPassword) {
            console.error("Passwords do not match.");
            return false;
        }

        // Send a POST request to the /signup endpoint with the username and password
        const response = await fetch("/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                "username": username,
                "password": password,
            })
        });

        // Handle the response from the server
        if (response.ok) {
            // Parse the JSON response and extract the access token
            const result = await response.json();
            const token = result.access_token;

            // Store the JWT token in local storage
            localStorage.setItem("jwt", token);

            // Navigate to the /map route upon successful sign-up
            navigate("/map");
        } else {
            // Handle and log any errors returned from the server
            const result = await response.json();
            console.error("Error fetching sign up detail", result?.message);
        }
    }

    return (
        <div>
            {/* Container for the background map */}
            <div id="MapBackgroundContainer">
                <iframe src="http://localhost:5000/static/homeMap.html" allowFullScreen></iframe>
            </div>

            {/* Sign-up form */}
            <div id="signup_page">
                <label>Username</label>
                <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <br />
                <label>Password</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <br />
                <label>Confirm your password</label>
                <input
                    type="password"
                    value={secondPassword}
                    onChange={(e) => setSecondPassword(e.target.value)}
                />
                <button onClick={handleSignUp}>Sign up</button>
            </div>
        </div>
    );
}

export default SignUpPage;
