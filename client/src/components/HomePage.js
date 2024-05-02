import React from "react";
import { useNavigate } from "react-router-dom";


const HomePage = () => {
    const navigate = useNavigate();

    const navigateToSignUp = () => {
        navigate("/signup");
    }
    
    const navigateToLogIn = () => {
        navigate("/login");
    }
    return (
        <div id="home_page">
            <h1>Welcome to Co-Navigator!</h1>
            <button onClick={navigateToSignUp}>Haven't logged in before? Sign up here.</button>
            <button onClick={navigateToLogIn}>Already have an account? Log in here.</button>
        </div>
    )
}

export default HomePage;