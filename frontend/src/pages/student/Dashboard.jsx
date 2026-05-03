import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import Layout from '../../components/Layout'
import StatusBadge from '../../components/StatusBadge'
import client from '../../api/client'
import styles from './Dashboard.module.css'

export default function StudentDashboard() {
  const { data: placement } = useQuery({
    queryKey: ['my-placement'],
    queryFn: () => client.get('/placements/mine/').then(r => r.data),
  })
  const { data: logs = [] } = useQuery({
    queryKey: ['my-logs'],
    queryFn: () => client.get('/logs/').then(r => r.data),
  })

  const counts = {
    total: logs.length,
    approved: logs.filter(l => l.status === 'approved').length,
    pending: logs.filter(l => l.status === 'submitted').length,
    rejected: logs.filter(l => l.status === 'rejected').length,
  }

  return (
    <Layout>
      <h2 className={styles.pageTitle || 'pageTitle'}>Student Dashboard</h2>

      {placement ? (
        <div className={styles.placement}>
          <p className={styles.placementLabel}>Current Placement</p>
          <p className={styles.placementName}>{placement.company_name}</p>
          <p className={styles.placementDates}>{placement.start_date} → {placement.end_date}</p>
        </div>
      ) : (
        <div className={styles.noPlacement}>No active placement. Contact your administrator.</div>
      )}

      <div className={styles.stats}>
        {[
          ['Total', counts.total, 'gray'],
          ['Approved', counts.approved, 'green'],
          ['Pending', counts.pending, 'blue'],
          ['Rejected', counts.rejected, 'red'],
        ].map(([label, val, color]) => (
          <div key={label} className={styles.statCard}>
            <p className={`${styles.statValue} ${styles[color]}`}>{val}</p>
            <p className={styles.statLabel}>{label}</p>
          </div>
        ))}
      </div>

      <div className={styles.actions}>
        <Link to="/student/logs/new" className={styles.btnPrimary}>+ New Log</Link>
        <Link to="/student/logs" className={styles.btnSecondary}>All Logs</Link>
      </div>

      <div className={styles.card}>
        <div className={styles.cardHeader}>Recent Logs</div>
        {!logs.length ? (
          <p className={styles.empty}>No logs yet.</p>
        ) : (
          logs.slice(0, 5).map(log => (
            <div key={log.id} className={styles.logItem}>
              <div>
                <p className={styles.logWeek}>Week {log.week_number}</p>
                <p className={styles.logDate}>{log.week_start_date}</p>
              </div>
              <StatusBadge status={log.status} />
            </div>
          ))
        )}
      </div>
    </Layout>
  )
}