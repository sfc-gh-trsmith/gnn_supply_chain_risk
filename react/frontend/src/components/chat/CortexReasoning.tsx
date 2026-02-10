import { Loader2 } from 'lucide-react'

interface CortexReasoningProps {
  stage: string
}

export function CortexReasoning({ stage }: CortexReasoningProps) {
  return (
    <div className="flex items-center gap-1.5 text-slate-400 text-xs px-2">
      <Loader2 className="w-3 h-3 animate-spin text-sky-400" />
      <span>{stage}</span>
    </div>
  )
}
