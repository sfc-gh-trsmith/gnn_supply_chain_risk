import ReactMarkdown from 'react-markdown'
import { User, Bot, Loader2 } from 'lucide-react'
import type { CortexMessage as MessageType } from '../../types/cortex'
import { CortexTool } from './CortexTool'

interface CortexMessageProps {
  message: MessageType
}

export function CortexMessage({ message }: CortexMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-2 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? 'bg-sky-600' : 'bg-slate-700'
        }`}
      >
        {isUser ? (
          <User className="w-3 h-3 text-white" />
        ) : (
          <Bot className="w-3 h-3 text-sky-400" />
        )}
      </div>

      <div
        className={`max-w-[90%] ${
          isUser
            ? 'bg-sky-600 text-white rounded-2xl rounded-tr-sm px-3 py-1.5 text-sm'
            : 'space-y-1.5'
        }`}
      >
        {isUser ? (
          <p className="text-sm">{message.content}</p>
        ) : (
          <>
            {message.toolCalls?.map((tool) => (
              <CortexTool key={tool.id} tool={tool} />
            ))}

            {message.content && (
              <div className="bg-slate-800 rounded-2xl rounded-tl-sm px-3 py-2">
                <div className="prose prose-xs prose-invert max-w-none prose-p:my-0.5 prose-p:text-[13px] prose-p:leading-relaxed prose-ul:my-0.5 prose-ul:text-[13px] prose-li:my-0 prose-code:text-xs prose-code:bg-slate-700/50 prose-headings:text-sm prose-headings:my-1">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
              </div>
            )}

            {message.isStreaming && !message.content && (
              <div className="flex items-center gap-2 text-slate-400 text-xs">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Thinking...</span>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
