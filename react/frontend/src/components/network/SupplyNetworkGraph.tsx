import { useCallback, useMemo, useState } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { nodeTypes } from './CustomNodes'
import { edgeTypes } from './CustomEdges'
import type { NetworkGraphData } from '../../types/network'

interface SupplyNetworkGraphProps {
  data: NetworkGraphData
  onNodeClick?: (nodeId: string, nodeType: string) => void
}

type LayoutType = 'hierarchical' | 'radial' | 'grouped'

function hierarchicalLayout(nodes: Node[], edges: Edge[]): Node[] {
  const vendorNodes = nodes.filter(n => n.type === 'vendor')
  const materialNodes = nodes.filter(n => n.type === 'material')
  const regionNodes = nodes.filter(n => n.type === 'region')
  const externalNodes = nodes.filter(n => n.type === 'external')

  const nodeSpacingX = 180
  const nodeSpacingY = 160
  const startX = 100

  regionNodes.forEach((node, i) => {
    node.position = {
      x: startX + i * nodeSpacingX * 1.5,
      y: 50
    }
  })

  const regionMap = new Map<string, string[]>()
  edges.forEach(edge => {
    const sourceNode = nodes.find(n => n.id === edge.source)
    const targetNode = nodes.find(n => n.id === edge.target)
    if (sourceNode?.type === 'region' && targetNode?.type === 'vendor') {
      if (!regionMap.has(edge.source)) regionMap.set(edge.source, [])
      regionMap.get(edge.source)!.push(edge.target)
    }
    if (targetNode?.type === 'region' && sourceNode?.type === 'vendor') {
      if (!regionMap.has(edge.target)) regionMap.set(edge.target, [])
      regionMap.get(edge.target)!.push(edge.source)
    }
  })

  let vendorX = startX
  const vendorY = 250
  const assignedVendors = new Set<string>()

  regionNodes.forEach((regionNode, regionIdx) => {
    const regionVendors = regionMap.get(regionNode.id) || []
    regionVendors.forEach((vendorId, i) => {
      const vendor = vendorNodes.find(n => n.id === vendorId)
      if (vendor && !assignedVendors.has(vendorId)) {
        vendor.position = {
          x: regionNode.position.x + (i - regionVendors.length / 2) * 100,
          y: vendorY + (i % 3) * 80
        }
        assignedVendors.add(vendorId)
      }
    })
  })

  vendorNodes.filter(n => !assignedVendors.has(n.id)).forEach((node, i) => {
    node.position = {
      x: vendorX + i * nodeSpacingX,
      y: vendorY + 200
    }
  })

  const materialY = 550
  materialNodes.forEach((node, i) => {
    node.position = {
      x: startX + i * nodeSpacingX,
      y: materialY
    }
  })

  const externalY = 750
  externalNodes.forEach((node, i) => {
    node.position = {
      x: startX + 50 + i * nodeSpacingX,
      y: externalY
    }
  })

  return [...regionNodes, ...vendorNodes, ...materialNodes, ...externalNodes]
}

function radialLayout(nodes: Node[]): Node[] {
  const vendorNodes = nodes.filter(n => n.type === 'vendor')
  const materialNodes = nodes.filter(n => n.type === 'material')
  const regionNodes = nodes.filter(n => n.type === 'region')
  const externalNodes = nodes.filter(n => n.type === 'external')

  const centerX = 1200
  const centerY = 800

  const regionRadius = 700
  regionNodes.forEach((node, i) => {
    const angle = (2 * Math.PI * i) / regionNodes.length - Math.PI / 2
    node.position = {
      x: centerX + regionRadius * Math.cos(angle),
      y: centerY + regionRadius * Math.sin(angle)
    }
  })

  const vendorRadius = 450
  vendorNodes.forEach((node, i) => {
    const angle = (2 * Math.PI * i) / vendorNodes.length
    node.position = {
      x: centerX + vendorRadius * Math.cos(angle),
      y: centerY + vendorRadius * Math.sin(angle)
    }
  })

  const materialRadius = 200
  materialNodes.forEach((node, i) => {
    const angle = (2 * Math.PI * i) / materialNodes.length + Math.PI / 4
    node.position = {
      x: centerX + materialRadius * Math.cos(angle),
      y: centerY + materialRadius * Math.sin(angle)
    }
  })

  const externalRadius = 580
  externalNodes.forEach((node, i) => {
    const angle = (2 * Math.PI * i) / externalNodes.length + Math.PI / (externalNodes.length || 1)
    node.position = {
      x: centerX + externalRadius * Math.cos(angle),
      y: centerY + externalRadius * Math.sin(angle)
    }
  })

  return [...regionNodes, ...vendorNodes, ...materialNodes, ...externalNodes]
}

