import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import client from '../api/client'
import styles from './RegisterPage.module.css'

export default function RegisterPage() {
  const navigate = useNavigate()

  const [form, setForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    role: '',
    department: '',
    student_number: '',
    staff_number: '',
    password: '',
    password2: '',
  })

  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  // Which extra field to show depends on role selected
  const isStudent = form.role === 'student'
  const isStaff = ['workplace', 'academic', 'admin'].includes(form.role)

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async e => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // Basic frontend validation before hitting the API
    if (form.password !== form.password2) {
      setError('Passwords do not match.')
      return
    }
    if (!form.role) {
      setError('Please select a role.')
      return
    }

    setLoading(true)
    try {
      await client.post('/api/auth/register/', form)
      setSuccess('Account created! Redirecting to login...')
      setTimeout(() => navigate('/login'), 2000)
    } catch (err) {
      // Django returns field-level errors as an object
      // e.g. { username: ['This field is required.'] }
      const data = err.response?.data
      if (typeof data === 'object') {
        // Flatten all error messages into one string
        const messages = Object.entries(data)
          .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
          .join(' | ')
        setError(messages)
      } else {
        setError('Registration failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <h1 className={styles.title}>Create Account</h1>
        <p className={styles.subtitle}>Internship Logging & Evaluation System</p>

        {error && <div className={styles.error}>{error}</div>}
        {success && <div className={styles.success}>{success}</div>}

        <form onSubmit={handleSubmit}>
          {/* Name row */}
          <div className={styles.grid2}>
            <div className={styles.field}>
              <label className={styles.label}>First Name</label>
              <input className={styles.input} name="first_name"
                value={form.first_name} onChange={handleChange} required />
            </div>
            <div className={styles.field}>
              <label className={styles.label}>Last Name</label>
              <input className={styles.input} name="last_name"
                value={form.last_name} onChange={handleChange} required />
            </div>
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Username</label>
            <input className={styles.input} name="username"
              value={form.username} onChange={handleChange} required />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Email</label>
            <input className={styles.input} type="email" name="email"
              value={form.email} onChange={handleChange} required />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Role</label>
            <select className={styles.select} name="role"
              value={form.role} onChange={handleChange} required>
              <option value="">Select your role</option>
              <option value="student">Student Intern</option>
              <option value="workplace">Workplace Supervisor</option>
              <option value="academic">Academic Supervisor</option>
              <option value="admin">Administrator</option>
            </select>
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Department</label>
            <input className={styles.input} name="department"
              value={form.department} onChange={handleChange}
              placeholder="e.g. Computer Science" />
          </div>

          {/* Show student number only for students */}
          {isStudent && (
            <div className={styles.field}>
              <label className={styles.label}>Student Number</label>
              <input className={styles.input} name="student_number"
                value={form.student_number} onChange={handleChange}
                placeholder="e.g. 2024/001" />
            </div>
          )}

          {/* Show staff number for supervisors and admins */}
          {isStaff && (
            <div className={styles.field}>
              <label className={styles.label}>Staff Number</label>
              <input className={styles.input} name="staff_number"
                value={form.staff_number} onChange={handleChange}
                placeholder="e.g. ST001" />
            </div>
          )}

          <div className={styles.grid2}>
            <div className={styles.field}>
              <label className={styles.label}>Password</label>
              <input className={styles.input} type="password" name="password"
                value={form.password} onChange={handleChange} required />
            </div>
            <div className={styles.field}>
              <label className={styles.label}>Confirm Password</label>
              <input className={styles.input} type="password" name="password2"
                value={form.password2} onChange={handleChange} required />
            </div>
          </div>

          <button type="submit" className={styles.submit} disabled={loading}>
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <p className={styles.loginLink}>
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  )
}