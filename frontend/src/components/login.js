import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate from react-router-dom
import "./../styles/login.css"; // Import the login CSS

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate(); // Initialize useNavigate hook for navigation

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        "http://localhost:5001/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email, password }),
        },
      );

      const data = await response.json();
      console.log("data", data);

      if (response.ok) {
        console.log("Login successful", data);
        alert("Login successful!");

        const { access_token, username, userId } = data; // Extract token and username
        console.log("Username:", username);
        console.log("User_ID:", userId);

        // Store in localStorage
        localStorage.setItem("username", username);
        localStorage.setItem("token", access_token);
        localStorage.setItem("userId", userId);

        // Redirect to dashboard
        navigate("/dashboard");
      } else {
        setError(data.message || "Invalid credentials. Please try again.");
      }
    } catch (err) {
      setError("An error occurred. Please try again later.");
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2>Login</h2>
      {error && <div className="error-message">{error}</div>}
      {loading && <div className="loading-message">Loading...</div>}
      <form onSubmit={handleLogin}>
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
        <button type="submit" className="submit-btn" disabled={loading}>
          Login
        </button>
      </form>
    </div>
  );
};

export default Login;
