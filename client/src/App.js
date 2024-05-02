import HomePage from "./components/HomePage";
import MapPage from "./components/MapPage";
import LogInPage from "./components/LogInPage";
import SignUpPage from "./components/SignUpPage";
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import EmailVerifyPage from "./components/EmailVerifiyPage";


const App = () => {
  return (
    <Router>
      <div>
          <h1>CO-Navigator</h1>
          <Routes>
            <Route path="/home" element={<HomePage />}/>
            <Route path="/login" element={<LogInPage />}/>
            <Route path="/signup" element={<SignUpPage />}/>
            <Route path="/map" element={<MapPage />}/>
            <Route path="/email" element={<EmailVerifyPage />}/>
            <Route path="/" element={
              <>
                <Navigate to="/home"/>
              </>
            }/>
          </Routes>
      </div>
    </Router>
  );
}

export default App;