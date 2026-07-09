import { useEffect, useRef, useState } from 'react'
import { runAgent, listDocuments, type AgentResponse, type DocumentItem } from './lib/api'
import { Card, WorkflowRail } from './components/Workflow'
import {
  DownloadPanel,
  ExecutionPanel,
  PlanPanel,
  ReflectionPanel,
} from './components/ResultPanels'

const EXAMPLE = 'Create a technical proposal for migrating a monolith to microservices'

// Indicative stage pacing while the single agent request is in flight.
const STAGE_TIMINGS_MS = [1500, 9000, 22000]

export default function App() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [stage, setStage] = useState(0)
  const [result, setResult] = useState<AgentResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [pastDocs, setPastDocs] = useState<DocumentItem[]>([])
  const timersRef = useRef<number[]>([])

  // Load past documents on mount and after each successful run
  function refreshDocs() {
    listDocuments().then(setPastDocs).catch(() => {})
  }
  useEffect(() => { refreshDocs() }, [])

  useEffect(() => () => timersRef.current.forEach(clearTimeout), [])

  async function submit() {
    const request = prompt.trim()
    if (!request || loading) return
    setLoading(true)
    setResult(null)
    setError(null)
    setStage(1)
    timersRef.current = STAGE_TIMINGS_MS.map((ms, i) =>
      window.setTimeout(() => setStage(i + 2), ms),
    )
    try {
      const res = await runAgent(request)
      setResult(res)
      refreshDocs()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      timersRef.current.forEach(clearTimeout)
      setLoading(false)
    }
  }

  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-3xl flex-col gap-6 px-4 py-10 md:py-16">
      <header className="flex flex-col gap-2 text-center">
        <p className="font-mono text-xs tracking-widest text-accent uppercase">
          Autonomous AI Agent
        </p>
        <h1 className="text-3xl font-bold text-balance md:text-4xl">
          Plan. Execute. Reflect. Deliver.
        </h1>
        <p className="mx-auto max-w-xl text-sm leading-relaxed text-muted text-pretty">
          Describe what you need. The agent builds its own execution plan, writes
          each section, reviews its own work, and hands you a professional DOCX.
        </p>
      </header>

      <WorkflowRail active={loading ? stage : 0} done={result !== null} />

      <section className="glass animate-rise rounded-2xl p-5">
        <label htmlFor="prompt" className="sr-only">
          Describe the document you need
        </label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => {
            if (
              e.key === 'Enter' &&
              !e.shiftKey &&
              !e.nativeEvent.isComposing &&
              e.keyCode !== 229
            ) {
              e.preventDefault()
              submit()
            }
          }}
          placeholder={EXAMPLE}
          rows={3}
          disabled={loading}
          className="w-full resize-none bg-transparent text-sm leading-relaxed placeholder:text-muted/60 focus:outline-none disabled:opacity-60"
        />
        <div className="mt-3 flex items-center justify-between gap-4">
          <button
            type="button"
            onClick={() => setPrompt(EXAMPLE)}
            disabled={loading}
            className="text-xs text-muted transition-colors hover:text-foreground disabled:opacity-50"
          >
            Try an example
          </button>
          <button
            type="button"
            onClick={submit}
            disabled={loading || prompt.trim().length < 3}
            className="rounded-xl bg-accent px-6 py-2.5 text-sm font-semibold text-background transition-all hover:scale-[1.03] active:scale-[0.98] disabled:scale-100 disabled:opacity-40"
          >
            {loading ? 'Agent working…' : 'Run Agent'}
          </button>
        </div>
      </section>

      {loading && (
        <Card title="Live Status" badge="running">
          <p className="flex items-center gap-3 text-sm text-muted">
            <span aria-hidden="true" className="size-2 rounded-full bg-accent animate-pulse-dot" />
            {stage <= 1 && 'Planner is decomposing your request into tasks…'}
            {stage === 2 && 'Executor is writing each section sequentially…'}
            {stage >= 3 && 'Reflection pass — the agent is reviewing its own work…'}
          </p>
        </Card>
      )}

      {error && (
        <Card title="Error">
          <p className="text-sm leading-relaxed text-danger">{error}</p>
        </Card>
      )}

      {result && (
        <>
          <PlanPanel plan={result.plan} />
          <ExecutionPanel result={result} />
          <ReflectionPanel reflection={result.execution_summary.reflection} />
          <DownloadPanel result={result} />
        </>
      )}

      {pastDocs.length > 0 && (
        <section className="glass animate-rise rounded-2xl p-5">
          <h2 className="mb-3 text-sm font-semibold text-foreground">Previous Documents</h2>
          <ul className="flex flex-col gap-2">
            {pastDocs.map((doc) => (
              <li key={doc.id} className="flex items-center justify-between gap-3">
                <span className="truncate font-mono text-xs text-muted">{doc.filename}</span>
                <button
                  type="button"
                  onClick={async () => {
                    const res = await fetch(doc.download_url)
                    if (!res.ok) return
                    const blob = await res.blob()
                    const a = document.createElement('a')
                    a.href = URL.createObjectURL(blob)
                    a.download = doc.filename
                    document.body.appendChild(a)
                    a.click()
                    a.remove()
                  }}
                  className="shrink-0 rounded-lg border border-border px-3 py-1 text-xs transition-colors hover:bg-accent hover:text-background"
                >
                  Download
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      <footer className="mt-auto pt-6 text-center text-xs text-muted">
        Single-agent pipeline · FastAPI + Groq llama-3.3-70b · Reflection with one bounded improvement pass
      </footer>
    </main>
  )
}
