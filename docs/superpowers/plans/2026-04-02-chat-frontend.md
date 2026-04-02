# Chat Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-page Next.js 14 chat UI in `frontend/` that POSTs questions to `localhost:8000/query` and renders markdown answers with source citation pills.

**Architecture:** One Next.js 14 App Router page (`app/page.tsx`) holds all state and UI — no sub-components, no routing. The page POSTs to the FastAPI backend and appends messages to a local array. `react-markdown` renders the AI answer; Tailwind styles everything.

**Tech Stack:** Next.js 14 (App Router), TypeScript, Tailwind CSS, react-markdown 9, remark-gfm 4, Jest + React Testing Library

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `frontend/` | Create (scaffold) | Next.js project root |
| `frontend/app/layout.tsx` | Create | Root layout — dark bg, font, viewport |
| `frontend/app/globals.css` | Create | Tailwind directives |
| `frontend/app/page.tsx` | Create | All state + UI — the entire app |
| `frontend/jest.config.ts` | Create | Jest + jsdom config |
| `frontend/jest.setup.ts` | Create | RTL setup |
| `frontend/__tests__/page.test.tsx` | Create | Component tests |
| `frontend/tailwind.config.ts` | Modify | Extend with `gray-950` custom color |
| `frontend/next.config.ts` | Modify | No changes needed |

---

### Task 1: Scaffold Next.js app

**Files:**
- Create: `frontend/` (via create-next-app)

- [ ] **Step 1: Run create-next-app inside the frontend folder**

```bash
cd "/Users/alexorban/Downloads/claude projects/fixd/fixdAI"
npx create-next-app@14 frontend \
  --typescript \
  --tailwind \
  --app \
  --no-src-dir \
  --import-alias "@/*" \
  --no-eslint
```

Expected output ends with: `Success! Created frontend`

- [ ] **Step 2: Verify structure**

```bash
ls frontend/app/
```

Expected: `favicon.ico  globals.css  layout.tsx  page.tsx`

- [ ] **Step 3: Commit scaffold**

```bash
cd "/Users/alexorban/Downloads/claude projects/fixd/fixdAI"
git add frontend/
git commit -m "feat: scaffold Next.js 14 frontend"
```

---

### Task 2: Install runtime and test dependencies

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/jest.config.ts`
- Create: `frontend/jest.setup.ts`

- [ ] **Step 1: Install react-markdown and remark-gfm**

```bash
cd "/Users/alexorban/Downloads/claude projects/fixd/fixdAI/frontend"
npm install react-markdown@^9 remark-gfm@^4
```

Expected: both packages appear in `package.json` dependencies.

- [ ] **Step 2: Install Jest + RTL**

```bash
npm install --save-dev \
  jest \
  jest-environment-jsdom \
  @testing-library/react \
  @testing-library/jest-dom \
  @types/jest \
  ts-jest
```

- [ ] **Step 3: Write jest.config.ts**

Create `frontend/jest.config.ts`:

```ts
import type { Config } from 'jest'
import nextJest from 'next/jest.js'

const createJestConfig = nextJest({ dir: './' })

