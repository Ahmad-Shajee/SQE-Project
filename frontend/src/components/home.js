import React from "react";
import {Link} from "react-router-dom";
import "./../styles/home.css"; // Import the CSS file

const Home = () => {
  return (
    <div className="container">
      <h1>Welcome to Video Streaming App</h1>
      <div className="button-container">
        <Link to="/register">
          <button className="register-button">Register</button>
        </Link>
        <Link to="/login">
          <button className="login-button">Login</button>
        </Link>
      </div>
    </div>
  );
};

export default Home;
