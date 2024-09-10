import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/HomePage.css";

const HomePage = () => {
    // Hook for programmatic navigation
    const navigate = useNavigate();

    // Function to navigate to the Sign-Up page
    const navigateToSignUp = () => {
        navigate("/signup");
    };

    // Function to navigate to the Log-In page
    const navigateToLogIn = () => {
        navigate("/login");
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

            {/* Main content for the home page */}
            <div id="home_page">
                <h1>Welcome to Co-Navigator!</h1>
                {/* Button to navigate to the Sign-Up page */}
                <button onClick={navigateToSignUp}>
                    Haven't logged in before? Sign up here.
                </button>
                {/* Button to navigate to the Log-In page */}
                <button onClick={navigateToLogIn}>
                    Already have an account? Log in here.
                </button>
            </div>
        </div>
    );
};

export default HomePage;
