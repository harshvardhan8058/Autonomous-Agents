const STAGES = ['Prompt', 'Plan', 'Execute', 'Reflect', 'Document'] as const

export function WorkflowRail({
  active,
  done,
}: {
  active: number
  done: boolean
}) {
  return (
    <nav aria-label="Agent workflow" className="glass rounded-2xl px-5 py-4">
      <ol className="flex items-center justify-between gap-2">
        {STAGES.map((stage, i) => {
          const state = done || i < active ? 'done' : i === active ? 'active' : 'idle'
          return (
            <li key={stage} className="flex flex-1 items-center gap-2 last:flex-none">
              <span className="flex items-center gap-2">
                <span
                  aria-hidden="true"
                  className={
                    state === 'done'
                      ? 'size-2.5 rounded-full bg-accent'
                      : state === 'active'
                        ? 'size-2.5 rounded-full bg-accent animate-pulse-dot'
                        : 'size-2.5 rounded-full bg-muted/40'
                  }
                />
                <span
                  className={
                    'text-xs font-medium tracking-wide ' +
                    (state === 'idle' ? 'text-muted' : 'text-foreground')
                  }
                >
                  {stage}
                </span>
              </span>
              {i < STAGES.length - 1 && (
                <span
                  aria-hidden="true"
                  className={
                    'h-px flex-1 ' +
                    (done || i < active ? 'bg-accent/50' : 'bg-border-glass')
                  }
                />
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}

export function Card({
  title,
  badge,
  children,
}: {
  title: string
  badge?: string
  children: React.ReactNode
}) {
  return (
    <section className="glass animate-rise rounded-2xl p-6">
      <header className="mb-4 flex items-center justify-between gap-4">
        <h2 className="text-sm font-semibold tracking-widest text-muted uppercase">
          {title}
        </h2>
        {badge && (
          <span className="rounded-full bg-accent-dim px-3 py-1 font-mono text-xs text-accent">
            {badge}
          </span>
        )}
      </header>
      {children}
    </section>
  )
}
