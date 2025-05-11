// src/App.js
import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "./components/home";
import Register from "./components/register";
import Login from "./components/login";
import Videos from "./components/videos";
import Photos from "./components/photos";
import Account from "./components/account";
import Dashboard from "./components/dashboard";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/videos" element={<Videos />}/>
        <Route path="/photos" element={<Photos />}/>
        <Route path="/account" element={<Account />}/>
      </Routes>
    </Router>
  );
};

export default App;
