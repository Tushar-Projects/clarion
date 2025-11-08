import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import CheckPost from './pages/CheckPost';

export default function AppRoutes() {
  return (
   
      <Routes>
        <Route path="/" element={<Login />}/>
        <Route path="/register" element={<Register />}/>
        <Route path="/" element={<Dashboard />}/>
        <Route path="/check" element={<CheckPost />}/>
      </Routes>
    
  );
}
