import React, {useState, useEffect} from "react";
import { useNavigate } from "react-router-dom";

const LogInPage = () => {
    const [username,setUsername] = useState("");
    const [password,setPassword] = useState("");
    const [error,setError] = useState(false);
    const navigate = useNavigate();

    const handleLogIn = async () => {
        const response = await fetch("/login",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({
                "username":username,
                "password":password
            })
        });
        if (response.ok) {
            const result = await response.json();
            const token = result.access_token;
            localStorage.setItem("jwt",token);
            console.log("success with login call");
            navigate("/map");
        }
        else {
            console.error("couldn't do response");
            setError(true);
        }
    }

    return (
        <div>
            <label>Enter username</label>
            <input type="text" value={username} onChange={(e) => {setUsername(e.target.value)}}/>
            <br />
            <label>Enter password</label>
            <input type="password" value={password} onChange={(e) => {setPassword(e.target.value)}}/>
            <button onClick={handleLogIn}>Log in</button>
            {error && <p>Incorrect login details, try again</p>}
        </div>
    )
}

export default LogInPage;