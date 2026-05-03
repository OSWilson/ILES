import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Layout from '../../components/Layout'
import client from '../../api/client'
import styles from './LogForm.module.css'

const FIELDS = [
  { name: 'activities', label: 'Activities Performed *' },
  { name: 'skills_gained', label: 'Skills Gained' },
  { name: 'challenges', label: 'Challenges Faced' },
  { name: 'next_week_plan', label: 'Next Week Plan' },
]

export default function LogForm() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    week_number: '', week_start_date: '',
    activities: '', skills_gained: '', challenges: '', next_week_plan: '',
  })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (id) client.get(`/logs/${id}/`).then(r => setForm(r.data))
  }, [id])

  const handleSave = async (andSubmit = false) => {
    setSubmitting(true)
    setError('')
    try {
      const { data: log } = id
        ? await client.patch(`/logs/${id}/`, form)
        : await client.post('/logs/', form)
      if (andSubmit) await client.post(`/logs/${log.id}/submit/`)
      navigate('/student/logs')
    } catch (err) {
      setError(JSON.stringify(err.response?.data) || 'Error saving log.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Layout>
      <h2 className={styles.title}>{id ? 'Edit Log' : 'New Weekly Log'}</h2>
      {error && <div className={styles.error}>{error}</div>}

      <div className={styles.card}>
        <div className={styles.grid2}>
          <div className={styles.field}>
            <label className={styles.label}>Week Number</label>
            <input type="number" className={styles.input} value={form.week_number}
              onChange={e => setForm({ ...form, week_number: e.target.value })} min="1" required />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Week Start Date</label>
            <input type="date" className={styles.input} value={form.week_start_date}
              onChange={e => setForm({ ...form, week_start_date: e.target.value })} required />
          </div>
        </div>

        {FIELDS.map(f => (
          <div key={f.name} className={styles.field}>
            <label className={styles.label}>{f.label}</label>
            <textarea className={styles.textarea} rows={3} value={form[f.name] || ''}
              onChange={e => setForm({ ...form, [f.name]: e.target.value })} />
          </div>
        ))}

        <div className={styles.actions}>
          <button className={styles.btnSecondary} onClick={() => handleSave(false)} disabled={submitting}>
            Save Draft
          </button>
          <button className={styles.btnPrimary} onClick={() => handleSave(true)} disabled={submitting}>
            Save & Submit
          </button>
          <button className={styles.btnCancel} onClick={() => navigate('/student/logs')}>
            Cancel
          </button>
        </div>
      </div>
    </Layout>
  )
}