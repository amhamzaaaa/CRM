import './App.css'

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

import HomePage from './pages/HomePage';
import CreatePage from './pages/CreatePage';
import DetailPage from './pages/DetailPage';
import TaskItem from './components/TaskItem';
import type { TaskOut } from './types';

const dummyTask: TaskOut = {
    id: "1",
    title: "Call back about pricing",
    status: "open",
    priority: "high",
    due_at: "2026-09-09T09:00:00Z", // Past date
    is_overdue: true, 
    notes: "This is note1",
    assignee_user_id: "103",
    customer_id: "301",
    completed_at: "comp date",
    created_at: "create date",
    updated_at: "upd date",
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        
        {/* <Route path="/" element={<TaskItem task={dummyTask} />} /> */}

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





