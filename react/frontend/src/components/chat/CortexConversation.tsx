import { useEffect, useRef } from 'react'
import { useAppStore } from '../../stores/appStore'
import { useCortexAgent } from '../../hooks/useCortexAgent'
import { CortexMessage } from './CortexMessage'
import { CortexPromptInput } from './CortexPromptInput'
import { CortexReasoning } from './CortexReasoning'
import { MessageSquare, X, Trash2 } from 'lucide-react'

export function CortexConversation() {
  const { messages, isChatOpen, setIsChatOpen, clearMessages } = useAppStore()
  const { sendMessage, cancelStream, processPendingPrompt, status, reasoningStage } = useCortexAgent()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    processPendingPrompt()
  }, [processPendingPrompt])

  if (!isChatOpen) {
    return (
      <button
        onClick={() => setIsChatOpen(true)}
        className="fixed bottom-6 right-6 bg-sky-500 hover:bg-sky-600 text-white p-4 rounded-full shadow-lg transition-all z-50"
        title="Open AI Assistant"
      >
        <MessageSquare className="w-6 h-6" />
      </button>
    )
  }

  return (
    <div className="fixed bottom-6 right-6 w-[560px] h-[700px] bg-slate-900 border border-slate-700 rounded-xl shadow-2xl flex flex-col z-50">
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-sky-400" />
          <span className="font-semibold text-slate-200">Supply Chain Copilot</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={clearMessages}
            className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-slate-200"
            title="Clear conversation"
          >
            <Trash2 className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsChatOpen(false)}
            className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-slate-200"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.length === 0 && (
          <div className="text-center text-slate-500 py-8">
            <p className="mb-2 text-sm">Ask me about your supply chain:</p>
            <div className="space-y-1.5 text-xs">
              <button
                onClick={() => sendMessage("What is our overall portfolio risk?")}
                className="block w-full text-left px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300"
              >
                "What is our overall portfolio risk?"
              </button>
              <button
                onClick={() => sendMessage("Which regions have the highest risk?")}
                className="block w-full text-left px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300"
              >
                "Which regions have the highest risk?"
              </button>
              <button
                onClick={() => sendMessage("What are our biggest bottlenecks?")}
                className="block w-full text-left px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300"
              >
                "What are our biggest bottlenecks?"
              </button>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <CortexMessage key={message.id} message={message} />
        ))}

        {reasoningStage && <CortexReasoning stage={reasoningStage} />}

        <div ref={messagesEndRef} />
      </div>

      <CortexPromptInput
        onSubmit={sendMessage}
        onCancel={cancelStream}
        isStreaming={status === 'streaming'}
      />
    </div>
  )
}
