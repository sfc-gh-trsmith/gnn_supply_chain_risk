import { memo } from 'react'
import { EdgeProps, getBezierPath, BaseEdge, EdgeLabelRenderer } from 'reactflow'
import type { SupplyChainEdgeData } from '../../types/network'

export const SuppliesEdge = memo(({ 
  id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, style 
}: EdgeProps<SupplyChainEdgeData>) => {
  const [edgePath] = getBezierPath({ sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition })
  
  return (
    <BaseEdge 
      id={id} 
      path={edgePath} 
      style={{ ...style, stroke: '#64748b', strokeWidth: 1.5 }} 
    />
  )
})

export const LocationEdge = memo(({ 
  id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, style 
}: EdgeProps<SupplyChainEdgeData>) => {
  const [edgePath] = getBezierPath({ sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition })
  
  return (
    <BaseEdge 
      id={id} 
      path={edgePath} 
      style={{ ...style, stroke: '#475569', strokeWidth: 1, strokeDasharray: '4 2' }} 
    />
  )
})

export const PredictedEdge = memo(({ 
  id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, data, style 
}: EdgeProps<SupplyChainEdgeData>) => {
  const [edgePath, labelX, labelY] = getBezierPath({ sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition })
  const probability = data?.probability || 0
  
  return (
    <>
      <BaseEdge 
        id={id} 
        path={edgePath} 
        style={{ ...style, stroke: '#dc2626', strokeWidth: 2, strokeDasharray: '6 3' }} 
      />
      {probability > 0 && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              pointerEvents: 'all',
            }}
            className="px-1.5 py-0.5 bg-red-900/80 border border-red-600 rounded text-[10px] text-red-200"
          >
            {(probability * 100).toFixed(0)}%
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  )
})

export const ShipsToEdge = memo(({ 
  id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, style 
}: EdgeProps<SupplyChainEdgeData>) => {
  const [edgePath] = getBezierPath({ sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition })
  
  return (
    <BaseEdge 
      id={id} 
      path={edgePath} 
      style={{ ...style, stroke: '#f59e0b', strokeWidth: 1.5, strokeDasharray: '3 3' }} 
    />
  )
})

export const edgeTypes = {
  supplies: SuppliesEdge,
  located_in: LocationEdge,
  predicted: PredictedEdge,
  ships_to: ShipsToEdge,
}
