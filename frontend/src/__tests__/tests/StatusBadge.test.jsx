import { render, screen } from '@testing-library/react'
import StatusBadge from '../components/StatusBadge'


test('renders correct status text', () => {
    render(<StatusBadge status="approved" />)
    expect(screen.getByText('approved')).toBeInTheDocument()
})

test('replaces underscore with space in status text', () => {
    render(<StatusBadge status="not_started" />)
    expect(screen.getByText('not started')).toBeInTheDocument()
})


test('applies the correct class for rejected status', () => {
    const { container } = render(<StatusBadge status="rejected" />)

    const badge = container.querySelector('span')
    expect(badge).not.toBeNull()
    expect(badge.textContent).toBe('rejected')
})