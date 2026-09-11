import './App.css'

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

import HomePage from './pages/HomePage';
import CreatePage from './pages/CreatePage';
import DetailPage from './pages/DetailPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        
        <Route path="/" element={<Navigate to="/home" replace />} />

        <Route path="/home" element={<HomePage />}/>
        <Route path="/create" element={<CreatePage />}/>
        <Route path="/detail/:id" element={<DetailPage />}/>

      </Routes>    
    </BrowserRouter>
  )
}

export default App


//import { useState } from 'react'





