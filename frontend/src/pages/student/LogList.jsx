import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import Layout from '../../components/Layout'
import StatusBadge from '../../components/StatusBadge'
import client from '../../api/client'
import styles from './LogList.module.css'

export default function LogList() {
  const qc = useQueryClient()
  const navigate = useNavigate()

  const { data: logs = [], isLoading } = useQuery({
    queryKey: ['my-logs'],
    queryFn: () => client.get('/logs/').then(r => r.data),
  })

  const submitMutation = useMutation({
    mutationFn: id => client.post(`/logs/${id}/submit/`),
    onSuccess: () => qc.invalidateQueries(['my-logs']),
  })

  return (
    <Layout>
      <div className={styles.header}>
        <h2 className={styles.title}>My Weekly Logs</h2>
        <Link to="/student/logs/new" className={styles.btnPrimary}>+ New Log</Link>
      </div>

      <div className={styles.card}>
        {isLoading ? (
          <p className={styles.loading}>Loading...</p>
        ) : !logs.length ? (
          <p className={styles.empty}>No logs yet.</p>
        ) : (
          <table className={styles.table}>
            <thead className={styles.thead}>
              <tr>
                {['Week', 'Date', 'Status', 'Actions'].map(h => (
                  <th key={h} className={styles.th}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id}>
                  <td className={styles.td}><span className={styles.week}>Week {log.week_number}</span></td>
                  <td className={styles.tdMuted}>{log.week_start_date}</td>
                  <td className={styles.td}><StatusBadge status={log.status} /></td>
                  <td className={styles.tdActions}>
                    {log.can_edit && (
                      <>
                        <button className={styles.btnEdit} onClick={() => navigate(`/student/logs/${log.id}/edit`)}>
                          Edit
                        </button>
                        {log.status === 'draft' && (
                          <button className={styles.btnSubmit} onClick={() => submitMutation.mutate(log.id)}>
                            Submit
                          </button>
                        )}
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </Layout>
  )
}