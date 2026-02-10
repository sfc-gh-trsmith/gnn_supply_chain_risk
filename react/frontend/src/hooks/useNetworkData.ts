import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

export function useNetworkGraph() {
  return useQuery({
    queryKey: ['network', 'graph'],
    queryFn: api.network.graph,
  })
}

export function useEgoGraph(nodeId: string | null) {
  return useQuery({
    queryKey: ['network', 'ego', nodeId],
    queryFn: () => api.network.egoGraph(nodeId!),
    enabled: !!nodeId,
  })
}

export function useNetworkData() {
  const graph = useNetworkGraph()
  
  return {
    graph,
    isLoading: graph.isLoading,
    isError: graph.isError,
  }
}
