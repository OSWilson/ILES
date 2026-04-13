import React, { useState, useEffect } from 'react';


const styles = {
  container: { display: 'flex', minHeight: '100vh', fontFamily: '"Segoe UI", Roboto, Helvetica, Arial, sans-serif', backgroundColor: '#f0f2f5' },
  sidebar: { width: '260px', backgroundColor: '#1a2a3a', color: 'white', padding: '25px', boxShadow: '2px 0 5px rgba(0,0,0,0.1)' },
  navItem: { padding: '12px 15px', cursor: 'pointer', borderRadius: '6px', marginBottom: '10px', transition: '0.3s' },
  main: { flex: 1, padding: '40px', overflowY: 'auto' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' },
  card: { backgroundColor: 'white', padding: '25px', borderRadius: '12px', marginBottom: '25px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' },
  button: { padding: '10px 20px', backgroundColor: '#3498db', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' },
  badge: (status) => {
    let bg = '#95a5a6'; // Default Gray
    if (status === 'Accepted') bg = '#27ae60';
    if (status === 'Shortlisted' || status === 'Interview') bg = '#f1c40f';
    if (status === 'Rejected') bg = '#e74c3c';
    return { padding: '6px 12px', borderRadius: '20px', fontSize: '12px', color: 'white', backgroundColor: bg };
  }
};

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [applications, setApplications] = useState([]);
  const [availableJobs, setAvailableJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch Django API??
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [appRes, jobRes] = await Promise.all([
          fetch('http://127.0.0.1:8000/api/applications/'),
          fetch('http://127.0.0.1:8000/api/internships/')
        ]);
        
        const appData = await appRes.json();
        const jobData = await jobRes.json();
        
        setApplications(appData);
        setAvailableJobs(jobData);
        setLoading(false);
      } catch (error) {
        console.error("Failed to fetch data from Django:", error);
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div style={styles.container}>
      {/* Sidebar Navigation */}
      <div style={styles.sidebar}>
        <h2 style={{ borderBottom: '1px solid #34495e', paddingBottom: '15px' }}>Student Portal</h2>
        <nav style={{ marginTop: '30px' }}>
          <div 
            style={{ ...styles.navItem, backgroundColor: activeTab === 'dashboard' ? '#3498db' : 'transparent' }} 
            onClick={() => setActiveTab('dashboard')}
          >
            📊 My Dashboard
          </div>
          <div 
            style={{ ...styles.navItem, backgroundColor: activeTab === 'find' ? '#3498db' : 'transparent' }} 
            onClick={() => setActiveTab('find')}
          >
            🔍 Find Internships
          </div>
        </nav>
      </div>

      {/* Main Content Area */}
      <main style={styles.main}>
        <header style={styles.header}>
          <h1>{activeTab === 'dashboard' ? "Student Dashboard" : "Available Opportunities"}</h1>
          <div style={{ color: '#7f8c8d' }}>Welcome back, Student</div>
        </header>

        {loading ? (
          <p>Connecting to backend...</p>
        ) : activeTab === 'dashboard' ? (
          <>
            {/* Section: Application Progress */}
            <section style={styles.card}>
              <h3 style={{ marginTop: 0 }}>Your Application Progress</h3>
              {applications.length > 0 ? (
                applications.map(app => (
                  <div key={app.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px 0', borderBottom: '1px solid #eee' }}>
                    <div>
                      {/* Using internship_details from your ApplicationSerializer */}
                      <strong style={{ fontSize: '16px' }}>{app.internship_details?.title || "Unknown Position"}</strong>
                      <div style={{ color: '#7f8c8d', fontSize: '14px' }}>{app.internship_details?.company || "Company Name"}</div>
                    </div>
                    <span style={styles.badge(app.status)}>{app.status}</span>
                  </div>
                ))
              ) : (
                <p style={{ color: '#7f8c8d' }}>You haven't applied to any internships yet.</p>
              )}
            </section>

            {/* Section: Quick Recommendation Stats */}
            <div style={styles.grid}>
              <div style={styles.card}>
                <h4>Profile Match</h4>
                <p>Your skills match <strong>85%</strong> of current openings in your department.</p>
              </div>
              <div style={styles.card}>
                <h4>Notifications</h4>
                <p>You have 2 new messages from recruiters.</p>
              </div>
            </div>
          </>
        ) : (
          /* Section: Find Internships */
          <div style={styles.grid}>
            {availableJobs.map(job => (
              <div key={job.id} style={styles.card}>
                <h3 style={{ marginTop: 0, color: '#2c3e50' }}>{job.title}</h3>
                <p style={{ fontWeight: 'bold', color: '#3498db' }}>{job.company}</p>
                <p style={{ fontSize: '14px', color: '#666', minHeight: '60px' }}>{job.description}</p>
                <div style={{ fontSize: '12px', color: '#95a5a6', marginBottom: '15px' }}>
                  <strong>Required:</strong> {job.required_coursework}
                </div>
                <button style={styles.button}>Apply Now</button>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;