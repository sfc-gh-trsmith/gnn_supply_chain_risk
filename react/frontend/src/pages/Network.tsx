import { useQuery } from '@tanstack/react-query'
import { SupplyNetworkGraph } from '../components/network'
import { api } from '../lib/api'
import { useAppStore } from '../stores/appStore'
import { Loader2 } from 'lucide-react'

export function Network() {
  const { data: graphData, isLoading } = useQuery({
    queryKey: ['network', 'graph'],
    queryFn: api.network.graph,
  })

  const { setPendingPrompt, setChatContext, setIsChatOpen } = useAppStore()

  const handleNodeClick = (nodeId: string, nodeType: string) => {
    setChatContext(`User clicked on ${nodeType} node "${nodeId}" in the supply network graph.`)
    setPendingPrompt(`Tell me about ${nodeType === 'vendor' ? 'vendor' : nodeType === 'external' ? 'external supplier' : nodeType} "${nodeId}" - what is their risk profile and any concerns?`)
    setIsChatOpen(true)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-sky-400" />
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Supply Network</h1>
          <p className="text-slate-400 mt-1">Interactive visualization of supply chain relationships</p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-sky-500" />
            <span className="text-slate-400">Vendors</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-purple-500" />
            <span className="text-slate-400">Materials</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-slate-500" />
            <span className="text-slate-400">Regions</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rotate-45 bg-amber-500" />
            <span className="text-slate-400">External</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-red-500 border-dashed border-t-2 border-red-500" />
            <span className="text-slate-400">Predicted</span>
          </div>
        </div>
      </div>

      {graphData && (
        <SupplyNetworkGraph data={graphData} onNodeClick={handleNodeClick} />
      )}

      <div className="grid grid-cols-4 gap-4 text-sm">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <p className="text-slate-400">Total Nodes</p>
          <p className="text-2xl font-bold text-slate-100">{graphData?.nodes.length || 0}</p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <p className="text-slate-400">Total Edges</p>
          <p className="text-2xl font-bold text-slate-100">{graphData?.edges.length || 0}</p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <p className="text-slate-400">Vendor Nodes</p>
          <p className="text-2xl font-bold text-sky-400">
            {graphData?.nodes.filter(n => n.type === 'vendor').length || 0}
          </p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <p className="text-slate-400">Predicted Links</p>
          <p className="text-2xl font-bold text-red-400">
            {graphData?.edges.filter(e => e.type === 'predicted').length || 0}
          </p>
        </div>
      </div>
    </div>
  )
}
