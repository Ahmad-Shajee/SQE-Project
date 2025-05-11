import React, { useState } from "react";

const Account = () => {
  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [message, setMessage] = useState("");
  const userId = localStorage.getItem("userId");

  // Function to update the username
  const handleUsernameChange = async () => {
    if (newUsername) {
      try {
        const response = await fetch(
          "http://localhost:5003/update-username",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              username: newUsername,
              // Include the user ID if needed
              user_id: userId, // Example user ID, replace with actual user ID
            }),
          },
        );

        const data = await response.json();

        if (response.ok) {
          setMessage(`Username updated to: ${newUsername}`);
          localStorage.setItem("username", `${newUsername}`); // where userId is the value you want to store
        } else {
          setMessage(data.message || "Error updating username.");
        }
      } catch (error) {
        console.error("Error:", error);
        setMessage("Error updating username.");
      }
    } else {
      setMessage("Please enter a new username.");
    }
  };

  // Function to update the password
  const handlePasswordChange = async () => {
    if (newPassword) {
      try {
        const response = await fetch(
          "http://localhost:5003/update-password",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              current_password: currentPassword,
              user_id: userId, // Example user ID, replace with actual user ID
              new_password: newPassword,
            }),
          },
        );

        const data = await response.json();

        if (response.ok) {
          setMessage("Password updated successfully!");
        } else {
          setMessage(data.message || "Error updating password.");
        }
      } catch (error) {
        console.error("Error:", error);
        setMessage("Error updating password.");
      }
    } else {
      setMessage("Please enter a new password.");
    }
  };

  return (
    <div>
      <h1>Manage Account</h1>
      <div className="account-section">
        <div className="input-group">
          <label>Change Username</label>
          <input
            type="text"
            placeholder="Enter new username"
            value={newUsername}
            onChange={(e) => setNewUsername(e.target.value)}
          />
          <button onClick={handleUsernameChange}>Update Username</button>
        </div>

        <div className="input-group">
          <label>Change Password</label>
           <input
            type="password"
            placeholder="Enter current password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
        />
          <input
            type="password"
            placeholder="Enter new password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
          <button onClick={handlePasswordChange}>Update Password</button>
        </div>

        {message && <p className="message">{message}</p>}
      </div>
    </div>
  );
};

export default Account;
