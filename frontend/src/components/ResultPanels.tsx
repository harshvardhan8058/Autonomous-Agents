import type { AgentResponse } from '../lib/api'
import { Card } from './Workflow'

const PRIORITY_STYLE: Record<string, string> = {
  high: 'text-accent',
  medium: 'text-foreground/80',
  low: 'text-muted',
}

export function PlanPanel({ plan }: { plan: AgentResponse['plan'] }) {
  return (
    <Card title="Generated Plan" badge={`confidence ${(plan.confidence * 100).toFixed(0)}%`}>
      <p className="mb-4 text-sm leading-relaxed text-foreground/90 text-pretty">{plan.goal}</p>
      <ol className="flex flex-col gap-2">
        {plan.tasks.map((task) => (
          <li key={task.id} className="flex items-baseline gap-3 rounded-lg bg-background/40 px-4 py-3">
            <span className="font-mono text-xs text-muted">{String(task.id).padStart(2, '0')}</span>
            <div className="flex flex-col gap-0.5">
              <span className="text-sm font-medium">{task.title}</span>
              <span className="text-xs leading-relaxed text-muted">{task.description}</span>
            </div>
            <span className={'ml-auto text-xs font-medium ' + (PRIORITY_STYLE[task.priority] ?? 'text-muted')}>
              {task.priority}
            </span>
          </li>
        ))}
      </ol>
      {plan.assumptions.length > 0 && (
        <p className="mt-4 text-xs leading-relaxed text-muted">
          Assumptions: {plan.assumptions.join(' · ')}
        </p>
      )}
    </Card>
  )
}

export function ExecutionPanel({ result }: { result: AgentResponse }) {
  const { execution_summary: summary, executions } = result
  return (
    <Card
      title="Execution"
      badge={`${summary.completed}/${summary.total_tasks} tasks · ${(summary.duration_ms / 1000).toFixed(1)}s`}
    >
      <ul className="flex flex-col gap-2">
        {executions.map((execution) => (
          <li key={execution.task_id} className="flex items-center gap-3 rounded-lg bg-background/40 px-4 py-2.5">
            <span
              aria-hidden="true"
              className={
                'size-2 rounded-full ' +
                (execution.status === 'completed' ? 'bg-accent' : 'bg-danger')
              }
            />
            <span className="text-sm">{execution.title}</span>
            <span className="ml-auto font-mono text-xs text-muted">
              {execution.status === 'completed'
                ? `${(execution.duration_ms / 1000).toFixed(1)}s`
                : 'failed'}
            </span>
          </li>
        ))}
      </ul>
    </Card>
  )
}

export function ReflectionPanel({
  reflection,
}: {
  reflection: AgentResponse['execution_summary']['reflection']
}) {
  return (
    <Card
      title="Reflection & Self-Check"
      badge={`quality ${(reflection.quality_score * 100).toFixed(0)}%`}
    >
      <p className="text-sm leading-relaxed text-foreground/90">
        {reflection.complete
          ? 'The agent reviewed its output and judged the document complete.'
          : 'The agent flagged the document as incomplete after review.'}
        {reflection.passes > 0 &&
          ` One improvement pass rewrote ${reflection.improved_sections.length} section(s): ${reflection.improved_sections.join(', ')}.`}
      </p>
      {reflection.issues.length > 0 && (
        <ul className="mt-3 flex flex-col gap-1.5">
          {reflection.issues.map((issue) => (
            <li key={issue} className="flex items-baseline gap-2 text-xs leading-relaxed text-muted">
              <span aria-hidden="true" className="text-accent">
                —
              </span>
              {issue}
            </li>
          ))}
        </ul>
      )}
    </Card>
  )
}

export function DownloadPanel({ result }: { result: AgentResponse }) {
  return (
    <Card title="Document">
      <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-col gap-1">
          <span className="font-mono text-xs break-all text-muted">{result.document_id}.docx</span>
          <span className="text-xs text-muted">Professional DOCX with TOC, executive summary, timeline table, and footer.</span>
        </div>
        <a
          href={result.document_url}
          download
          className="rounded-xl bg-accent px-6 py-3 text-sm font-semibold text-background transition-transform hover:scale-[1.03] active:scale-[0.98]"
        >
          Download DOCX
        </a>
      </div>
    </Card>
  )
}
