import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Layout from '../../components/Layout'
import StatusBadge from '../../components/StatusBadge'
import { useToast } from '../../context/ToastContext'
import client from '../../api/client'
import styles from './EvaluationDetail.module.css'

export default function EvaluationDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const { showToast } = useToast()

 
  const [scores, setScores] = useState({})

  const { data: evaluation, isLoading } = useQuery({
    queryKey: ['evaluation', id],
    queryFn: () => client.get(`/evaluations/${id}/`).then(r => r.data),
  })

  const { data: criteria = [] } = useQuery({
    queryKey: ['criteria'],
    queryFn: () => client.get('/criteria/').then(r => r.data),
  })

  const scoreMutation = useMutation({
    mutationFn: ({ criteria_id, score }) =>
      client.post(`/evaluations/${id}/scores/`, {
        criteria: criteria_id,
        score,
      }),
    onSuccess: () => {
      qc.invalidateQueries(['evaluation', id])
      showToast('Score saved', 'success')
    },
    onError: () => showToast('Failed to save score', 'error'),
  })

  const finalizeMutation = useMutation({
    mutationFn: () => client.post(`/evaluations/${id}/finalize/`),
    onSuccess: () => {
      qc.invalidateQueries(['evaluation', id])
      qc.invalidateQueries(['evaluations'])
      showToast('Evaluation finalized!', 'success')
    },
  })

  if (isLoading) return <Layout><p>Loading...</p></Layout>
  if (!evaluation) return <Layout><p>Evaluation not found.</p></Layout>

  const savedScores = {}
  evaluation.criteria_scores?.forEach(s => {
    savedScores[s.criteria] = s.score
  })

  const isFinalized = evaluation.status === 'finalized'

  return (
    <Layout>
      <button className={styles.backBtn} onClick={() => navigate('/academic/dashboard')}>
        ← Back to Evaluations
      </button>

      <h2 className={styles.title}>Evaluation Detail</h2>
      <p className={styles.subtitle}>
        Placement ID: {evaluation.placement} &nbsp;|&nbsp;
        <StatusBadge status={evaluation.status} />
      </p>

      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <span>Criteria Scores</span>
          <span style={{ fontSize: 12, color: '#9ca3af' }}>Score out of 10</span>
        </div>

        {criteria.map(c => {
          const existing = savedScores[c.id]
          const inputVal = scores[c.id] ?? existing ?? ''

          return (
            <div key={c.id} className={styles.scoreRow}>
              <div>
                <p className={styles.criteriaName}>{c.name}</p>
                <p className={styles.criteriaWeight}>Weight: {c.weight}%</p>
              </div>

              {existing !== undefined && (
                <span style={{ fontSize: 13, color: '#16a34a', fontWeight: 600 }}>
                  Saved: {existing}
                </span>
              )}

              <input
                type="number"
                min="0" max="10" step="0.5"
                className={styles.scoreInput}
                value={inputVal}
                disabled={isFinalized}
                onChange={e => setScores({ ...scores, [c.id]: e.target.value })}
              />

              {!isFinalized && (
                <button
                  className={styles.btnSave}
                  onClick={() => scoreMutation.mutate({
                    criteria_id: c.id,
                    score: scores[c.id] ?? existing,
                  })}
                  disabled={scoreMutation.isPending}
                >
                  Save
                </button>
              )}
            </div>
          )
        })}
      </div>

      <div className={styles.totalBox}>
        <span className={styles.totalLabel}>Total Score</span>
        <span className={styles.totalValue}>
          {evaluation.total_score ?? '—'}<span style={{ fontSize: 16, color: '#9ca3af' }}>/100</span>
        </span>
      </div>

      {isFinalized ? (
        <div className={styles.finalized}>✓ This evaluation has been finalized</div>
      ) : (
        <button
          className={styles.btnFinalize}
          onClick={() => finalizeMutation.mutate()}
          disabled={finalizeMutation.isPending}
        >
          {finalizeMutation.isPending ? 'Finalizing...' : 'Finalize Evaluation'}
        </button>
      )}
    </Layout>
  )
}