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
