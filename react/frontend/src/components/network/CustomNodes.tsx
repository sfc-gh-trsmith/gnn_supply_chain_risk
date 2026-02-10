import { memo, useState } from 'react'
import { Handle, Position, NodeProps } from 'reactflow'
import type { VendorNodeData, MaterialNodeData, RegionNodeData, ExternalNodeData } from '../../types/network'
import { getRiskColor } from '../../lib/utils'

export const VendorNode = memo(({ data }: NodeProps<VendorNodeData>) => {
  const [showFull, setShowFull] = useState(false)
  const borderColor = getRiskColor(data.risk_score)

  return (
    <div
      className="px-2 py-1.5 rounded-full bg-slate-800 border-2 text-center cursor-pointer transition-all hover:z-50"
      style={{ borderColor, minWidth: showFull ? 'auto' : '70px' }}
      onMouseEnter={() => setShowFull(true)}
      onMouseLeave={() => setShowFull(false)}
    >
      <Handle type="target" position={Position.Top} className="!bg-slate-500 !w-2 !h-2" />
      <div
        className={`text-[10px] font-medium text-slate-200 ${showFull ? '' : 'truncate max-w-[60px]'}`}
        title={data.label}
      >
        {data.label}
      </div>
      <div className="text-[9px] text-slate-400">{data.country}</div>
      <div className="text-[9px] font-mono" style={{ color: borderColor }}>
        {(data.risk_score * 100).toFixed(0)}%
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-slate-500 !w-2 !h-2" />
    </div>
  )
})

export const MaterialNode = memo(({ data }: NodeProps<MaterialNodeData>) => {
  const [showFull, setShowFull] = useState(false)

  return (
    <div
      className="px-2 py-1.5 bg-purple-900/50 border-2 border-purple-500 rounded-lg text-center cursor-pointer transition-all hover:z-50"
      style={{ minWidth: showFull ? 'auto' : '70px' }}
      onMouseEnter={() => setShowFull(true)}
      onMouseLeave={() => setShowFull(false)}
    >
      <Handle type="target" position={Position.Top} className="!bg-purple-500 !w-2 !h-2" />
      <div
        className={`text-[10px] font-medium text-purple-200 ${showFull ? '' : 'truncate max-w-[60px]'}`}
        title={data.label}
      >
        {data.label}
      </div>
      <div className="text-[9px] text-purple-300">
        Crit: {(data.criticality * 100).toFixed(0)}%
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-purple-500 !w-2 !h-2" />
    </div>
  )
})

export const RegionNode = memo(({ data }: NodeProps<RegionNodeData>) => {
  const riskColor = data.base_risk >= 0.6 ? '#dc2626' : data.base_risk >= 0.3 ? '#f59e0b' : '#10b981'

  return (
    <div
      className="px-2 py-1.5 bg-slate-700 border-2 rounded-sm text-center"
      style={{ borderColor: riskColor, minWidth: '70px' }}
    >
      <Handle type="target" position={Position.Top} className="!bg-slate-400 !w-2 !h-2" />
      <div className="text-[10px] font-medium text-slate-200">{data.label}</div>
      <div className="text-[9px] text-slate-400">{data.vendor_count} vendors</div>
      <Handle type="source" position={Position.Bottom} className="!bg-slate-400 !w-2 !h-2" />
    </div>
  )
})

export const ExternalNode = memo(({ data }: NodeProps<ExternalNodeData>) => {
  const [showFull, setShowFull] = useState(false)
  const borderColor = data.is_bottleneck ? '#dc2626' : getRiskColor(data.risk_score)

  return (
    <div
      className="px-2 py-1.5 bg-amber-900/30 border-2 text-center cursor-pointer transition-all hover:z-50"
      style={{ borderColor, minWidth: '60px', transform: 'rotate(45deg)' }}
      onMouseEnter={() => setShowFull(true)}
      onMouseLeave={() => setShowFull(false)}
    >
      <Handle type="target" position={Position.Top} className="!bg-amber-500 !w-2 !h-2" style={{ transform: 'rotate(-45deg)' }} />
      <div style={{ transform: 'rotate(-45deg)' }}>
        <div
          className={`text-[10px] font-medium text-amber-200 ${showFull ? '' : 'truncate max-w-[50px]'}`}
          title={data.label}
        >
          {data.label}
        </div>
        {data.is_bottleneck && (
          <div className="text-[8px] text-red-400 font-bold">BOTTLENECK</div>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-amber-500 !w-2 !h-2" style={{ transform: 'rotate(-45deg)' }} />
    </div>
  )
})

export const nodeTypes = {
  vendor: VendorNode,
  material: MaterialNode,
  region: RegionNode,
  external: ExternalNode,
}
