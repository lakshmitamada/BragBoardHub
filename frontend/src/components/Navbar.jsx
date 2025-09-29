import { Link, useNavigate, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";
import "../styles/Navbar.scss";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [role, setRole] = useState("");

  // Check login status and role whenever the location changes
  useEffect(() => {
    const token = localStorage.getItem("accessToken"); 
    const userRole = localStorage.getItem("role");
    setIsLoggedIn(!!token);
    setRole(userRole || "");
  }, [location]);

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("role");

    setIsLoggedIn(false);
    setRole("");

    alert("Logged out successfully!");
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <div className="nav-logo">Bragboard</div>
      <ul className="nav-links">
        {/* Always show Home unless on login/register page */}
        {location.pathname !== "/login" && location.pathname !== "/register" && (
          <li><Link to="/home">Home</Link></li>
        )}

        {/* Admin-only links */}
        {role === "admin" && (
          <>
            <li><Link to="/dashboard">Dashboard</Link></li>
            <li><Link to="/AdminDashboard">Security Keys</Link></li>
            <li><Link to="/employee-list">Employee List</Link></li>
          </>
        )}

        {/* Logged in links (common for both roles) */}
        {isLoggedIn ? (
          <>
            <li><Link to="/profile">Profile</Link></li>
            <li>
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            </li>
          </>
        ) : (
          // Not logged in links
          <>
            <li><Link to="/login">Login</Link></li>
            <li><Link to="/register">Register</Link></li>
          </>
        )}
      </ul>
    </nav>
  );
}
