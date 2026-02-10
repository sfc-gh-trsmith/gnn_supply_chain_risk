import { useCallback, useState, useRef } from 'react'
import { useAppStore } from '../stores/appStore'
import type { CortexMessage, ToolCall, AgentStatus } from '../types/cortex'

export function useCortexAgent() {
  const [status, setStatus] = useState<AgentStatus>('idle')
  const [reasoningStage, setReasoningStage] = useState<string | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)
  const processingPromptRef = useRef<string | null>(null)
  
  const { messages, addMessage, updateMessage, pendingPrompt, setPendingPrompt, chatContext } = useAppStore()

  const sendMessage = useCallback(async (content: string) => {
    if (processingPromptRef.current === content) return
    processingPromptRef.current = content

    const userMessage: CortexMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date(),
    }
    addMessage(userMessage)

    const assistantId = crypto.randomUUID()
    const assistantMessage: CortexMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      toolCalls: [],
      isStreaming: true,
    }
    addMessage(assistantMessage)

    setStatus('streaming')
    setReasoningStage('Connecting...')

    abortControllerRef.current = new AbortController()

    try {
      const response = await fetch('/api/agent/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: content,
          context: chatContext || undefined
        }),
        signal: abortControllerRef.current.signal,
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''
      let fullContent = ''
      const toolCalls: ToolCall[] = []

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const data = line.slice(6).trim()
          if (data === '[DONE]') continue

          try {
            const event = JSON.parse(data)

            switch (event.type) {
              case 'text_delta':
                fullContent += event.text
                updateMessage(assistantId, { content: fullContent })
                setReasoningStage(null)
                break

              case 'tool_start':
                setReasoningStage(`Using ${event.tool_name}...`)
                toolCalls.push({
                  id: event.tool_call_id || crypto.randomUUID(),
                  name: event.tool_name,
                  status: 'running',
                })
                updateMessage(assistantId, { toolCalls: [...toolCalls] })
                break

              case 'tool_end':
                const idx = toolCalls.findIndex(
                  (t) => t.name === event.tool_name && t.status === 'running'
                )
                if (idx >= 0) {
                  toolCalls[idx] = {
                    ...toolCalls[idx],
                    status: 'completed',
                    output: event.output,
                  }
                }
                updateMessage(assistantId, { toolCalls: [...toolCalls] })
                setReasoningStage(null)
                break

              case 'analyst_result':
                const analystIdx = toolCalls.findIndex(
                  (t) => t.name === 'SUPPLY_CHAIN_ANALYTICS' && t.status === 'running'
                )
                if (analystIdx >= 0) {
                  toolCalls[analystIdx] = {
                    ...toolCalls[analystIdx],
                    status: 'completed',
                    sql: event.sql,
                    output: event.result,
                  }
                  updateMessage(assistantId, { toolCalls: [...toolCalls] })
                }
                break

              case 'reasoning':
                setReasoningStage(event.stage)
                break

              case 'error':
                throw new Error(event.message)
            }
          } catch (e) {
            if (!(e instanceof SyntaxError)) throw e
          }
        }
      }

      updateMessage(assistantId, { isStreaming: false })
      setStatus('idle')
      setReasoningStage(null)

    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        updateMessage(assistantId, { 
          content: '_Message cancelled._',
          isStreaming: false 
        })
      } else {
        updateMessage(assistantId, {
          content: `Error: ${(error as Error).message}. Please try again.`,
          isStreaming: false,
        })
      }
      setStatus('error')
      setReasoningStage(null)
    } finally {
      processingPromptRef.current = null
    }
  }, [addMessage, updateMessage, chatContext])

  const cancelStream = useCallback(() => {
    abortControllerRef.current?.abort()
  }, [])

  const processPendingPrompt = useCallback(() => {
    if (pendingPrompt && status !== 'streaming' && processingPromptRef.current !== pendingPrompt) {
      const prompt = pendingPrompt
      setPendingPrompt(null)
      sendMessage(prompt)
    }
  }, [pendingPrompt, status, setPendingPrompt, sendMessage])

  return {
    messages,
    sendMessage,
    cancelStream,
    processPendingPrompt,
    status,
    reasoningStage,
  }
}
