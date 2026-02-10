import { useQuery } from '@tanstack/react-query'
import { KPICard, HealthGauge, RegionalHeatmap, ConcentrationAlert } from '../components'
import { api } from '../lib/api'
import { useAppStore } from '../stores/appStore'
import { Loader2, TrendingUp, AlertTriangle, Network, Link2 } from 'lucide-react'

export function Executive() {
  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['metrics', 'executive'],
    queryFn: api.metrics.executive,
  })

  const { data: regional, isLoading: regionalLoading } = useQuery({
    queryKey: ['metrics', 'regional'],
    queryFn: api.metrics.regional,
  })

  const { data: bottlenecks } = useQuery({
    queryKey: ['risk', 'bottlenecks'],
    queryFn: api.risk.bottlenecks,
  })

  const { setPendingPrompt, setChatContext, setIsChatOpen } = useAppStore()

  if (metricsLoading || regionalLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-sky-400" />
      </div>
    )
  }

  const topBottleneck = bottlenecks?.[0]

  const handleAnalyzeBottleneck = () => {
    if (topBottleneck) {
      setChatContext(`User is viewing executive summary. Top bottleneck is "${topBottleneck.node_id}" with ${topBottleneck.dependent_count} dependents.`)
      setPendingPrompt(`Analyze the business impact of our top bottleneck "${topBottleneck.node_id}" and suggest executive-level mitigation strategies.`)
      setIsChatOpen(true)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Executive Summary</h1>
        <p className="text-slate-400 mt-1">Supply chain risk posture and strategic metrics</p>
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-4">
          <HealthGauge value={metrics?.portfolio_health || 0} />
        </div>

        <div className="col-span-8 grid grid-cols-4 gap-4">
          <KPICard
            value={metrics?.critical_count || 0}
            label="Critical Risks"
            variant="critical"
          />
          <KPICard
            value={metrics?.total_bottlenecks || 0}
            label="Bottlenecks"
            variant="warning"
          />
          <KPICard
            value={metrics?.total_vendors || 0}
            label="Total Vendors"
          />
          <KPICard
            value={metrics?.predicted_links_count || 0}
            label="Hidden Links"
            variant="warning"
          />
        </div>
      </div>

      {topBottleneck && (
        <ConcentrationAlert bottleneck={topBottleneck} onAnalyze={handleAnalyzeBottleneck} />
      )}

      <div className="grid grid-cols-2 gap-6">
        <div>
          <RegionalHeatmap data={regional || []} />
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <h3 className="text-sm font-medium text-slate-400 mb-4">Risk Summary by Category</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-slate-300">Average Portfolio Risk</span>
              <span className="text-lg font-semibold text-slate-100">
                {((metrics?.avg_risk_score || 0) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-300">High Risk Vendors</span>
              <span className="text-lg font-semibold text-amber-400">
                {metrics?.high_risk_count || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-300">GNN Predicted Links</span>
              <span className="text-lg font-semibold text-sky-400">
                {metrics?.predicted_links_count || 0}
              </span>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-700">
            <h4 className="text-sm font-medium text-slate-400 mb-3">ROI Calculator</h4>
            <div className="bg-emerald-900/20 border border-emerald-600 rounded-lg p-3">
              <p className="text-emerald-300 text-sm">
                Early detection of {metrics?.predicted_links_count || 0} hidden Tier-2 dependencies 
                could prevent an estimated <span className="font-bold">$2.4M</span> in supply disruption costs.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
