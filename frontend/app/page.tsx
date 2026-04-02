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
        <h1 className="text-lg font-semibold tracking-tight"><span aria-hidden="true">🔧 </span>FixdAI</h1>
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
