import ReactFlow, { Background, Controls, MiniMap } from 'reactflow'
import 'reactflow/dist/style.css'
import { nodeTypes } from './CustomNodes'
import { edgeTypes } from './CustomEdges'
import type { NetworkGraphData } from '../../types/network'

interface EgoGraphProps {
  data: NetworkGraphData
  title?: string
}

export function EgoGraph({ data, title }: EgoGraphProps) {
  const nodeCount = data.nodes.length
  const showMiniMap = nodeCount > 10
  
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
      {title && (
        <div className="px-4 py-2 border-b border-slate-700 flex justify-between items-center">
          <h3 className="text-sm font-medium text-slate-300">{title}</h3>
          <span className="text-xs text-slate-400">{nodeCount} nodes connected</span>
        </div>
      )}
      <div className="h-[500px]">
        <ReactFlow
          nodes={data.nodes}
          edges={data.edges}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          fitView
          fitViewOptions={{ padding: 0.3 }}
          minZoom={0.2}
          maxZoom={1.5}
          nodesDraggable={true}
          nodesConnectable={false}
          elementsSelectable={true}
        >
          <Background color="#334155" gap={16} />
          <Controls 
            showInteractive={false}
            className="!bg-slate-800 !border-slate-700 !rounded-lg [&>button]:!bg-slate-700 [&>button]:!border-slate-600 [&>button]:!text-slate-300" 
          />
          {showMiniMap && (
            <MiniMap 
              nodeColor={(node) => {
                if (node.type === 'external') return '#ef4444'
                if (node.type === 'vendor') return '#38bdf8'
                return '#94a3b8'
              }}
              maskColor="rgba(15, 23, 42, 0.8)"
              className="!bg-slate-800 !border-slate-700"
            />
          )}
        </ReactFlow>
      </div>
    </div>
  )
}
