import Plot from 'react-plotly.js'
import { theme } from '../styles/snowflake-theme'

interface HealthGaugeProps {
  value: number
  title?: string
}

export function HealthGauge({ value, title = 'Portfolio Health' }: HealthGaugeProps) {
  const color = value >= 70 ? theme.colors.risk.low : value >= 40 ? theme.colors.risk.medium : theme.colors.risk.critical

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
      <h3 className="text-sm font-medium text-slate-400 mb-2">{title}</h3>
      <Plot
        data={[{
          type: 'indicator',
          mode: 'gauge+number',
          value: value,
          number: { suffix: '%', font: { color: '#f8fafc', size: 36 } },
          gauge: {
            axis: { range: [0, 100], tickcolor: '#64748b', tickfont: { color: '#64748b' } },
            bar: { color: color },
            bgcolor: '#1e293b',
            borderwidth: 0,
            steps: [
              { range: [0, 40], color: 'rgba(220, 38, 38, 0.2)' },
              { range: [40, 70], color: 'rgba(245, 158, 11, 0.2)' },
              { range: [70, 100], color: 'rgba(16, 185, 129, 0.2)' },
            ],
            threshold: {
              line: { color: '#f8fafc', width: 2 },
              thickness: 0.75,
              value: value
            }
          }
        }]}
        layout={{
          autosize: true,
          height: 200,
          margin: { t: 20, b: 20, l: 30, r: 30 },
          paper_bgcolor: 'transparent',
          font: { color: '#f8fafc' }
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%' }}
      />
    </div>
  )
}
