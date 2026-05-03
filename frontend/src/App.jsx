
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './context/AuthContext'
import { ToastProvider } from './context/ToastContext'
import ProtectedRoute from './components/ProtectedRoute'

import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'

import StudentDashboard from './pages/student/Dashboard'
import LogList from './pages/student/LogList'
import LogForm from './pages/student/LogForm'

import WorkplaceDashboard from './pages/workplace/Dashboard'

import AcademicDashboard from './pages/academic/Dashboard'
import EvaluationDetail from './pages/academic/EvaluationDetail'

import AdminDashboard from './pages/admin/Dashboard'

const qc = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <AuthProvider>
        <ToastProvider>
          <BrowserRouter>
            <Routes>
              {/* Public */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              {/* Student */}
              <Route element={<ProtectedRoute roles={['student']} />}>
                <Route path="/student/dashboard" element={<StudentDashboard />} />
                <Route path="/student/logs" element={<LogList />} />
                <Route path="/student/logs/new" element={<LogForm />} />
                <Route path="/student/logs/:id/edit" element={<LogForm />} />
                <Route path="/profile" element={<ProfilePage />} />
              </Route>

              {/* Workplace */}
              <Route element={<ProtectedRoute roles={['workplace']} />}>
                <Route path="/workplace/dashboard" element={<WorkplaceDashboard />} />
                <Route path="/profile" element={<ProfilePage />} />
              </Route>

              {/* Academic */}
              <Route element={<ProtectedRoute roles={['academic']} />}>
                <Route path="/academic/dashboard" element={<AcademicDashboard />} />
                <Route path="/academic/evaluations/:id" element={<EvaluationDetail />} />
                <Route path="/profile" element={<ProfilePage />} />
              </Route>

              {/* Admin */}
              <Route element={<ProtectedRoute roles={['admin']} />}>
                <Route path="/admin/dashboard" element={<AdminDashboard />} />
                <Route path="/profile" element={<ProfilePage />} />
              </Route>

              <Route path="/" element={<Navigate to="/login" replace />} />
            </Routes>
          </BrowserRouter>
        </ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}