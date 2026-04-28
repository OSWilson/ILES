import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import Layout from '../components/Layout'
import { useAuth } from '../context/AuthContext'
import client from '../api/client'
import styles from './ProfilePage.module.css'

export default function ProfilePage() {
  const { user, login } = useAuth()
  const qc = useQueryClient()

  const [form, setForm] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    department: user?.department || '',
  })

  const [pwForm, setPwForm] = useState({
    old_password: '',
    new_password: '',
    new_password2: '',
  })

  const [msg, setMsg] = useState({ type: '', text: '' })
  const [pwMsg, setPwMsg] = useState({ type: '', text: '' })

  const updateMutation = useMutation({
    mutationFn: data => client.patch('/auth/profile/', data),
    onSuccess: () => {
      setMsg({ type: 'success', text: 'Profile updated successfully.' })
      qc.invalidateQueries(['profile'])
    },
    onError: () => setMsg({ type: 'error', text: 'Failed to update profile.' }),
  })

  const pwMutation = useMutation({
    mutationFn: data => client.post('/auth/change-password/', data),
    onSuccess: () => {
      setPwMsg({ type: 'success', text: 'Password changed successfully.' })
      setPwForm({ old_password: '', new_password: '', new_password2: '' })
    },
    onError: err => {
      const data = err.response?.data
      const text = typeof data === 'object'
        ? Object.values(data).flat().join(' ')
        : 'Failed to change password.'
      setPwMsg({ type: 'error', text })
    },
  })

  return (
    <Layout>
      <h2 className={styles.title}>My Profile</h2>
      <span className={styles.roleBadge}>{user?.role}</span>

      {/* Profile info */}
      <div className={styles.card}>
        <h3 className={styles.cardTitle}>Personal Information</h3>

        {msg.text && (
          <div className={msg.type === 'success' ? styles.success : styles.error}>
            {msg.text}
          </div>
        )}

        <div className={styles.grid2}>
          <div className={styles.field}>
            <label className={styles.label}>First Name</label>
            <input className={styles.input} value={form.first_name}
              onChange={e => setForm({ ...form, first_name: e.target.value })} />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Last Name</label>
            <input className={styles.input} value={form.last_name}
              onChange={e => setForm({ ...form, last_name: e.target.value })} />
          </div>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Email</label>
          <input className={styles.input} type="email" value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })} />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Department</label>
          <input className={styles.input} value={form.department}
            onChange={e => setForm({ ...form, department: e.target.value })} />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Username (cannot change)</label>
          <input className={`${styles.input} ${styles.inputReadonly}`}
            value={user?.username} readOnly />
        </div>

        <button className={styles.btnPrimary}
          onClick={() => updateMutation.mutate(form)}
          disabled={updateMutation.isPending}>
          {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {/* Change password */}
      <div className={styles.card}>
        <h3 className={styles.cardTitle}>Change Password</h3>

        {pwMsg.text && (
          <div className={pwMsg.type === 'success' ? styles.success : styles.error}>
            {pwMsg.text}
          </div>
        )}

        {['old_password', 'new_password', 'new_password2'].map(field => (
          <div key={field} className={styles.field}>
            <label className={styles.label}>
              {field === 'old_password' ? 'Current Password'
                : field === 'new_password' ? 'New Password'
                : 'Confirm New Password'}
            </label>
            <input className={styles.input} type="password"
              value={pwForm[field]}
              onChange={e => setPwForm({ ...pwForm, [field]: e.target.value })} />
          </div>
        ))}

        <button className={styles.btnPrimary}
          onClick={() => pwMutation.mutate(pwForm)}
          disabled={pwMutation.isPending}>
          {pwMutation.isPending ? 'Changing...' : 'Change Password'}
        </button>
      </div>
    </Layout>
  )
}