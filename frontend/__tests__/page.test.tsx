import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
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

describe('Page — API interaction', () => {
  beforeEach(() => {
    jest.resetAllMocks()
  })

  it('disables submit when input is empty', () => {
    render(<Page />)
    const button = screen.getByRole('button', { name: /send/i })
    expect(button).toBeDisabled()
  })

  it('enables submit when input has text', async () => {
    render(<Page />)
    const textarea = screen.getByPlaceholderText('Ask a bike repair question...')
    await userEvent.type(textarea, 'How do I bleed brakes?')
    const button = screen.getByRole('button', { name: /send/i })
    expect(button).not.toBeDisabled()
  })

  it('shows error message when fetch fails', async () => {
    ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))
    render(<Page />)
    const textarea = screen.getByPlaceholderText('Ask a bike repair question...')
    await userEvent.type(textarea, 'test question')
    fireEvent.submit(screen.getByRole('button', { name: /send/i }).closest('form')!)
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument()
    })
  })

  it('renders answer and source pills on success', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        question: 'How do I bleed brakes?',
        answer: '## Steps\n1. Install spacer',
        sources: [{ doc_name: 'Dm Gn0001 30 Eng', page: 'p.116', content: 'text' }],
      }),
    })
    render(<Page />)
    const textarea = screen.getByPlaceholderText('Ask a bike repair question...')
    await userEvent.type(textarea, 'How do I bleed brakes?')
    fireEvent.submit(screen.getByRole('button', { name: /send/i }).closest('form')!)
    await waitFor(() => {
      expect(screen.getByText(/Install spacer/)).toBeInTheDocument()
      expect(screen.getByText(/Gn0001 30/)).toBeInTheDocument()
    })
  })
})
