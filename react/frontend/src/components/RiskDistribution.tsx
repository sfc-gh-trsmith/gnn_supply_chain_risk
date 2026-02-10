import Plot from 'react-plotly.js'
import { theme } from '../styles/snowflake-theme'

interface RiskDistributionProps {
  data: { category: string; count: number }[]
}

export function RiskDistribution({ data }: RiskDistributionProps) {
  const categoryOrder = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
  const sortedData = categoryOrder
    .map(cat => data.find(d => d.category === cat))
    .filter(Boolean) as { category: string; count: number }[]

  const colors = {
    CRITICAL: theme.colors.risk.critical,
    HIGH: theme.colors.risk.high,
    MEDIUM: theme.colors.risk.medium,
    LOW: theme.colors.risk.low,
  }

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
      <h3 className="text-sm font-medium text-slate-400 mb-4">Risk Distribution</h3>
      <Plot
        data={[{
          type: 'bar',
          x: sortedData.map(d => d.category),
          y: sortedData.map(d => d.count),
          marker: {
            color: sortedData.map(d => colors[d.category as keyof typeof colors] || '#64748b')
          },
          text: sortedData.map(d => d.count.toString()),
          textposition: 'outside',
          textfont: { color: '#f8fafc' },
        }]}
        layout={{
          autosize: true,
          height: 250,
          margin: { t: 20, b: 40, l: 40, r: 20 },
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          xaxis: {
            tickfont: { color: '#f8fafc' },
          },
          yaxis: {
            title: 'Count',
            titlefont: { color: '#94a3b8', size: 11 },
            tickfont: { color: '#64748b' },
            gridcolor: '#334155',
          },
          font: { color: '#f8fafc' },
          bargap: 0.3
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%' }}
      />
    </div>
  )
}
