import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import './App.css';


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
        if (data.user.role !== role && role !== 'supervisor') {
           setError(`Account found, but it is not a ${role} account.`);
           return;
        }

        localStorage.setItem('access', data.access);
        localStorage.setItem('userRole', data.user.role);
        setToken(data.access);
        navigate('/dashboard'); // Redirect after login
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


function Dashboard({ token, setToken }) {
  const role = localStorage.getItem('userRole');
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.clear();
    setToken(null);
    navigate('/login');
  };

  return (
    <div className="dashboard">
      <nav>
        <h1>{role.toUpperCase()} Portal</h1>
        <button onClick={handleLogout}>Logout</button>
      </nav>
      <div className="content">
        <h2>Welcome back!</h2>
        <p>You are logged in as a <strong>{role}</strong>.</p>
        
        {role === 'student' ? <p>Check your weekly logs.</p> : <p>Review student placements.</p>}
      </div>
    </div>
  );
}


function App() {
  const [token, setToken] = useState(localStorage.getItem('access'));

  return (
    <Router>
      <Routes>
        
        <Route 
          path="/login" 
          element={!token ? <LoginPage setToken={setToken} /> : <Navigate to="/dashboard" />} 
        />
        
        {/* Protect the Dashboard Route */}
        <Route 
          path="/dashboard" 
          element={token ? <Dashboard token={token} setToken={setToken} /> : <Navigate to="/login" />} 
        />

        {/* Redirect any other path to login */}
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

export default App;