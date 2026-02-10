import { cn, getRiskBgClass } from '../lib/utils'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface KPICardProps {
  value: number | string
  label: string
  trend?: 'up' | 'down' | 'neutral'
  variant?: 'default' | 'critical' | 'warning' | 'success'
  className?: string
}

export function KPICard({ value, label, trend, variant = 'default', className }: KPICardProps) {
  const variantStyles = {
    default: 'border-slate-600',
    critical: 'border-red-600 bg-red-600/10',
    warning: 'border-amber-500 bg-amber-500/10',
    success: 'border-emerald-500 bg-emerald-500/10',
  }

  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus
  const trendColor = trend === 'up' ? 'text-red-400' : trend === 'down' ? 'text-emerald-400' : 'text-slate-400'

  return (
    <div className={cn(
      'bg-slate-800/50 border rounded-lg p-4',
      variantStyles[variant],
      className
    )}>
      <div className="flex items-center justify-between">
        <span className="text-3xl font-bold text-slate-100">{value}</span>
        {trend && <TrendIcon className={cn('w-5 h-5', trendColor)} />}
      </div>
      <p className="text-sm text-slate-400 mt-1">{label}</p>
    </div>
  )
}
