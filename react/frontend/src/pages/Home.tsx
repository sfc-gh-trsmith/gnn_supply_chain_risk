import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { Link } from 'react-router-dom'
import { Loader2, ArrowRight, AlertTriangle, Network, Target, Zap } from 'lucide-react'
import { KPICard, HealthGauge } from '../components'

export function Home() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['metrics', 'executive'],
    queryFn: api.metrics.executive,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-sky-400" />
      </div>
    )
  }

  return (
    <div className="p-6 space-y-8">
      <div className="text-center py-8">
        <h1 className="text-4xl font-bold text-slate-100 mb-2">
          N-Tier Supply Chain Risk
        </h1>
        <p className="text-xl text-slate-400 max-w-2xl mx-auto">
          Graph Neural Network powered analytics for discovering hidden dependencies 
          and predicting supply chain vulnerabilities
        </p>
      </div>

      <div className="grid grid-cols-3 gap-6 max-w-4xl mx-auto">
        <div className="col-span-1">
          <HealthGauge value={metrics?.portfolio_health || 0} />
        </div>
        <div className="col-span-2 grid grid-cols-2 gap-4">
          <KPICard value={metrics?.total_vendors || 0} label="Total Vendors" />
          <KPICard value={metrics?.critical_count || 0} label="Critical Risks" variant="critical" />
          <KPICard value={metrics?.total_bottlenecks || 0} label="Bottlenecks" variant="warning" />
          <KPICard value={metrics?.predicted_links_count || 0} label="Hidden Links Found" />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 max-w-5xl mx-auto pt-6">
        <Link 
          to="/executive" 
          className="bg-slate-800/50 border border-slate-700 hover:border-sky-500 rounded-lg p-6 transition-colors group"
        >
          <AlertTriangle className="w-8 h-8 text-amber-400 mb-3" />
          <h3 className="font-semibold text-slate-200 group-hover:text-sky-400 transition-colors">
            Executive Summary
          </h3>
          <p className="text-sm text-slate-400 mt-1">Portfolio health and strategic KPIs</p>
          <div className="flex items-center gap-1 text-sky-400 mt-4 text-sm">
            View Dashboard <ArrowRight className="w-4 h-4" />
          </div>
        </Link>

        <Link 
          to="/network" 
          className="bg-slate-800/50 border border-slate-700 hover:border-sky-500 rounded-lg p-6 transition-colors group"
        >
          <Network className="w-8 h-8 text-purple-400 mb-3" />
          <h3 className="font-semibold text-slate-200 group-hover:text-sky-400 transition-colors">
            Supply Network
          </h3>
          <p className="text-sm text-slate-400 mt-1">Interactive graph visualization</p>
          <div className="flex items-center gap-1 text-sky-400 mt-4 text-sm">
            Explore Graph <ArrowRight className="w-4 h-4" />
          </div>
        </Link>

        <Link 
          to="/tier2" 
          className="bg-slate-800/50 border border-slate-700 hover:border-sky-500 rounded-lg p-6 transition-colors group"
        >
          <Target className="w-8 h-8 text-red-400 mb-3" />
          <h3 className="font-semibold text-slate-200 group-hover:text-sky-400 transition-colors">
            Tier-2 Analysis
          </h3>
          <p className="text-sm text-slate-400 mt-1">Hidden dependencies & bottlenecks</p>
          <div className="flex items-center gap-1 text-sky-400 mt-4 text-sm">
            Analyze Risks <ArrowRight className="w-4 h-4" />
          </div>
        </Link>

        <Link 
          to="/simulator" 
          className="bg-slate-800/50 border border-slate-700 hover:border-sky-500 rounded-lg p-6 transition-colors group"
        >
          <Zap className="w-8 h-8 text-sky-400 mb-3" />
          <h3 className="font-semibold text-slate-200 group-hover:text-sky-400 transition-colors">
            Scenario Simulator
          </h3>
          <p className="text-sm text-slate-400 mt-1">What-if disruption modeling</p>
          <div className="flex items-center gap-1 text-sky-400 mt-4 text-sm">
            Run Simulation <ArrowRight className="w-4 h-4" />
          </div>
        </Link>
      </div>

      <div className="text-center pt-8">
        <p className="text-slate-500 text-sm">
          Powered by <span className="text-sky-400">Snowflake Cortex</span> and 
          <span className="text-purple-400"> PyTorch Geometric</span>
        </p>
      </div>
    </div>
  )
}
