export interface ToolCall {
  id: string
  name: string
  status: 'running' | 'completed' | 'error'
  output?: string
  sql?: string
}

export interface CortexMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  toolCalls?: ToolCall[]
  isStreaming?: boolean
}

export type AgentStatus = 'idle' | 'streaming' | 'error'

export interface AgentEvent {
  type: 'text_delta' | 'tool_start' | 'tool_end' | 'analyst_result' | 'reasoning' | 'error'
  text?: string
  tool_name?: string
  tool_call_id?: string
  output?: string
  sql?: string
  result?: string
  stage?: string
  message?: string
}
