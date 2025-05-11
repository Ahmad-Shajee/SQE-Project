import React, { useState } from "react";
import "./../styles/register.css"; // Import the register CSS
import { useNavigate } from "react-router-dom";

const Register = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(""); // Reset error message on new attempt

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(
        "http://localhost:5002/register",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, email, password }),
        },
      );

      const data = await response.json();

      if (response.ok) {
        console.log("Registration successful", data);
        const userId = data.userId;
        console.log("userId", userId);
        alert("Registration successful!");
        localStorage.setItem("username", `${username}`); // where userId is the value you want to store
        localStorage.setItem("userId", `${userId}`);
        navigate("/dashboard");
        // Redirect to login or other page here
      } else {
        setError(data.message || "Registration failed. Please try again.");
        console.log("Registration failed", data);
      }
    } catch (err) {
      setError("An error occurred. Please try again later.");
      console.log("Registration error", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2>Register</h2>
      {error && <div className="error-message">{error}</div>}
      {loading && <div className="loading-message">Loading...</div>}
      <form onSubmit={handleRegister}>
        <input
          type="text"
          placeholder="Enter your username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Enter your password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Confirm your password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />
        <button type="submit" className="submit-btn" disabled={loading}>
          Register
        </button>
      </form>
    </div>
  );
};

export default Register;