function groupedLayout(nodes: Node[]): Node[] {
  const vendorNodes = nodes.filter(n => n.type === 'vendor')
  const materialNodes = nodes.filter(n => n.type === 'material')
  const regionNodes = nodes.filter(n => n.type === 'region')
  const externalNodes = nodes.filter(n => n.type === 'external')

  const groupSpacing = 400
  const nodeSpacing = 120
  const nodesPerRow = 6

  regionNodes.forEach((node, i) => {
    const row = Math.floor(i / nodesPerRow)
    const col = i % nodesPerRow
    node.position = {
      x: 100 + col * nodeSpacing,
      y: 50 + row * 100
    }
  })

  const vendorStartY = 200 + Math.ceil(regionNodes.length / nodesPerRow) * 100
  const vendorNodesPerRow = 8
  vendorNodes.forEach((node, i) => {
    const row = Math.floor(i / vendorNodesPerRow)
    const col = i % vendorNodesPerRow
    node.position = {
      x: 80 + col * 150,
      y: vendorStartY + row * 120
    }
  })

  const materialStartY = vendorStartY + Math.ceil(vendorNodes.length / vendorNodesPerRow) * 120 + 80
  materialNodes.forEach((node, i) => {
    const row = Math.floor(i / nodesPerRow)
    const col = i % nodesPerRow
    node.position = {
      x: 100 + col * nodeSpacing,
      y: materialStartY + row * 100
    }
  })

  const externalStartY = materialStartY + Math.ceil(materialNodes.length / nodesPerRow) * 100 + 80
  externalNodes.forEach((node, i) => {
    const row = Math.floor(i / nodesPerRow)
    const col = i % nodesPerRow
    node.position = {
      x: 100 + col * nodeSpacing,
      y: externalStartY + row * 100
    }
  })

  return [...regionNodes, ...vendorNodes, ...materialNodes, ...externalNodes]
}

function layoutNodes(nodes: Node[], edges: Edge[], layoutType: LayoutType): Node[] {
  const clonedNodes = nodes.map(n => ({ ...n, position: { ...n.position } }))
  
  switch (layoutType) {
    case 'hierarchical':
      return hierarchicalLayout(clonedNodes, edges)
    case 'radial':
      return radialLayout(clonedNodes)
    case 'grouped':
      return groupedLayout(clonedNodes)
    default:
      return hierarchicalLayout(clonedNodes, edges)
  }
}

export function SupplyNetworkGraph({ data, onNodeClick }: SupplyNetworkGraphProps) {
  const [layoutType, setLayoutType] = useState<LayoutType>('grouped')
  const [showEdges, setShowEdges] = useState(true)
  const [filterType, setFilterType] = useState<string | null>(null)

  const filteredData = useMemo(() => {
    if (!filterType) return data
    return {
      nodes: data.nodes.filter(n => n.type === filterType),
      edges: data.edges.filter(e => {
        const sourceNode = data.nodes.find(n => n.id === e.source)
        const targetNode = data.nodes.find(n => n.id === e.target)
        return sourceNode?.type === filterType || targetNode?.type === filterType
      })
    }
  }, [data, filterType])

  const initialNodes = useMemo(
    () => layoutNodes(filteredData.nodes as Node[], filteredData.edges as Edge[], layoutType),
    [filteredData.nodes, filteredData.edges, layoutType]
  )
  
  const displayEdges = useMemo(
    () => showEdges ? filteredData.edges as Edge[] : [],
    [filteredData.edges, showEdges]
  )

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(displayEdges)

  useMemo(() => {
    setNodes(initialNodes)
    setEdges(displayEdges)
  }, [initialNodes, displayEdges, setNodes, setEdges])

  const handleNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    if (onNodeClick) {
      onNodeClick(node.id, node.type || 'unknown')
    }
  }, [onNodeClick])

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Layout:</span>
          <div className="flex gap-1">
            {(['grouped', 'hierarchical', 'radial'] as LayoutType[]).map(type => (
              <button
                key={type}
                onClick={() => setLayoutType(type)}
                className={`px-3 py-1 text-xs rounded transition-colors ${
                  layoutType === type
                    ? 'bg-sky-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Filter:</span>
          <div className="flex gap-1">
            <button
              onClick={() => setFilterType(null)}
              className={`px-3 py-1 text-xs rounded transition-colors ${
                !filterType ? 'bg-sky-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              All
            </button>
            {['vendor', 'material', 'region', 'external'].map(type => (
              <button
                key={type}
                onClick={() => setFilterType(filterType === type ? null : type)}
                className={`px-3 py-1 text-xs rounded transition-colors ${
                  filterType === type
                    ? 'bg-sky-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}s
              </button>
            ))}
          </div>
        </div>

        <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer">
          <input
            type="checkbox"
            checked={showEdges}
            onChange={(e) => setShowEdges(e.target.checked)}
            className="rounded bg-slate-700 border-slate-600 text-sky-500 focus:ring-sky-500"
          />
          Show Edges
        </label>
      </div>

      <div className="h-[700px] bg-slate-900 rounded-lg border border-slate-700">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={handleNodeClick}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.1}
          maxZoom={2}
          defaultEdgeOptions={{
            style: { strokeWidth: 1, opacity: 0.6 }
          }}
        >
          <Background color="#334155" gap={20} />
          <Controls className="!bg-slate-800 !border-slate-700 !rounded-lg [&>button]:!bg-slate-700 [&>button]:!border-slate-600 [&>button]:!text-slate-300" />
          <MiniMap
            nodeColor={(node) => {
              switch (node.type) {
                case 'vendor': return '#29B5E8'
                case 'material': return '#8b5cf6'
                case 'region': return '#64748b'
                case 'external': return '#f59e0b'
                default: return '#475569'
              }
            }}
            maskColor="rgba(15, 23, 42, 0.8)"
            className="!bg-slate-800 !border-slate-700"
            pannable
            zoomable
          />
        </ReactFlow>
      </div>
    </div>
  )
}
