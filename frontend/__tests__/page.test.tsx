import { render, screen } from '@testing-library/react'
import Page from '@/app/page'

// Mock fetch globally
global.fetch = jest.fn()

describe('Page', () => {
  it('renders the title', () => {
    render(<Page />)
    expect(screen.getByText('FixdAI')).toBeInTheDocument()
  })

  it('renders the input placeholder', () => {
    render(<Page />)
    expect(screen.getByPlaceholderText('Ask a bike repair question...')).toBeInTheDocument()
  })

  it('renders the submit button', () => {
    render(<Page />)
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument()
  })
})
