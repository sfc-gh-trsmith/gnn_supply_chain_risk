import Plot from 'react-plotly.js'
import { theme } from '../styles/snowflake-theme'
import type { RegionalRisk } from '../types'

interface RegionalHeatmapProps {
  data: RegionalRisk[]
  onRegionClick?: (region: string) => void
}

export function RegionalHeatmap({ data, onRegionClick }: RegionalHeatmapProps) {
  const sortedData = [...data].sort((a, b) => (b.avg_risk || 0) - (a.avg_risk || 0))
  
  const colors = sortedData.map(d => {
    const risk = d.avg_risk || 0
    if (risk >= 0.6) return theme.colors.risk.critical
    if (risk >= 0.4) return theme.colors.risk.high
    if (risk >= 0.2) return theme.colors.risk.medium
    return theme.colors.risk.low
  })

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
      <h3 className="text-sm font-medium text-slate-400 mb-4">Regional Risk Distribution</h3>
      <Plot
        data={[{
          type: 'bar',
          orientation: 'h',
          y: sortedData.map(d => d.region_name),
          x: sortedData.map(d => (d.avg_risk || 0) * 100),
          marker: { color: colors },
          text: sortedData.map(d => `${((d.avg_risk || 0) * 100).toFixed(0)}%`),
          textposition: 'outside',
          textfont: { color: '#f8fafc', size: 11 },
          hovertemplate: '%{y}<br>Risk: %{x:.1f}%<br>Vendors: %{customdata}<extra></extra>',
          customdata: sortedData.map(d => d.vendor_count),
        }]}
        layout={{
          autosize: true,
          height: Math.max(200, sortedData.length * 35),
          margin: { t: 10, b: 30, l: 100, r: 50 },
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          xaxis: {
            title: 'Risk Score (%)',
            titlefont: { color: '#94a3b8', size: 11 },
            tickfont: { color: '#64748b' },
            gridcolor: '#334155',
            range: [0, 100]
          },
          yaxis: {
            tickfont: { color: '#f8fafc' },
            automargin: true
          },
          font: { color: '#f8fafc' }
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%' }}
        onClick={(e) => {
          if (onRegionClick && e.points[0]) {
            const idx = e.points[0].pointIndex
            onRegionClick(sortedData[idx].region_code)
          }
        }}
      />
    </div>
  )
}
