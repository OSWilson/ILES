import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import styles from './Layout.module.css'

const NAV = {

  student: [
    { to: '/student/dashboard', label: 'Dashboard' },
    { to: '/student/logs', label: 'My Logs' },
    { to: '/profile', label: 'Profile' },
  ],
  workplace: [
    { to: '/workplace/dashboard', label: 'Dashboard' },
    { to: '/profile', label: 'Profile' },
  ],
  academic: [
    { to: '/academic/dashboard', label: 'Dashboard' },
    { to: '/profile', label: 'Profile' },
  ],
  admin: [
    { to: '/admin/dashboard', label: 'Dashboard' },
    { to: '/profile', label: 'Profile' },
  ],
}


export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className={styles.wrapper}>
      <nav className={styles.nav}>
        <div className={styles.navLeft}>
          <span className={styles.logo}>ILES</span>
          {(NAV[user?.role] || []).map(l => (
            <Link key={l.to} to={l.to} className={styles.navLink}>{l.label}</Link>
          ))}
        </div>
        <div className={styles.navRight}>
          <span className={styles.navUser}>{user?.full_name}</span>
          <span className={styles.navRole}>{user?.role}</span>
          <button className={styles.logoutBtn} onClick={() => { logout(); navigate('/login') }}>
            Logout
          </button>
        </div>
      </nav>
      <main className={styles.main}>{children}</main>
    </div>
  )
}



