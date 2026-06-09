import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Layout from '../../components/Layout'
import StatusBadge from '../../components/StatusBadge'
import client from '../../api/client'
import styles from './Dashboard.module.css'

export default function AcademicDashboard() {
  const qc = useQueryClient()

  const { data: evaluations = [] } = useQuery({
    queryKey: ['evaluations'],
    queryFn: () => client.get('/evaluations/').then(r => r.data),
  })

  const finalizeMutation = useMutation({
    mutationFn: id => client.post(`/evaluations/${id}/finalize/`),
    onSuccess: () => qc.invalidateQueries(['evaluations']),
  })

  return (
    <Layout>
      <h2 className={styles.title}>Evaluations</h2>

      <div className={styles.card}>
        {!evaluations.length ? (
          <p className={styles.empty}>No evaluations assigned.</p>
        ) : (
          <table className={styles.table}>
            <thead className={styles.thead}>
              <tr>
                {['Placement', 'Score', 'Status', 'Actions'].map(h => (
                  <th key={h} className={styles.th}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {evaluations.map(ev => (
                <tr key={ev.id}>
                  <td className={styles.td}>{ev.placement}</td>
                  <td className={styles.tdScore}>{ev.total_score ?? '—'}</td>
                  <td className={styles.td}><StatusBadge status={ev.status} /></td>
                  <td className={styles.td}>
                    {ev.status !== 'finalized' && (
                      <button className={styles.btnFinalize}
                        onClick={() => finalizeMutation.mutate(ev.id)}>
                        Finalize
                      </button>
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