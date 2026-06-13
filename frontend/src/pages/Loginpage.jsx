import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import styles from './LoginPage.module.css'
import { Link } from "react-router-dom";

const REDIRECTS = {
  student: '/student/dashboard',
  workplace: '/workplace/dashboard',
  academic: '/academic/dashboard',
  admin: '/admin/dashboard',
}

export default function LoginPage() {
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async e => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const user = await login(form.username, form.password)
      navigate(REDIRECTS[user.role] || '/login')
    } catch {
      setError('Invalid username or password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <h1 className={styles.title}>ILES</h1>
        <p className={styles.subtitle}>Internship Logging & Evaluation System</p>

        {error && <div className={styles.error}>{error}</div>}

        <form className={styles.form} onSubmit={handleSubmit}>
          {['username', 'password'].map(field => (
            <div key={field} className={styles.field}>
              <label className={styles.label}>{field.charAt(0).toUpperCase() + field.slice(1)}</label>
              <input
                className={styles.input}
                type={field === 'password' ? 'password' : 'text'}
                value={form[field]}
                onChange={e => setForm({ ...form, [field]: e.target.value })}
                required
              />
            </div>
          ))}
          <button type="submit" className={styles.submit} disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>

        
           <p style={{ textAlign: 'center', fontSize: 13, color: '#9ca3af', marginTop: 16 }}>
               No account? <Link to="/register" style={{ color: '#2563eb', fontWeight: 500 }}>Register here</Link>
           </p>

        </form>
      </div>
    </div>
  )
}



