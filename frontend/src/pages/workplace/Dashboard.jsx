import { useState, useEffect } from 'react'
import Layout from '../../components/Layout'
import client from '../../api/client'
import styles from './Dashboard.module.css' 

export default function WorkplaceDashboard() {
  const [stats, setStats] = useState({
    total_assigned: 0,
    pending_review: 0,
    approved: 0,
    rejected: 0,
  })
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  
  
  const [selectedLog, setSelectedLog] = useState(null)
  const [reviewComment, setReviewComment] = useState('')
  const [actionLoading, setActionLoading] = useState(false)

  // Fetch stats and logs from backend
  const fetchDashboardData = async () => {
    try {
      setError('')
      const [statsRes, logsRes] = await Promise.all([
        client.get('/stats/supervisor/'),
        client.get('/logs/')
      ])
      setStats(statsRes.data)
      setLogs(logsRes.data)
    } catch (err) {
      setError('Failed to fetch dashboard data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
  }, [])

 
  const handleReview = async (logId, action) => {
    if (action === 'reject' && !reviewComment.trim()) {
      alert('Please provide a comment before rejecting a log.')
      return
    }

    setActionLoading(true)
    try {
      await client.post(`/logs/${logId}/review/`, {
        action: action,
        comment: reviewComment
      })
      
      
      setSelectedLog(null)
      setReviewComment('')
      await fetchDashboardData()
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to submit review action.')
    } finally {
      setActionLoading(false)
    }
  }

  if (loading) return <Layout><div className={styles.centered}>Loading Dashboard Data...</div></Layout>

  return (
    <Layout>
      <div className={styles.container}>
        <div className={styles.header}>
          <h2>Workplace Supervisor Dashboard</h2>
          <p className={styles.subtitle}>Review submitted logs and manage your assigned student interns.</p>
        </div>

        {error && <div className={styles.errorBanner}>{error}</div>}

        {/* 1. Statistics Cards Section */}
        <div className={styles.statsGrid}>
          <div className={`${styles.statCard} ${styles.total}`}>
            <h3>{stats.total_assigned}</h3>
            <p>Total Assigned Logs</p>
          </div>
          <div className={`${styles.statCard} ${styles.pending}`}>
            <h3>{stats.pending_review}</h3>
            <p>Pending Review</p>
          </div>
          <div className={`${styles.statCard} ${styles.approved}`}>
            <h3>{stats.approved}</h3>
            <p>Approved Logs</p>
          </div>
          <div className={`${styles.statCard} ${styles.rejected}`}>
            <h3>{stats.rejected}</h3>
            <p>Rejected Logs</p>
          </div>
        </div>

        {/* 2. Main Dashboard Split Layout */}
        <div className={styles.contentLayout}>
          
          {/* Left Column: List of Student Logs */}
          <div className={styles.listSection}>
            <h3>Weekly Logs Queue</h3>
            {logs.length === 0 ? (
              <p className={styles.emptyText}>No logs found for your assigned placements.</p>
            ) : (
              <div className={styles.logQueue}>
                {logs.map(log => (
                  <div 
                    key={log.id} 
                    className={`${styles.logItem} ${selectedLog?.id === log.id ? styles.activeLog : ''}`}
                    onClick={() => { setSelectedLog(log); setReviewComment(''); }}
                  >
                    <div className={styles.logItemHeader}>
                      <strong>{log.student_name || `Student #${log.student}`}</strong>
                      <span className={`${styles.badge} ${styles[log.status]}`}>{log.status}</span>
                    </div>
                    <div className={styles.logItemMeta}>
                      <span>Week {log.week_number}</span>
                      <span>•</span>
                      <span>Started: {log.week_start_date}</span>
                    </div>
                    <p className={styles.snippet}>
                      {log.activities ? log.activities.substring(0, 80) + '...' : 'No description provided.'}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Right Column: Dynamic Action Inspection Station */}
          <div className={styles.inspectionSection}>
            {selectedLog ? (
              <div className={styles.inspectionCard}>
                <div className={styles.inspectionHeader}>
                  <h3>Week {selectedLog.week_number} Review</h3>
                  <p>Intern: <strong>{selectedLog.student_name}</strong> ({selectedLog.company_name})</p>
                </div>
                
                <div className={styles.inspectionBody}>
                  <div className={styles.detailGroup}>
                    <h4>Activities Undertaken</h4>
                    <p>{selectedLog.activities}</p>
                  </div>

                  {selectedLog.skills_gained && (
                    <div className={styles.detailGroup}>
                      <h4>Skills Gained / Developed</h4>
                      <p>{selectedLog.skills_gained}</p>
                    </div>
                  )}

                  {selectedLog.challenges && (
                    <div className={styles.detailGroup}>
                      <h4>Challenges Encountered</h4>
                      <p>{selectedLog.challenges}</p>
                    </div>
                  )}

                  {selectedLog.next_week_plan && (
                    <div className={styles.detailGroup}>
                      <h4>Next Week's Outlook</h4>
                      <p>{selectedLog.next_week_plan}</p>
                    </div>
                  )}
                </div>

                {/* Conditional Actions Input Area based on Status */}
                {selectedLog.status === 'submitted' ? (
                  <div className={styles.actionArea}>
                    <h4>Action Station</h4>
                    <textarea
                      className={styles.commentInput}
                      placeholder="Add supervisor internal commentary or reasons for rejection here..."
                      value={reviewComment}
                      onChange={(e) => setReviewComment(e.target.value)}
                      rows={3}
                    />
                    <div className={styles.actionButtons}>
                      <button 
                        className={styles.approveBtn} 
                        disabled={actionLoading}
                        onClick={() => handleReview(selectedLog.id, 'approve')}
                      >
                        {actionLoading ? 'Processing...' : 'Approve Log'}
                      </button>
                      <button 
                        className={styles.rejectBtn} 
                        disabled={actionLoading}
                        onClick={() => handleReview(selectedLog.id, 'reject')}
                      >
                        {actionLoading ? 'Processing...' : 'Reject / Request Changes'}
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className={styles.completedReviewCard}>
                    <p>This log was processed with a status of <strong>{selectedLog.status.toUpperCase()}</strong>.</p>
                    {selectedLog.supervisor_comment && (
                      <p className={styles.oldComment}><strong>Your saved feedback:</strong> {selectedLog.supervisor_comment}</p>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className={styles.placeholderCard}>
                <p>Select a weekly log from the queue layout to inspect details, leave feedback, and complete supervisor approval actions.</p>
              </div>
            )}
          </div>

        </div>
      </div>
    </Layout>
  )
}