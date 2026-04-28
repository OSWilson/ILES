import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Layout from '../../components/Layout'
import StatusBadge from '../../components/StatusBadge'
import client from '../../api/client'
import styles from './Dashboard.module.css'

export default function WorkplaceDashboard() {
  const qc = useQueryClient()
  const [comment, setComment] = useState('')
  const [activeLog, setActiveLog] = useState(null)

  const { data: logs = [] } = useQuery({
    queryKey: ['review-logs'],
    queryFn: () => client.get('/logs/').then(r => r.data),
  })

  const reviewMutation = useMutation({
    mutationFn: ({ id, action, comment }) =>
      client.post(`/logs/${id}/review/`, { action, comment }),
    onSuccess: () => {
      qc.invalidateQueries(['review-logs'])
      setActiveLog(null)
      setComment('')
    },
  })

  const pending = logs.filter(l => l.status === 'submitted')

  return (
    <Layout>
      <h2 className={styles.title}>Logs to Review ({pending.length})</h2>

      {!pending.length ? (
        <p className={styles.empty}>No logs pending review.</p>
      ) : (
        pending.map(log => (
          <div key={log.id} className={styles.logCard}>
            <div className={styles.logCardTop}>
              <div>
                <p className={styles.studentName}>{log.student_name} — Week {log.week_number}</p>
                <p className={styles.logMeta}>{log.week_start_date}</p>
              </div>
              <StatusBadge status={log.status} />
            </div>

            <p className={styles.logPreview}>{log.activities?.slice(0, 150)}...</p>

            {activeLog === log.id ? (
              <div className={styles.reviewSection}>
                <textarea
                  className={styles.textarea}
                  rows={2}
                  value={comment}
                  onChange={e => setComment(e.target.value)}
                  placeholder="Comment (required for rejection)"
                />
                <div className={styles.reviewActions}>
                  <button className={styles.btnApprove}
                    onClick={() => reviewMutation.mutate({ id: log.id, action: 'approve', comment })}>
                    Approve
                  </button>
                  <button className={styles.btnReject}
                    onClick={() => reviewMutation.mutate({ id: log.id, action: 'reject', comment })}>
                    Reject
                  </button>
                  <button className={styles.btnCancel} onClick={() => setActiveLog(null)}>
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <button className={styles.btnReviewLink} onClick={() => setActiveLog(log.id)}>
                Review →
              </button>
            )}
          </div>
        ))
      )}
    </Layout>
  )
}