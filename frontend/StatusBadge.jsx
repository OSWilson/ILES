import styles from './StatusBadge.module.css'
export default function StatusBadge({ status }) {
  const label = status?.replace('_', ' ') || ''
  return (
    <span className={`${styles.badge} ${styles[status] || ''}`}>
      {label}
    </span>
  )
}