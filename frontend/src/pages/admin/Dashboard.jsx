import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import Layout from '../../components/Layout'
import client from '../../api/client'
import styles from './Dashboard.module.css'
export default function AdminDashboard() {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    student: '', company_name: '', start_date: '', end_date: '',
    workplace_supervisor: '', academic_supervisor: '',
  })

  const { data: placements = [] } = useQuery({ queryKey: ['placements'], queryFn: () => client.get('/placements/').then(r => r.data) })
  const { data: students = [] } = useQuery({ queryKey: ['students'], queryFn: () => client.get('/users/?role=student').then(r => r.data) })
  const { data: wpUsers = [] } = useQuery({ queryKey: ['wp-users'], queryFn: () => client.get('/users/?role=workplace').then(r => r.data) })
  const { data: acUsers = [] } = useQuery({ queryKey: ['ac-users'], queryFn: () => client.get('/users/?role=academic').then(r => r.data) })

  const createMutation = useMutation({
    mutationFn: data => client.post('/placements/', data),
    onSuccess: () => {
      qc.invalidateQueries(['placements'])
      setForm({ student: '', company_name: '', start_date: '', end_date: '', workplace_supervisor: '', academic_supervisor: '' })
    },
  })

  const f = (key, val) => setForm({ ...form, [key]: val })

  return (
    <Layout>
      <h2 className={styles.title}>Admin Dashboard</h2>

      <div className={styles.stats}>
        {[['Placements', placements.length], ['Students', students.length], ['Active', placements.filter(p => p.is_active).length]].map(([label, val]) => (
          <div key={label} className={styles.statCard}>
            <p className={styles.statValue}>{val}</p>
            <p className={styles.statLabel}>{label}</p>
          </div>
        ))}
      </div>

      <div className={styles.formCard}>
        <h3 className={styles.formTitle}>Assign New Placement</h3>
        <div className={styles.grid2}>
          <select className={styles.select} value={form.student} onChange={e => f('student', e.target.value)}>
            <option value="">Select Student</option>
            {students.map(s => <option key={s.id} value={s.id}>{s.full_name}</option>)}
          </select>
          <input className={styles.input} type="text" placeholder="Company Name"
            value={form.company_name} onChange={e => f('company_name', e.target.value)} />
          <input className={styles.input} type="date" value={form.start_date} onChange={e => f('start_date', e.target.value)} />
          <input className={styles.input} type="date" value={form.end_date} onChange={e => f('end_date', e.target.value)} />
          <select className={styles.select} value={form.workplace_supervisor} onChange={e => f('workplace_supervisor', e.target.value)}>
            <option value="">Workplace Supervisor (optional)</option>
            {wpUsers.map(u => <option key={u.id} value={u.id}>{u.full_name}</option>)}
          </select>
          <select className={styles.select} value={form.academic_supervisor} onChange={e => f('academic_supervisor', e.target.value)}>
            <option value="">Academic Supervisor (optional)</option>
            {acUsers.map(u => <option key={u.id} value={u.id}>{u.full_name}</option>)}
          </select>
        </div>
        <button className={styles.btnCreate} onClick={() => createMutation.mutate(form)}>
          Create Placement
        </button>
      </div>

      <div className={styles.tableCard}>
        <div className={styles.tableHeader}>All Placements</div>
        <table className={styles.table}>
          <thead className={styles.thead}>
            <tr>
              {['Student', 'Company', 'Start', 'End', 'Active'].map(h => (
                <th key={h} className={styles.th}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {placements.map(p => (
              <tr key={p.id}>
                <td className={styles.td}>{p.student_detail?.full_name || p.student}</td>
                <td className={styles.td}>{p.company_name}</td>
                <td className={styles.tdMuted}>{p.start_date}</td>
                <td className={styles.tdMuted}>{p.end_date}</td>
                <td className={styles.td}>
                  <span className={p.is_active ? styles.activeYes : styles.activeNo}>
                    {p.is_active ? 'Yes' : 'No'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Layout>
  )
}
