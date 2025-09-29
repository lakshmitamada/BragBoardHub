import { useEffect, useState } from "react";
import Navbar from "../../components/Navbar";
import "../../styles/profile.scss"

export default function Profile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const accessToken = localStorage.getItem("accessToken");

  useEffect(() => {
    const fetchUser = async () => {
      if (!accessToken) {
        setError("Access token missing. Please login.");
        setLoading(false);
        return;
      }

      try {
        const res = await fetch("http://127.0.0.1:8000/auth/me", {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });

        if (!res.ok) {
          throw new Error(`Error: ${res.status} ${res.statusText}`);
        }

        const data = await res.json();
        setUser(data);
      } catch (err) {
        console.error(err);
        setError("Failed to fetch user profile.");
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [accessToken]);

  return (
    <>
      <Navbar />
      <div className="profile-container">
        <h1>Profile</h1>

        {loading && <p>Loading...</p>}
        {error && <p style={{ color: "red" }}>{error}</p>}

        {user && (
          <div className="profile-details">
            <p>
              <strong>Name:</strong> {user.name}
            </p>
            <p>
              <strong>Username:</strong> {user.username}
            </p>
            <p>
              <strong>Email:</strong> {user.email}
            </p>
            <p>
              <strong>Role:</strong> {user.role}
            </p>
          </div>
        )}
      </div>
    </>
  );
}