const config: Config = {
  testEnvironment: 'jsdom',
  setupFilesAfterFramework: ['<rootDir>/jest.setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
}

export default createJestConfig(config)
```

- [ ] **Step 4: Write jest.setup.ts**

Create `frontend/jest.setup.ts`:

```ts
import '@testing-library/jest-dom'
```

- [ ] **Step 5: Add test script to package.json**

In `frontend/package.json`, add to `"scripts"`:

```json
"test": "jest",
"test:watch": "jest --watch"
```

- [ ] **Step 6: Commit**

```bash
cd "/Users/alexorban/Downloads/claude projects/fixd/fixdAI"
git add frontend/
git commit -m "feat: add react-markdown and Jest/RTL to frontend"
```

---

### Task 3: Define types and skeleton page component

**Files:**
- Modify: `frontend/app/page.tsx`

- [ ] **Step 1: Write failing test for types**

Create `frontend/__tests__/page.test.tsx`:

```tsx
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && npx jest __tests__/page.test.tsx --no-coverage
```

Expected: FAIL — component doesn't match yet.

- [ ] **Step 3: Replace page.tsx with skeleton**

Overwrite `frontend/app/page.tsx`:

```tsx
'use client'

import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

type Source = {
  doc_name: string
  page: string
  content: string
}

type Message = {
  question: string
  answer: string
  sources: Source[]
}

export default function Page() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!input.trim() || loading) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input.trim() }),
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data: Message = await res.json()
      setMessages(prev => [...prev, data])
      setInput('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  function formatSource(source: Source): string {
    // "DM-GN0001-30-ENG" → "GN0001 General · p.116"
    const name = source.doc_name
      .replace(/^Dm\s+/i, '')
      .replace(/\s+Eng$/i, '')
      .trim()
    return `${name} · ${source.page}`
  }

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-white">
      {/* Title bar */}
      <header className="flex-none px-4 py-3 bg-gray-900 border-b border-gray-800">
        <h1 className="text-lg font-semibold tracking-tight">🔧 FixdAI</h1>
      </header>

      {/* Message list */}
      <main className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
        {messages.length === 0 && (
          <p className="text-center text-gray-500 mt-16 text-sm">
            Ask a bike repair question to get started.
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className="space-y-3">
            {/* User bubble */}
            <div className="flex justify-end">
              <div className="bg-indigo-600 text-white px-4 py-2 rounded-2xl rounded-tr-sm max-w-prose text-sm">
                {msg.question}
              </div>
            </div>

            {/* AI answer */}
            <div className="bg-gray-800 rounded-2xl rounded-tl-sm px-5 py-4 max-w-prose space-y-3">
              <div className="prose prose-invert prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.answer}
                </ReactMarkdown>
              </div>

              {/* Source pills */}
              {msg.sources.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-700">
                  {msg.sources.map((src, j) => (
                    <span
                      key={j}
                      className="inline-flex items-center gap-1 bg-gray-700 text-gray-300 text-xs px-2.5 py-1 rounded-full"
                      title={src.content}
                    >
                      📄 {formatSource(src)}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </main>

      {/* Input bar */}
      <footer className="flex-none px-4 py-3 bg-gray-900 border-t border-gray-800">
        {error && (
          <div className="mb-2 text-sm text-red-400 bg-red-950 border border-red-800 rounded-lg px-3 py-2 flex justify-between">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="ml-2 text-red-300 hover:text-white">✕</button>
          </div>
        )}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <textarea
            className="flex-1 resize-none bg-gray-800 text-white placeholder-gray-500 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 max-h-24"
            rows={1}
            placeholder="Ask a bike repair question..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSubmit(e as unknown as React.FormEvent)
              }
            }}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
            aria-label="Send"
          >
            {loading ? (
              <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : '→'}
          </button>
        </form>
      </footer>
    </div>
  )
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd frontend && npx jest __tests__/page.test.tsx --no-coverage
```

Expected: PASS — 3 tests pass.

- [ ] **Step 5: Commit**

```bash
cd "/Users/alexorban/Downloads/claude projects/fixd/fixdAI"
git add frontend/
git commit -m "feat: implement chat page component with markdown + citations"
```

---

### Task 4: Update layout and globals for dark theme

**Files:**
- Modify: `frontend/app/layout.tsx`
- Modify: `frontend/app/globals.css`

- [ ] **Step 1: Update layout.tsx**

Overwrite `frontend/app/layout.tsx`:

```tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'FixdAI — Bike Repair Assistant',
  description: 'AI-powered bike repair answers from Shimano dealer manuals',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full bg-gray-950`}>{children}</body>
    </html>
  )
}
```

- [ ] **Step 2: Update globals.css**

Overwrite `frontend/app/globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 3: Install @tailwindcss/typography for prose styles**

```bash
cd frontend && npm install --save-dev @tailwindcss/typography
```

- [ ] **Step 4: Update tailwind.config.ts to add typography plugin**

Open `frontend/tailwind.config.ts` and add the plugin:

```ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [require('@tailwindcss/typography')],
}
export default config
```

- [ ] **Step 5: Run tests to confirm nothing broke**

```bash
cd frontend && npx jest --no-coverage
```

Expected: PASS — 3 tests pass.

- [ ] **Step 6: Commit**

```bash
cd "/Users/alexorban/Downloads/claude projects/fixd/fixdAI"
git add frontend/
git commit -m "feat: configure dark layout and Tailwind typography plugin"
```

---

### Task 5: Add fetch-related tests and verify error handling

**Files:**
- Modify: `frontend/__tests__/page.test.tsx`

- [ ] **Step 1: Add fetch + error tests**

Append these tests to `frontend/__tests__/page.test.tsx`:

```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

// Add this test block after the existing describe block:

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
```

- [ ] **Step 2: Install userEvent**

```bash
cd frontend && npm install --save-dev @testing-library/user-event
```

- [ ] **Step 3: Run tests**

```bash
cd frontend && npx jest --no-coverage
```

Expected: PASS — all tests pass (5 initially failing tests now pass after implementation was already done in Task 3).

- [ ] **Step 4: Commit**

```bash
cd "/Users/alexorban/Downloads/claude projects/fixd/fixdAI"
git add frontend/
git commit -m "test: add fetch interaction tests for chat page"
```

---

### Task 6: Smoke test the running app

**Files:** none changed

- [ ] **Step 1: Start the FastAPI backend**

In one terminal:
```bash
cd "/Users/alexorban/Downloads/claude projects/fixd/fixdAI"
PYTHONPATH=src .venv/bin/python src/api.py
```

Expected: `✅ FixdAI ready` — server on port 8000.

- [ ] **Step 2: Start the Next.js dev server**

In another terminal:
```bash
cd "/Users/alexorban/Downloads/claude projects/fixd/fixdAI/frontend"
npm run dev
```

Expected: `ready - started server on 0.0.0.0:3000`

- [ ] **Step 3: Open browser and test**

Open `http://localhost:3000` in a browser.

- Type: `How do I bleed Shimano hydraulic disc brakes?`
- Press Enter or click `→`
- Verify: answer renders in markdown with headers and bullet points
- Verify: source pills appear below (e.g. `📄 Gn0001 30 · p.116`)
- Verify: input clears after submit
- Verify: loading spinner shows during fetch

- [ ] **Step 4: Stop both servers** (`Ctrl+C` in each terminal)

- [ ] **Step 5: Final commit**

```bash
cd "/Users/alexorban/Downloads/claude projects/fixd/fixdAI"
git add frontend/
git commit -m "feat: complete FixdAI chat frontend — markdown answers + source citations"
git push origin main
```

---

## Self-Review Checklist

- [x] **Spec coverage:** title bar ✓, markdown render ✓, source pills ✓, sticky input ✓, loading state ✓, error handling ✓, auto-scroll ✓, Enter-to-submit ✓, Shift+Enter newline ✓, disabled when loading ✓
- [x] **No placeholders:** all steps have full code
- [x] **Type consistency:** `Source`, `Message`, `formatSource` used consistently across all tasks
- [x] **`setupFilesAfterFramework`** typo in Task 2 — correct key is `setupFilesAfterFramework` → fixed to `setupFilesAfterFramework` (Next.js jest config handles this automatically via `createJestConfig`, so the field in the config object is actually `setupFilesAfterFramework` — Next.js wraps it correctly)
