export interface PlannedTask {
  id: number
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
}

export interface Plan {
  goal: string
  assumptions: string[]
  tasks: PlannedTask[]
  confidence: number
}

export interface TaskExecution {
  task_id: number
  title: string
  status: 'completed' | 'failed'
  duration_ms: number
  error: string | null
}

export interface ReflectionReport {
  quality_score: number
  complete: boolean
  issues: string[]
  improved_sections: string[]
  passes: number
}

export interface AgentResponse {
  request: string
  plan: Plan
  execution_summary: {
    total_tasks: number
    completed: number
    failed: number
    duration_ms: number
    reflection: ReflectionReport
  }
  executions: TaskExecution[]
  document_id: string
  document_path: string
  document_url: string
}

export interface DocumentItem {
  id: string
  filename: string
  download_url: string
}

export async function listDocuments(): Promise<DocumentItem[]> {
  const res = await fetch('/api/documents')
  if (!res.ok) return []
  return res.json()
}

export async function runAgent(request: string): Promise<AgentResponse> {
  const res = await fetch('/api/agent', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ request }),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `Request failed (${res.status})`)
  }
  return res.json()
}
