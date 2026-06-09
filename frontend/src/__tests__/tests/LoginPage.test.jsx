import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import LoginPage from '../pages/LoginPage'


test('renders login form with username and password fields', () => {
    render(
        <MemoryRouter>
            <AuthProvider>
                <LoginPage />
            </AuthProvider>
        </MemoryRouter>
    )
  
    expect(screen.getByText('ILES')).toBeInTheDocument()
 
    expect(screen.getByText('Username')).toBeInTheDocument()
    expect(screen.getByText('Password')).toBeInTheDocument()
   
    expect(screen.getByText('Sign In')).toBeInTheDocument()
})


test('displays error message on failed login', async () => {
  
    global.fetch = jest.fn(() =>
        Promise.resolve({ ok: false, status: 401, json: () => Promise.resolve({ detail: 'No active account' }) })
    )

    render(
        <MemoryRouter>
            <AuthProvider>
                <LoginPage />
            </AuthProvider>
        </MemoryRouter>
    )

    fireEvent.change(screen.getByDisplayValue(''), { target: { value: 'wronguser' } })
    fireEvent.click(screen.getByText('Sign In'))

    await waitFor(() => {
        expect(screen.getByText('Invalid username or password.')).toBeInTheDocument()
    })
})