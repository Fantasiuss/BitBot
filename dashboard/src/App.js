import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './Dashboard';
import GuildSettings from './GuildSettings';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/guild/:id" element={<GuildSettings />} />
      </Routes>
    </Router>
  );
}

export default App;
