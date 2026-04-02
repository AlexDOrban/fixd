# FixdAI Chat Frontend — Design Spec

**Date:** 2026-04-02  
**Status:** Approved

---

## Overview

A single-page Next.js 14 chat interface that connects to the FixdAI FastAPI backend at `localhost:8000/query`. Users type a bike repair question, submit it, and see the AI answer rendered in markdown with source citations below each response.

---

## Architecture

```
frontend/
├── app/
│   ├── layout.tsx        # Root layout (sets dark bg, font)
│   └── page.tsx          # Single page — all state and UI here
├── package.json
├── tailwind.config.ts
└── next.config.ts
```

Single component, single page. No routing, no state library, no API layer abstraction — just a `fetch` call inside the page component.

---

## State

All state lives in `page.tsx`:

```ts
type Source = { doc_name: string; page: string; content: string }
type Message = { question: string; answer: string; sources: Source[] }

const [messages, setMessages] = useState<Message[]>([])
const [input, setInput]       = useState('')
const [loading, setLoading]   = useState(false)
const [error, setError]       = useState<string | null>(null)
```

---

## Data Flow

1. User types question → updates `input`
2. On submit: set `loading = true`, POST `{ question }` to `http://localhost:8000/query`
3. On success: append `Message` to `messages[]`, clear `input`, set `loading = false`
4. On error: set `error` string, set `loading = false`
5. Auto-scroll to bottom after each new message

---

## UI Layout

```
┌─────────────────────────────────────┐
│  🔧 FixdAI          [title bar]     │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────────────────────┐   │
│  │ How do I bleed brakes?  [you]│   │  ← user bubble (indigo-600, right-aligned)
│  └──────────────────────────────┘   │
│                                     │
│  ┌──────────────────────────────┐   │
│  │ ## Required Tools            │   │  ← AI answer (gray-800, left-aligned)
│  │ - SM-DISC bleeding kit       │   │    rendered as markdown
│  │ ...                          │   │
│  │                              │   │
│  │ 📄 GN0001 General · p.116    │   │  ← source pills (gray-700)
│  │ 📄 GN0001 General · p.117    │   │
│  └──────────────────────────────┘   │
│                                     │
├─────────────────────────────────────┤
│  [Ask a bike repair question...] [→]│  ← sticky input bar
└─────────────────────────────────────┘
```

### Title bar
- Fixed top, `gray-900` background, white "🔧 FixdAI" text

### Message list
- Scrollable, fills available height between title bar and input
- Auto-scrolls to bottom on new message via `useRef` + `useEffect`
- User messages: right-aligned pill bubble, `indigo-600` bg
- AI answers: left-aligned card, `gray-800` bg, markdown rendered via `react-markdown` + `remark-gfm`
- Source citations: row of pills below each AI answer — format: `"GN0001 General · p.116"` — `gray-700` bg, small text

### Input bar
- Sticky bottom, `gray-900` bg
- `<textarea>` (single line, grows to 3 lines max), `Enter` submits, `Shift+Enter` newline
- Submit button disabled + shows spinner while `loading = true`
- Error banner above input bar if `error` is set (dismissible)

---

## Error Handling

- Network error or non-2xx response: set `error` with a human-readable message
- Error banner displayed above the input bar, auto-dismissed on next successful query
- Empty input: submit button disabled (client-side only)

---

## Dependencies

```json
"react-markdown": "^9",
"remark-gfm": "^4"
```

All other dependencies come from `create-next-app` (Next.js 14, Tailwind, TypeScript).

---

## Out of Scope

- Conversation history / multi-turn context (API is stateless)
- Authentication
- Mobile responsiveness beyond basic usability
- Streaming responses
