import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { api } from '../lib/api'
import { useAppStore } from '../stores/appStore'
import { KPICard, ConcentrationAlert } from '../components'
import { EgoGraph } from '../components/network'
import { Loader2, ChevronRight } from 'lucide-react'
import { getRiskBgClass } from '../lib/utils'

export function Tier2Analysis() {
  const [selectedBottleneck, setSelectedBottleneck] = useState<string | null>(null)
  
  const { data: bottlenecks, isLoading: bottlenecksLoading } = useQuery({
    queryKey: ['risk', 'bottlenecks'],
    queryFn: api.risk.bottlenecks,
  })

  const { data: predictedLinks, isLoading: linksLoading } = useQuery({
    queryKey: ['links', 'predicted'],
    queryFn: api.links.predicted,
  })

  const { data: egoData, isLoading: egoLoading } = useQuery({
    queryKey: ['network', 'ego', selectedBottleneck],
    queryFn: () => api.network.egoGraph(selectedBottleneck!),
    enabled: !!selectedBottleneck,
  })

  const { setPendingPrompt, setChatContext, setIsChatOpen } = useAppStore()

  if (bottlenecksLoading || linksLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-sky-400" />
      </div>
    )
  }

  const topBottleneck = bottlenecks?.[0]
  const activeBottleneck = bottlenecks?.find(b => b.node_id === selectedBottleneck) || topBottleneck
  
  if (!selectedBottleneck && topBottleneck) {
    setSelectedBottleneck(topBottleneck.node_id)
  }

  const handleAnalyze = (nodeId: string) => {
    const bn = bottlenecks?.find(b => b.node_id === nodeId)
    if (bn) {
      setChatContext(`User is analyzing bottleneck "${bn.node_id}" with ${bn.dependent_count} dependent vendors and impact score ${(bn.impact_score * 100).toFixed(0)}%.`)
      setPendingPrompt(`Provide detailed analysis of bottleneck "${bn.node_id}" including:\n1. Root cause of concentration\n2. Affected supply chains\n3. Recommended mitigation actions`)
      setIsChatOpen(true)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Tier-2 Analysis</h1>
        <p className="text-slate-400 mt-1">GNN-discovered hidden dependencies and concentration risks</p>
      </div>

      <div className="grid grid-cols-5 gap-4">
        <KPICard value={bottlenecks?.length || 0} label="Bottlenecks Found" variant="critical" />
        <KPICard value={predictedLinks?.length || 0} label="Predicted Links" variant="warning" />
        <KPICard 
          value={predictedLinks?.filter(l => (l.probability || 0) > 0.8).length || 0} 
          label="High Confidence" 
        />
        <KPICard 
          value={bottlenecks?.reduce((sum, b) => sum + b.dependent_count, 0) || 0} 
          label="Affected Vendors" 
          variant="warning"
        />
        <KPICard 
          value={`${((activeBottleneck?.impact_score || 0) * 100).toFixed(0)}%`} 
          label="Top Impact Score" 
          variant="critical"
        />
      </div>

      {topBottleneck && (
        <ConcentrationAlert 
          bottleneck={topBottleneck} 
          onAnalyze={() => handleAnalyze(topBottleneck.node_id)} 
        />
      )}

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          {egoLoading ? (
            <div className="h-[400px] flex items-center justify-center bg-slate-800/50 rounded-lg">
              <Loader2 className="w-6 h-6 animate-spin text-sky-400" />
            </div>
          ) : egoData ? (
            <EgoGraph 
              data={egoData} 
              title={`Dependency Graph: ${activeBottleneck?.node_id}`} 
            />
          ) : null}
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-700">
            <h3 className="font-medium text-slate-200">All Bottlenecks</h3>
          </div>
          <div className="max-h-[360px] overflow-y-auto">
            {bottlenecks?.map((bn) => (
              <button
                key={bn.bottleneck_id}
                onClick={() => setSelectedBottleneck(bn.node_id)}
                className={`w-full px-4 py-3 flex items-center justify-between hover:bg-slate-700/50 transition-colors border-b border-slate-700/50 ${
                  selectedBottleneck === bn.node_id ? 'bg-sky-900/30' : ''
                }`}
              >
                <div className="text-left">
                  <p className="text-sm font-medium text-slate-200">{bn.node_id}</p>
                  <p className="text-xs text-slate-400">{bn.dependent_count} dependents</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded ${getRiskBgClass(bn.impact_score >= 0.7 ? 'CRITICAL' : bn.impact_score >= 0.4 ? 'HIGH' : 'MEDIUM')}`}>
                    {(bn.impact_score * 100).toFixed(0)}%
                  </span>
                  <ChevronRight className="w-4 h-4 text-slate-500" />
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-700 flex items-center justify-between">
          <h3 className="font-medium text-slate-200">Predicted Tier-2 Links</h3>
          <span className="text-xs text-slate-400">{predictedLinks?.length} total</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-900/50">
              <tr>
                <th className="px-4 py-2 text-left text-slate-400 font-medium">Source</th>
                <th className="px-4 py-2 text-left text-slate-400 font-medium">Target</th>
                <th className="px-4 py-2 text-left text-slate-400 font-medium">Link Type</th>
                <th className="px-4 py-2 text-left text-slate-400 font-medium">Confidence</th>
                <th className="px-4 py-2 text-left text-slate-400 font-medium">Evidence</th>
              </tr>
            </thead>
            <tbody>
              {predictedLinks?.slice(0, 10).map((link) => (
                <tr key={link.link_id} className="border-t border-slate-700/50 hover:bg-slate-700/30">
                  <td className="px-4 py-2 text-slate-200 font-mono text-xs">{link.source_node_id}</td>
                  <td className="px-4 py-2 text-slate-200 font-mono text-xs">{link.target_node_id}</td>
                  <td className="px-4 py-2 text-slate-300">{link.link_type}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      (link.probability || 0) >= 0.8 ? 'bg-red-600/30 text-red-300' : 
                      (link.probability || 0) >= 0.6 ? 'bg-amber-600/30 text-amber-300' : 
                      'bg-slate-600/30 text-slate-300'
                    }`}>
                      {((link.probability || 0) * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className="px-4 py-2 text-slate-400 text-xs">{link.evidence_strength}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
