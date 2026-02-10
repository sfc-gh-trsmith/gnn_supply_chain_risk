import { useState, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { useAppStore } from '../stores/appStore'
import { Loader2, Zap, AlertTriangle } from 'lucide-react'
import { PropagationGraph } from '../components/network/PropagationGraph'

export function Simulator() {
  const [selectedRegion, setSelectedRegion] = useState<string>('CHN')
  const [intensity, setIntensity] = useState(0.5)

  const { data: regions } = useQuery({
    queryKey: ['metrics', 'regional'],
    queryFn: api.metrics.regional,
  })

  const { data: propagationData, refetch: refetchPropagation, isLoading: propagationLoading } = useQuery({
    queryKey: ['simulator', 'propagation', selectedRegion, intensity],
    queryFn: () => api.simulator.propagation(selectedRegion, intensity),
    enabled: !!selectedRegion,
  })

  const mutation = useMutation({
    mutationFn: () => api.simulator.shock(selectedRegion, intensity),
  })

  const { setPendingPrompt, setChatContext, setIsChatOpen } = useAppStore()

  const handleSimulate = () => {
    mutation.mutate()
    refetchPropagation()
  }

  const handleAnalyze = () => {
    if (mutation.data) {
      const regionName = regions?.find(r => r.region_code === selectedRegion)?.region_name || selectedRegion
      setChatContext(`User simulated a ${(intensity * 100).toFixed(0)}% disruption in ${regionName}. Results: ${mutation.data.affected_vendors} vendors affected, risk increase of ${mutation.data.risk_increase}%.`)
      setPendingPrompt(`Based on this simulation of a ${(intensity * 100).toFixed(0)}% disruption in ${regionName}, what immediate actions should we take to mitigate the impact on our ${mutation.data.affected_vendors} affected vendors?`)
      setIsChatOpen(true)
    }
  }

  useEffect(() => {
    if (selectedRegion) {
      refetchPropagation()
    }
  }, [selectedRegion, intensity])

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Scenario Simulator</h1>
        <p className="text-slate-400 mt-1">Model regional disruptions and visualize risk propagation through the supply network</p>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h3 className="font-semibold text-slate-200 mb-4">Disruption Parameters</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-2">Target Region</label>
              <select
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-sky-500"
              >
                {regions?.map((r) => (
                  <option key={r.region_code} value={r.region_code}>
                    {r.region_name} ({r.vendor_count} vendors)
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-slate-400 mb-2">
                Shock Intensity: {(intensity * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0.1"
                max="1"
                step="0.1"
                value={intensity}
                onChange={(e) => setIntensity(parseFloat(e.target.value))}
                className="w-full accent-sky-500"
              />
              <div className="flex justify-between text-xs text-slate-500 mt-1">
                <span>Mild (10%)</span>
                <span>Moderate (50%)</span>
                <span>Severe (100%)</span>
              </div>
            </div>

            <button
              onClick={handleSimulate}
              disabled={mutation.isPending}
              className="w-full flex items-center justify-center gap-2 bg-amber-600 hover:bg-amber-500 disabled:bg-slate-700 text-white py-3 rounded-lg transition-colors"
            >
              {mutation.isPending ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Zap className="w-5 h-5" />
              )}
              Run Simulation
            </button>
          </div>
        </div>

        <div className="col-span-2 bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h3 className="font-semibold text-slate-200 mb-4">Simulation Results</h3>
          
          {mutation.data ? (
            <div className="space-y-4">
              <div className="bg-red-900/20 border border-red-600 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-5 h-5 text-red-500" />
                  <span className="font-semibold text-red-400">Impact Assessment</span>
                </div>
                <p className="text-slate-300 text-sm">
                  A {(intensity * 100).toFixed(0)}% disruption in {regions?.find(r => r.region_code === selectedRegion)?.region_name} 
                  would affect <span className="font-bold text-white">{mutation.data.affected_vendors}</span> vendors.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <p className="text-xs text-slate-400">Current Avg Risk</p>
                  <p className="text-2xl font-bold text-slate-100">
                    {(mutation.data.current_avg_risk * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <p className="text-xs text-slate-400">Projected Risk</p>
                  <p className="text-2xl font-bold text-red-400">
                    {(mutation.data.projected_risk * 100).toFixed(1)}%
                  </p>
                </div>
              </div>

              <div className="bg-amber-900/20 border border-amber-600 rounded-lg p-4">
                <p className="text-sm text-amber-300">
                  Risk increase of <span className="font-bold">{mutation.data.risk_increase}%</span> expected
                </p>
              </div>

              <button
                onClick={handleAnalyze}
                className="w-full bg-sky-600 hover:bg-sky-500 text-white py-2 rounded-lg transition-colors text-sm"
              >
                Ask AI for Mitigation Strategies
              </button>
            </div>
          ) : (
            <div className="text-center text-slate-500 py-12">
              <Zap className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>Configure parameters and run a simulation</p>
            </div>
          )}
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-slate-200 mb-4">Risk Propagation Visualization</h2>
        {propagationLoading ? (
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-12 flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-sky-500 animate-spin" />
          </div>
        ) : propagationData ? (
          <PropagationGraph data={propagationData} />
        ) : (
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-12 text-center text-slate-500">
            <p>Select a region to visualize disruption propagation</p>
          </div>
        )}
      </div>
    </div>
  )
}
