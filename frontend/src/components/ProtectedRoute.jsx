import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import styles from './ProtectedRoute.module.css'

export default function ProtectedRoute({ roles }) {
  const { user, loading } = useAuth()
  if (loading) return <div className={styles.loading}>Loading...</div>
  if (!user) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user.role)) return <Navigate to="/login" replace />
  return <Outlet />
}