import React, {useState, useEffect} from "react";
import { useNavigate } from "react-router-dom";

function decodeJwt(token) {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map((c) => {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
  
    return JSON.parse(jsonPayload);
}


const EmailVerifyPage = () => {
    const [code,setCode] = useState("");
    const [inputCode,setInputCode] = useState("");
    const [wrongCode,setWrongCode] = useState(false);

    const navigate = useNavigate();

    useEffect(() => {
        const sendEmail = async () => {
            const token = decodeJwt(localStorage.getItem("jwt"));
            const email = token.email;
            const response = await fetch("/sendEmail",{
                method:"POST",
                headers:{"Content-Type":"application/json"},
                body:JSON.stringify({
                    "email":email
                })
            });
            if (response.ok) {
                const result = await response.json();
                setCode(result?.code);
            }
            else {
                const result = await response.json();
                console.log("Error sending email", result?.messsage);
            }
        };
        sendEmail();
    },[]);

    useEffect(() => {
        if (code && code===inputCode) {
            navigate("/map");
        }
        else {
            setWrongCode(false);
        }
    },[inputCode]);

    return (
        <div>
            <label>Enter 4 digit verification code sent to your email</label>
            <input type="text" value={inputCode} onChange={(e) => setInputCode(e.target.value)}/>
            {wrongCode && <p>Wrong code. Try again.</p>}
        </div>
    )
}

export default EmailVerifyPage;