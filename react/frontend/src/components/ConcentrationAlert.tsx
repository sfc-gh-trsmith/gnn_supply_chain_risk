import { AlertTriangle } from 'lucide-react'
import type { Bottleneck } from '../types'

interface ConcentrationAlertProps {
  bottleneck: Bottleneck
  onAnalyze?: () => void
}

export function ConcentrationAlert({ bottleneck, onAnalyze }: ConcentrationAlertProps) {
  return (
    <div className="bg-red-900/20 border border-red-600 rounded-lg p-4">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="font-semibold text-red-400">Critical Concentration Risk</h3>
          <p className="text-sm text-slate-300 mt-1">
            <span className="font-mono text-red-300">{bottleneck.node_id}</span> is a single point of failure 
            affecting <span className="font-bold text-white">{bottleneck.dependent_count}</span> downstream vendors.
          </p>
          {bottleneck.description && (
            <p className="text-sm text-slate-400 mt-2">{bottleneck.description}</p>
          )}
          <div className="flex items-center gap-4 mt-3">
            <span className="text-xs text-slate-500">
              Impact Score: <span className="text-red-400 font-medium">{(bottleneck.impact_score * 100).toFixed(0)}%</span>
            </span>
            <span className="text-xs px-2 py-0.5 bg-red-600/30 text-red-300 rounded">
              {bottleneck.mitigation_status}
            </span>
            {onAnalyze && (
              <button
                onClick={onAnalyze}
                className="ml-auto text-xs px-3 py-1.5 bg-sky-600 hover:bg-sky-500 text-white rounded transition-colors"
              >
                Ask AI About This
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
