import { Database, CheckCircle2, Loader2, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import type { ToolCall } from '../../types/cortex'

interface CortexToolProps {
  tool: ToolCall
}

export function CortexTool({ tool }: CortexToolProps) {
  const [expanded, setExpanded] = useState(false)

  const statusIcon = {
    running: <Loader2 className="w-3 h-3 animate-spin text-sky-400" />,
    completed: <CheckCircle2 className="w-3 h-3 text-emerald-400" />,
    error: <AlertCircle className="w-3 h-3 text-red-400" />,
  }[tool.status]

  const toolLabel = {
    SUPPLY_CHAIN_ANALYTICS: 'Querying Data',
    RISK_SCENARIO_ANALYZER: 'Analyzing Scenario',
  }[tool.name] || tool.name

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-2 py-1.5 hover:bg-slate-700/50 transition-colors"
      >
        <div className="flex items-center gap-1.5">
          <Database className="w-3 h-3 text-slate-400" />
          <span className="text-xs text-slate-300">{toolLabel}</span>
          {statusIcon}
        </div>
        {tool.output && (
          expanded ? (
            <ChevronUp className="w-3 h-3 text-slate-400" />
          ) : (
            <ChevronDown className="w-3 h-3 text-slate-400" />
          )
        )}
      </button>

      {expanded && tool.output && (
        <div className="px-2 py-1.5 border-t border-slate-700 bg-slate-900/50">
          {tool.sql && (
            <div className="mb-2">
              <p className="text-xs text-slate-500 mb-1">SQL Query:</p>
              <pre className="text-xs text-slate-400 bg-slate-800 p-2 rounded overflow-x-auto">
                {tool.sql}
              </pre>
            </div>
          )}
          <div>
            <p className="text-xs text-slate-500 mb-1">Result:</p>
            <pre className="text-xs text-slate-400 bg-slate-800 p-2 rounded overflow-x-auto max-h-48">
              {typeof tool.output === 'string' 
                ? tool.output 
                : JSON.stringify(tool.output, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}
