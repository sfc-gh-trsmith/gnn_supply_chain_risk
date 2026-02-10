export const theme = {
  colors: {
    primary: '#29B5E8',
    secondary: '#10b981',
    tertiary: '#8b5cf6',
    warning: '#f59e0b',
    danger: '#dc2626',
    background: {
      primary: '#0f172a',
      secondary: '#1e293b',
      card: 'rgba(30, 41, 59, 0.8)',
    },
    text: {
      primary: '#f8fafc',
      secondary: '#94a3b8',
      muted: '#64748b',
    },
    risk: {
      critical: '#dc2626',
      high: '#ea580c',
      medium: '#f59e0b',
      low: '#10b981',
    }
  }
}

export const riskColor = (score: number): string => {
  if (score >= 0.7) return theme.colors.risk.critical
  if (score >= 0.5) return theme.colors.risk.high
  if (score >= 0.3) return theme.colors.risk.medium
  return theme.colors.risk.low
}

export const riskCategory = (score: number): string => {
  if (score >= 0.7) return 'CRITICAL'
  if (score >= 0.5) return 'HIGH'
  if (score >= 0.3) return 'MEDIUM'
  return 'LOW'
}
