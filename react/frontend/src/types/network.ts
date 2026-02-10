import type { Node, Edge } from 'reactflow'

export interface VendorNodeData {
  label: string
  vendor_id: string
  risk_score: number
  risk_category: string
  country: string
  tier: number
  propagation_step?: number
}

export interface MaterialNodeData {
  label: string
  material_id: string
  criticality: number
  propagation_step?: number
}

export interface RegionNodeData {
  label: string
  region_code: string
  base_risk: number
  vendor_count: number
  is_source?: boolean
}

export interface ExternalNodeData {
  label: string
  node_id: string
  risk_score: number
  is_bottleneck: boolean
}

export type SupplyChainNode = 
  | Node<VendorNodeData, 'vendor'>
  | Node<MaterialNodeData, 'material'>
  | Node<RegionNodeData, 'region'>
  | Node<ExternalNodeData, 'external'>

export interface SupplyChainEdgeData {
  edge_type: 'supplies' | 'located_in' | 'ships_to' | 'predicted' | 'propagation'
  probability?: number
  step?: number
}

export type SupplyChainEdge = Edge<SupplyChainEdgeData>

export interface NetworkGraphData {
  nodes: SupplyChainNode[]
  edges: SupplyChainEdge[]
}

export interface PropagationStep {
  step: number
  label: string
  node_ids: string[]
  count: number
}

export interface PropagationData extends NetworkGraphData {
  propagation_steps: PropagationStep[]
  intensity: number
  region: string
  region_name: string
  total_affected: number
}
