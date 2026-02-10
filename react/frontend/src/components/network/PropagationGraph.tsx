import { useState, useEffect, useCallback, useMemo } from 'react'
import ReactFlow, { Background, Controls, MiniMap, Node, Edge, useReactFlow, ReactFlowProvider } from 'reactflow'
import 'reactflow/dist/style.css'
import { nodeTypes } from './CustomNodes'
import { Play, Pause, RotateCcw, SkipForward } from 'lucide-react'
import type { PropagationData } from '../../types/network'

interface PropagationGraphProps {
  data: PropagationData
}

const ANIMATION_DURATION = 2500

function PropagationGraphInner({ data }: PropagationGraphProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [isPlaying, setIsPlaying] = useState(true)
  const { fitView } = useReactFlow()
  
  const maxStep = data.propagation_steps.length - 1
  
  useEffect(() => {
    setCurrentStep(0)
    setIsPlaying(true)
  }, [data.region])
  
  useEffect(() => {
    if (!isPlaying) return
    
    const timer = setTimeout(() => {
      setCurrentStep((prev) => {
        if (prev >= maxStep) {
          return 0
        }
        return prev + 1
      })
    }, ANIMATION_DURATION)
    
    return () => clearTimeout(timer)
  }, [currentStep, isPlaying, maxStep])
  
  const handlePlayPause = useCallback(() => {
    setIsPlaying((prev) => !prev)
  }, [])
  
  const handleReset = useCallback(() => {
    setCurrentStep(0)
    setIsPlaying(true)
  }, [])
  
  const handleStepForward = useCallback(() => {
    setCurrentStep((prev) => (prev >= maxStep ? 0 : prev + 1))
  }, [maxStep])
  
  const { visibleNodes, visibleEdges } = useMemo(() => {
    const visibleNodeIds = new Set<string>()
    const visibleSteps = data.propagation_steps.slice(0, currentStep + 1)
    
    visibleSteps.forEach((step) => {
      step.node_ids.forEach((id) => visibleNodeIds.add(id))
    })
    
    data.nodes.forEach((n) => {
      const nodeData = n.data as any
      if (nodeData.is_source) {
        visibleNodeIds.add(n.id)
      }
      const nodeStep = nodeData.propagation_step
      if (nodeStep !== undefined && nodeStep <= currentStep) {
        visibleNodeIds.add(n.id)
      }
    })
    
    const nodes = data.nodes.filter((n) => visibleNodeIds.has(n.id))
    
    const edges = data.edges.filter((e) => {
      const edgeStep = e.data?.step ?? -1
      const sourceVisible = visibleNodeIds.has(e.source)
      const targetVisible = visibleNodeIds.has(e.target)
      return edgeStep <= currentStep && sourceVisible && targetVisible
    })
    
    return { visibleNodes: nodes, visibleEdges: edges }
  }, [data, currentStep])
  
  const styledNodes: Node[] = useMemo(() => {
    return visibleNodes.map((node) => {
      const nodeStep = (node.data as any).propagation_step ?? -1
      const isCurrentStep = nodeStep === currentStep
      const isSource = (node.data as any).is_source
      
      return {
        ...node,
        style: {
          ...node.style,
          opacity: 1,
          transition: 'all 0.3s ease-out'
        },
        className: isCurrentStep || isSource ? 'scale-110' : '',
        data: {
          ...node.data,
          highlighted: isCurrentStep || isSource
        }
      }
    }) as Node[]
  }, [visibleNodes, currentStep])
  
  const styledEdges: Edge[] = useMemo(() => {
    return visibleEdges.map((edge) => {
      const edgeStep = edge.data?.step ?? -1
      const isCurrentStep = edgeStep === currentStep
      
      return {
        ...edge,
        type: 'default',
        animated: isCurrentStep,
        style: {
          stroke: isCurrentStep ? '#f97316' : edgeStep === 0 ? '#ef4444' : edgeStep === 1 ? '#eab308' : '#22c55e',
          strokeWidth: isCurrentStep ? 3 : 2,
          opacity: 1
        }
      }
    }) as Edge[]
  }, [visibleEdges, currentStep])
  
  useEffect(() => {
    if (styledNodes.length > 0) {
      const timer = setTimeout(() => {
        fitView({ padding: 0.2, duration: 300, minZoom: 0.1, maxZoom: 0.8 })
      }, 100)
      return () => clearTimeout(timer)
    }
  }, [data.region, styledNodes.length, fitView])
  
  const currentStepInfo = data.propagation_steps[currentStep]
  
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-700">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-slate-300">Disruption Propagation</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={handleReset}
              className="p-1.5 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 transition-colors"
              title="Reset"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              onClick={handlePlayPause}
              className="p-1.5 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 transition-colors"
              title={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </button>
            <button
              onClick={handleStepForward}
              className="p-1.5 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 transition-colors"
              title="Step Forward"
            >
              <SkipForward className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {data.propagation_steps.map((step, idx) => (
            <div
              key={step.step}
              className={`flex-1 text-center py-1.5 px-2 rounded text-xs transition-all cursor-pointer ${
                idx === currentStep
                  ? 'bg-orange-600 text-white'
                  : idx < currentStep
                  ? 'bg-slate-600 text-slate-200'
                  : 'bg-slate-700/50 text-slate-500'
              }`}
              onClick={() => {
                setCurrentStep(idx)
                setIsPlaying(false)
              }}
            >
              <div className="font-medium truncate">{step.label}</div>
              <div className="text-[10px] opacity-75">{step.count} nodes</div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="h-[500px] relative">
        <ReactFlow
          nodes={styledNodes}
          edges={styledEdges}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2, minZoom: 0.1, maxZoom: 0.8 }}
          minZoom={0.05}
          maxZoom={2}
          nodesDraggable={true}
          nodesConnectable={false}
          elementsSelectable={true}
          onInit={(instance) => {
            setTimeout(() => {
              instance.fitView({ padding: 0.2, minZoom: 0.1, maxZoom: 0.8 })
            }, 200)
          }}
        >
          <Background color="#334155" gap={16} />
          <Controls 
            showInteractive={false}
            className="!bg-slate-800 !border-slate-700 !rounded-lg [&>button]:!bg-slate-700 [&>button]:!border-slate-600 [&>button]:!text-slate-300" 
          />
          <MiniMap 
            nodeColor={(node) => {
              const step = (node.data as any).propagation_step
              if ((node.data as any).is_source) return '#dc2626'
              if (step === 0) return '#ef4444'
              if (step === 1) return '#eab308'
              if (step === 2) return '#22c55e'
              return '#94a3b8'
            }}
            maskColor="rgba(15, 23, 42, 0.8)"
            className="!bg-slate-800 !border-slate-700"
          />
        </ReactFlow>
        
        {currentStepInfo && (
          <div className="absolute bottom-4 left-4 bg-slate-900/90 border border-slate-600 rounded-lg px-3 py-2 text-sm">
            <div className="text-orange-400 font-medium">{currentStepInfo.label}</div>
            <div className="text-slate-400 text-xs">{currentStepInfo.count} affected</div>
          </div>
        )}
      </div>
      
      <div className="px-4 py-2 border-t border-slate-700 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-red-500"></span>
            <span>Initial</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
            <span>Materials</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-green-500"></span>
            <span>Secondary</span>
          </div>
        </div>
        <div>
          Total impact: <span className="text-white font-medium">{data.total_affected}</span> vendors
        </div>
      </div>
    </div>
  )
}

export function PropagationGraph({ data }: PropagationGraphProps) {
  return (
    <ReactFlowProvider>
      <PropagationGraphInner data={data} />
    </ReactFlowProvider>
  )
}
