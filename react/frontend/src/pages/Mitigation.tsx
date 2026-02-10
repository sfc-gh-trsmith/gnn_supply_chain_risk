import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { useAppStore } from '../stores/appStore'
import { Loader2, Shield, CheckCircle, Clock, AlertTriangle } from 'lucide-react'

export function Mitigation() {
  const { data: bottlenecks, isLoading } = useQuery({
    queryKey: ['risk', 'bottlenecks'],
    queryFn: api.risk.bottlenecks,
  })

  const { setPendingPrompt, setChatContext, setIsChatOpen } = useAppStore()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-sky-400" />
      </div>
    )
  }

  const statusCounts = {
    unmitigated: bottlenecks?.filter(b => b.mitigation_status === 'UNMITIGATED').length || 0,
    in_progress: bottlenecks?.filter(b => b.mitigation_status === 'IN_PROGRESS').length || 0,
    mitigated: bottlenecks?.filter(b => b.mitigation_status === 'MITIGATED').length || 0,
  }

  const handleGetSuggestions = (nodeId: string) => {
    const bn = bottlenecks?.find(b => b.node_id === nodeId)
    if (bn) {
      setChatContext(`User is in mitigation tracking view, looking at bottleneck "${bn.node_id}" with ${bn.dependent_count} dependents.`)
      setPendingPrompt(`Generate a detailed mitigation plan for bottleneck "${bn.node_id}" including:\n1. Immediate actions (this week)\n2. Short-term strategies (this month)\n3. Long-term resilience improvements`)
      setIsChatOpen(true)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Risk Mitigation</h1>
        <p className="text-slate-400 mt-1">Track and manage bottleneck remediation actions</p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-red-900/20 border border-red-600 rounded-lg p-4 flex items-center gap-4">
          <AlertTriangle className="w-8 h-8 text-red-500" />
          <div>
            <p className="text-2xl font-bold text-red-400">{statusCounts.unmitigated}</p>
            <p className="text-sm text-slate-400">Unmitigated</p>
          </div>
        </div>
        <div className="bg-amber-900/20 border border-amber-600 rounded-lg p-4 flex items-center gap-4">
          <Clock className="w-8 h-8 text-amber-500" />
          <div>
            <p className="text-2xl font-bold text-amber-400">{statusCounts.in_progress}</p>
            <p className="text-sm text-slate-400">In Progress</p>
          </div>
        </div>
        <div className="bg-emerald-900/20 border border-emerald-600 rounded-lg p-4 flex items-center gap-4">
          <CheckCircle className="w-8 h-8 text-emerald-500" />
          <div>
            <p className="text-2xl font-bold text-emerald-400">{statusCounts.mitigated}</p>
            <p className="text-sm text-slate-400">Mitigated</p>
          </div>
        </div>
      </div>

      <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-700 flex items-center justify-between">
          <h3 className="font-medium text-slate-200">Bottleneck Action Items</h3>
          <span className="text-xs text-slate-400">{bottlenecks?.length} total</span>
        </div>
        
        <div className="divide-y divide-slate-700/50">
          {bottlenecks?.map((bn) => (
            <div key={bn.bottleneck_id} className="p-4 hover:bg-slate-700/30 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <Shield className="w-5 h-5 text-slate-400" />
                    <h4 className="font-medium text-slate-200">{bn.node_id}</h4>
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      bn.mitigation_status === 'UNMITIGATED' ? 'bg-red-600/30 text-red-300' :
                      bn.mitigation_status === 'IN_PROGRESS' ? 'bg-amber-600/30 text-amber-300' :
                      'bg-emerald-600/30 text-emerald-300'
                    }`}>
                      {bn.mitigation_status}
                    </span>
                  </div>
                  <p className="text-sm text-slate-400 mt-1 ml-8">
                    {bn.dependent_count} dependent vendors | Impact: {(bn.impact_score * 100).toFixed(0)}%
                  </p>
                  {bn.description && (
                    <p className="text-sm text-slate-500 mt-1 ml-8">{bn.description}</p>
                  )}
                </div>
                <button
                  onClick={() => handleGetSuggestions(bn.node_id)}
                  className="px-3 py-1.5 bg-sky-600/20 hover:bg-sky-600/40 text-sky-400 text-sm rounded-lg transition-colors"
                >
                  Get AI Suggestions
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
