import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

export function useExecutiveMetrics() {
  return useQuery({
    queryKey: ['metrics', 'executive'],
    queryFn: api.metrics.executive,
  })
}

export function useRegionalRisk() {
  return useQuery({
    queryKey: ['metrics', 'regional'],
    queryFn: api.metrics.regional,
  })
}

export function useRiskScores() {
  return useQuery({
    queryKey: ['risk', 'scores'],
    queryFn: api.risk.scores,
  })
}

export function useBottlenecks() {
  return useQuery({
    queryKey: ['risk', 'bottlenecks'],
    queryFn: api.risk.bottlenecks,
  })
}

export function useBottleneckDependents(nodeId: string | null) {
  return useQuery({
    queryKey: ['risk', 'bottleneck', nodeId, 'dependents'],
    queryFn: () => api.risk.bottleneckDependents(nodeId!),
    enabled: !!nodeId,
  })
}

export function usePredictedLinks() {
  return useQuery({
    queryKey: ['links', 'predicted'],
    queryFn: api.links.predicted,
  })
}

export function useRiskData() {
  const executive = useExecutiveMetrics()
  const regional = useRegionalRisk()
  const bottlenecks = useBottlenecks()
  const links = usePredictedLinks()
  
  return {
    executive,
    regional,
    bottlenecks,
    links,
    isLoading: executive.isLoading || regional.isLoading || bottlenecks.isLoading,
    isError: executive.isError || regional.isError || bottlenecks.isError,
  }
}
