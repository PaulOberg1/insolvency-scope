import HomePage from "./components/HomePage";
import MapPage from "./components/MapPage";
import LogInPage from "./components/LogInPage";
import SignUpPage from "./components/SignUpPage";
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import DropDownComponent from "./components/DropDownComponent";
import "./styles/Menu.css";

const App = () => {
  
  // Toggles the visibility of the dropdown menu
  const renderDropDown = (e) => {
    const dropdown = document.getElementById("AccountDropDown");
    dropdown.classList.toggle("active");
  };

  return (
    <Router>
      <div>
          {/* Top bar with title and dropdown menu */}
          <div id="top-bar">
            <h1>CO-Navigator</h1>
            <div id="AccountDropDown">
              <button id="hamburger-icon" onClick={renderDropDown}>
                &#9776; {/* Hamburger icon for the dropdown menu */}
              </button>
              <DropDownComponent
                username={"a"} // Placeholder username, could be dynamically set
              />
            </div>
          </div>
          
          {/* Define application routes */}
          <Routes>
            <Route path="/home" element={<HomePage />} />
            <Route path="/login" element={<LogInPage />} />
            <Route path="/signup" element={<SignUpPage />} />
            <Route path="/map" element={<MapPage />} />
            {/* Redirect root URL to /home */}
            <Route path="/" element={
              <>
                <Navigate to="/home" />
              </>
            }/>
          </Routes>
      </div>
    </Router>
  );
}

export default App;
