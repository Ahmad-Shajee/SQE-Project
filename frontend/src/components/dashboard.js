import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate from react-router-dom
import "./../styles/dashboard.css";

const Dashboard = () => {
  const navigate = useNavigate(); // Initialize navigate function

  // State to store the remaining storage and bandwidth
  const [remainingStorage, setRemainingStorage] = useState(null);
  const [remainingBandwidth, setRemainingBandwidth] = useState(null);
  const userId = localStorage.getItem("userId");

  // Fetch remaining storage and bandwidth from the backend API
  useEffect(() => {
    const fetchUsageData = async () => {
      try {
        console.log("Usage of user with userId", userId);
        const response = await fetch(
          `http://localhost:5004/api/usage/${userId}`,
        ); // Backend API URL

        if (response.ok) {
          const data = await response.json();
          setRemainingStorage(data.remainingStorage); // Assuming the API response contains these fields
          setRemainingBandwidth(data.remainingBandwidth);
        } else {
          console.error("Error fetching usage data");
        }
      } catch (error) {
        console.error("Error fetching usage data:", error);
      }
    };

    fetchUsageData();
  }, []); // Empty dependency array to run only once on component mount

  // Handle button clicks to navigate
  const handleManageVideos = () => {
    navigate("/videos"); // Navigate to Videos page
  };

  const handleManagePhotos = () => {
    navigate("/photos"); // Navigate to Photos page
  };

  const handleManageAccount = () => {
    navigate("/account"); // Navigate to Account Management page
  };

  const username = localStorage.getItem("username");

  return (
    <div className="dashboard-container">
      {/* Display the username in the greeting */}
      <button className="navigate-button" onClick={() => navigate("/")}>Back</button>
      <h1>Welcome {username || "User"}</h1>{" "}
      {/* Fallback to "User" if no username is found */}
      {/* Display remaining storage and bandwidth */}
      <div className="usage-info">
        <p>
          <strong>Remaining Daily Bandwidth:</strong>{" "}
          {remainingBandwidth ? remainingBandwidth : "Loading..."}
        </p>
        <p>
          <strong>Remaining Storage:</strong>{" "}
          {remainingStorage ? remainingStorage : "Loading..."}
        </p>
      </div>
      <div className="main-buttons">
        <button onClick={handleManageVideos}>Manage Videos</button>
        <button onClick={handleManagePhotos}>Manage Photos</button>
        <button onClick={handleManageAccount}>Manage Account</button>
      </div>
    </div>
  );
};

export default Dashboard;
