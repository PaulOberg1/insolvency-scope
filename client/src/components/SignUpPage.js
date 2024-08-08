import React, {useState} from "react";
import { useNavigate } from "react-router-dom";

const SignUpPage = () => {
    const [username,setUsername] = useState('');
    const [password,setPassword] = useState('');
    const [email,setEmail] = useState('');
    const [secondPassword, setSecondPassword] = useState('');

    const navigate = useNavigate();

    const handleSignUp = async () => {
        if (password!==secondPassword) {
            return false;
        }
        const response = await fetch("/signup",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({
                "username":username,
                "password":password,
            })
        });
        if (response.ok) {
            const result = await response.json();
            const token = result.access_token;
            localStorage.setItem("jwt",token);
            navigate("/map");
        }
        else {
            const result = await response.json();
            console.error("Error fetching sign up detail",result?.message);
        }
        
    }

    return (
        <div>
            <label>Username</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)}/>
            <br />
            <label>Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}/>
            <br />
            <label>Confirm your password</label>
            <input type="password" value={secondPassword} onChange={(e) => setSecondPassword(e.target.value)}/>
            <button onClick={handleSignUp}>Sign up</button>
        </div>
    )
}

export default SignUpPage;