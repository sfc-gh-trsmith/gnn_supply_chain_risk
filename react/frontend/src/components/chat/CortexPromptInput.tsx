import { useState, useRef, useEffect } from 'react'
import { Send, Square } from 'lucide-react'

interface CortexPromptInputProps {
  onSubmit: (message: string) => void
  onCancel: () => void
  isStreaming: boolean
}

export function CortexPromptInput({ onSubmit, onCancel, isStreaming }: CortexPromptInputProps) {
  const [input, setInput] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px'
    }
  }, [input])

  const handleSubmit = () => {
    if (!input.trim() || isStreaming) return
    onSubmit(input.trim())
    setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="border-t border-slate-700 p-2">
      <div className="flex items-end gap-1.5">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about supply chain risk..."
          className="flex-1 bg-slate-800 border border-slate-600 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 placeholder-slate-500 resize-none focus:outline-none focus:border-sky-500 min-h-[32px]"
          rows={1}
          disabled={isStreaming}
        />
        {isStreaming ? (
          <button
            onClick={onCancel}
            className="p-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors"
            title="Stop"
          >
            <Square className="w-3.5 h-3.5" />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!input.trim()}
            className="p-2 bg-sky-600 hover:bg-sky-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg transition-colors"
            title="Send"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </div>
  )
}
