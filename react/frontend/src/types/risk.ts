export interface Vendor {
  vendor_id: string
  name: string
  country_code: string
  city: string | null
  tier: number
  financial_health_score: number
}

export interface RiskScore {
  score_id: number
  node_id: string
  node_type: 'SUPPLIER' | 'PART' | 'EXTERNAL_SUPPLIER'
  risk_score: number
  risk_category: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
  confidence: number
}

export interface Bottleneck {
  bottleneck_id: number
  node_id: string
  node_type: string
  dependent_count: number
  impact_score: number
  description: string | null
  mitigation_status: 'UNMITIGATED' | 'IN_PROGRESS' | 'MITIGATED'
}

export interface Region {
  region_code: string
  region_name: string
  base_risk_score: number
  geopolitical_risk: number
  natural_disaster_risk: number
  infrastructure_score: number
}

export interface PredictedLink {
  link_id: number
  source_node_id: string
  source_node_type: string
  target_node_id: string
  target_node_type: string
  link_type: string
  probability: number
  evidence_strength: string
}

export interface ExecutiveMetrics {
  total_vendors: number
  critical_count: number
  high_risk_count: number
  avg_risk_score: number
  total_bottlenecks: number
  predicted_links_count: number
  portfolio_health: number
}

export interface RegionalRisk {
  region_code: string
  region_name: string
  vendor_count: number
  avg_risk: number
  high_risk_count: number
}
