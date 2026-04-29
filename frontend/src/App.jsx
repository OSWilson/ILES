import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, Link } from 'react-router-dom';
import './App.css';



const Sidebar = ({ role }) => (
  <div className="sidebar">
    <div className="sidebar-brand">ILES Portal</div>
    <nav className="sidebar-nav">
      <Link to="/dashboard" className="nav-item active">Dashboard Overview</Link>
      <Link to="/placements" className="nav-item">Student Placements</Link>
      {role === 'admin' && <Link to="/users" className="nav-item">Manage Users</Link>}
      <Link to="/settings" className="nav-item">System Settings</Link>
    </nav>
  </div>
);

const StatCard = ({ title, value, color }) => (
  <div className="stat-card" style={{ borderLeft: `4px solid ${color}` }}>
    <div className="stat-header">
      <span className="stat-title">{title}</span>
    </div>
    <div className="stat-value">{value}</div>
  </div>
);



function LoginPage({ setToken }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('student'); 
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://127.0.0.1:8000/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok) {
        
        if (data.user.role !== role) {
           setError(`Account found, but it is not a ${role} account.`);
           return;
        }

        localStorage.setItem('access', data.access);
        localStorage.setItem('userRole', data.user.role);
        setToken(data.access);
        navigate('/dashboard'); 
      } else {
        setError('Invalid username or password.');
      }
    } catch (err) {
      setError('Connection failed. Is the backend running?');
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>ILES Login</h2>
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label>I am a:</label>
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="student">Student</option>
              <option value="workplace">Workplace Supervisor</option>
              <option value="academic">Academic Supervisor</option>
              <option value="admin">Administrator</option>
            </select>
          </div>

          <input 
            type="text" 
            placeholder="Username" 
            value={username} 
            onChange={(e) => setUsername(e.target.value)} 
            required 
          />
          <input 
            type="password" 
            placeholder="Password" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)} 
            required 
          />
          
          <button type="submit" className="login-btn">Login</button>
        </form>
        {error && <p className="error-msg">{error}</p>}
      </div>
    </div>
  );
}

function AdminDashboard({ token }) {
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState('');
  const navigate = useNavigate();
  const userRole = localStorage.getItem('userRole');

  useEffect(() => {
    fetchLogs();
  }, [filter]);

  const fetchLogs = async () => {
    const url = filter 
      ? `http://127.0.0.1:8000/api/logs/?status=${filter}` 
      : 'http://127.0.0.1:8000/api/logs/';
    
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setLogs(data);
  };

  const handleAction = async (id, action) => {
    const response = await fetch(`http://127.0.0.1:8000/api/logs/${id}/review/`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ action, comment: action === 'reject' ? 'Revisions needed' : '' })
    });
    if (response.ok) fetchLogs();
  };

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = '/login';
  };

  return (
    <div className="dashboard-layout">
      <Sidebar role={userRole} />
      <main className="main-content">
        <header className="top-nav">
          <div>
            <h1>Registrar Dashboard</h1>
            <p className="welcome-text">Managing student log submissions</p>
          </div>
          <button className="logout-btn" onClick={handleLogout}>Logout</button>
        </header>

        <section className="stats-grid">
          <StatCard title="Pending Review" value={logs.filter(l => l.status === 'submitted').length} color="#fbbf24" />
          <StatCard title="Total Logs" value={logs.length} color="#10b981" />
          <StatCard title="System Alerts" value="0" color="#3b82f6" />
        </section>

        <section className="table-section">
          <div className="table-header">
            <h3>Weekly Logs Submissions</h3>
            <select onChange={(e) => setFilter(e.target.value)} className="filter-dropdown">
              <option value="">All Statuses</option>
              <option value="submitted">Submitted</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Week No.</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id}>
                  <td>{log.student_name}</td>
                  <td>Week {log.week_number}</td>
                  <td><span className={`status-tag ${log.status}`}>{log.status}</span></td>
                  <td>
                    {log.status === 'submitted' && (
                      <div className="action-group">
                        <button onClick={() => handleAction(log.id, 'approve')} className="btn-approve">Approve</button>
                        <button onClick={() => handleAction(log.id, 'reject')} className="btn-reject">Reject</button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </main>
    </div>
  );
}

// --- Main App ---

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('access'));

  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={!token ? <LoginPage setToken={setToken} /> : <Navigate to="/dashboard" />} 
        />
        <Route 
          path="/dashboard" 
          element={token ? <AdminDashboard token={token} /> : <Navigate to="/login" />} 
        />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}