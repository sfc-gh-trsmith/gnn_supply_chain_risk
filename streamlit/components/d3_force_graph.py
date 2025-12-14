"""
D3.js Force-Directed Graph Component

Interactive network visualization for supply chain graphs.
Supports heterogeneous node types with different colors and sizes.
"""

import json
import streamlit.components.v1 as components


def render_force_graph(nodes: list, edges: list, config: dict = None, height: int = 600):
    """
    Render an interactive force-directed graph using D3.js.
    
    Args:
        nodes: List of dicts with keys: id, type, label, risk_score (optional)
        edges: List of dicts with keys: source, target, type (optional), weight (optional)
        config: Optional config dict with keys: show_labels, highlight_risks, animate_reveal
        height: Height of the visualization in pixels
    """
    default_config = {
        "show_labels": True,
        "highlight_risks": True,
        "animate_reveal": False,
        "node_colors": {
            "SUPPLIER": "#3b82f6",      # Blue
            "PART": "#8b5cf6",           # Purple
            "MATERIAL": "#8b5cf6",       # Purple
            "EXTERNAL_SUPPLIER": "#f59e0b",  # Amber
            "REGION": "#10b981",         # Green
            "HIDDEN": "#6b7280"          # Gray (for reveal animation)
        },
        "risk_colors": {
            "critical": "#dc2626",
            "high": "#ea580c", 
            "medium": "#ca8a04",
            "low": "#16a34a"
        }
    }
    
    if config:
        default_config.update(config)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                overflow: hidden;
            }}
            #graph-container {{
                width: 100%;
                height: {height}px;
                position: relative;
            }}
            .node-label {{
                font-size: 11px;
                fill: #e2e8f0;
                pointer-events: none;
                text-shadow: 0 1px 2px rgba(0,0,0,0.8);
            }}
            .link {{
                stroke-opacity: 0.6;
            }}
            .link-predicted {{
                stroke-dasharray: 4,4;
            }}
            .tooltip {{
                position: absolute;
                background: rgba(15, 23, 42, 0.95);
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 12px;
                color: #e2e8f0;
                font-size: 12px;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s;
                max-width: 250px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }}
            .tooltip h4 {{
                margin: 0 0 8px 0;
                color: #f8fafc;
                font-size: 14px;
            }}
            .tooltip-row {{
                display: flex;
                justify-content: space-between;
                margin: 4px 0;
            }}
            .tooltip-label {{
                color: #94a3b8;
            }}
            .risk-badge {{
                padding: 2px 8px;
                border-radius: 4px;
                font-weight: 600;
                font-size: 11px;
            }}
            .legend {{
                position: absolute;
                bottom: 20px;
                left: 20px;
                background: rgba(15, 23, 42, 0.9);
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 12px;
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                margin: 4px 0;
                font-size: 12px;
                color: #e2e8f0;
            }}
            .legend-color {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }}
        </style>
    </head>
    <body>
        <div id="graph-container">
            <div class="tooltip" id="tooltip"></div>
            <div class="legend" id="legend"></div>
        </div>
        <script>
            const nodes = {json.dumps(nodes)};
            const links = {json.dumps(edges)};
            const config = {json.dumps(default_config)};
            
            const container = document.getElementById('graph-container');
            const width = container.clientWidth;
            const height = {height};
            
            // Create SVG
            const svg = d3.select('#graph-container')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            // Add zoom behavior
            const g = svg.append('g');
            svg.call(d3.zoom()
                .scaleExtent([0.2, 4])
                .on('zoom', (event) => g.attr('transform', event.transform)));
            
            // Create force simulation
            const simulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(links).id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collision', d3.forceCollide().radius(30));
            
            // Draw links
            const link = g.append('g')
                .selectAll('line')
                .data(links)
                .join('line')
                .attr('class', d => d.predicted ? 'link link-predicted' : 'link')
                .attr('stroke', d => d.predicted ? '#f59e0b' : '#475569')
                .attr('stroke-width', d => Math.sqrt(d.weight || 1) * 1.5);
            
            // Draw nodes
            const node = g.append('g')
                .selectAll('circle')
                .data(nodes)
                .join('circle')
                .attr('r', d => {{
                    if (d.type === 'EXTERNAL_SUPPLIER') return 14;
                    if (d.type === 'SUPPLIER') return 12;
                    return 8;
                }})
                .attr('fill', d => {{
                    if (config.highlight_risks && d.risk_score) {{
                        if (d.risk_score >= 0.75) return config.risk_colors.critical;
                        if (d.risk_score >= 0.5) return config.risk_colors.high;
                        if (d.risk_score >= 0.25) return config.risk_colors.medium;
                        return config.risk_colors.low;
                    }}
                    return config.node_colors[d.type] || '#6b7280';
                }})
                .attr('stroke', '#0f172a')
                .attr('stroke-width', 2)
                .style('cursor', 'pointer')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));
            
            // Add labels if configured
            if (config.show_labels) {{
                const labels = g.append('g')
                    .selectAll('text')
                    .data(nodes)
                    .join('text')
                    .attr('class', 'node-label')
                    .attr('dx', 15)
                    .attr('dy', 4)
                    .text(d => d.label || d.id);
                
                simulation.on('tick', () => {{
                    link
                        .attr('x1', d => d.source.x)
                        .attr('y1', d => d.source.y)
                        .attr('x2', d => d.target.x)
                        .attr('y2', d => d.target.y);
                    
                    node
                        .attr('cx', d => d.x)
                        .attr('cy', d => d.y);
                    
                    labels
                        .attr('x', d => d.x)
                        .attr('y', d => d.y);
                }});
            }} else {{
                simulation.on('tick', () => {{
                    link
                        .attr('x1', d => d.source.x)
                        .attr('y1', d => d.source.y)
                        .attr('x2', d => d.target.x)
                        .attr('y2', d => d.target.y);
                    
                    node
                        .attr('cx', d => d.x)
                        .attr('cy', d => d.y);
                }});
            }}
            
            // Tooltip
            const tooltip = d3.select('#tooltip');
            
            node.on('mouseover', (event, d) => {{
                let riskBadge = '';
                if (d.risk_score !== undefined) {{
                    let riskLevel = 'low';
                    let riskColor = config.risk_colors.low;
                    if (d.risk_score >= 0.75) {{ riskLevel = 'CRITICAL'; riskColor = config.risk_colors.critical; }}
                    else if (d.risk_score >= 0.5) {{ riskLevel = 'HIGH'; riskColor = config.risk_colors.high; }}
                    else if (d.risk_score >= 0.25) {{ riskLevel = 'MEDIUM'; riskColor = config.risk_colors.medium; }}
                    else {{ riskLevel = 'LOW'; }}
                    riskBadge = `<span class="risk-badge" style="background: ${{riskColor}}">${{riskLevel}}</span>`;
                }}
                
                tooltip.html(`
                    <h4>${{d.label || d.id}}</h4>
                    <div class="tooltip-row">
                        <span class="tooltip-label">Type:</span>
                        <span>${{d.type}}</span>
                    </div>
                    ${{d.country ? `<div class="tooltip-row"><span class="tooltip-label">Country:</span><span>${{d.country}}</span></div>` : ''}}
                    ${{d.risk_score !== undefined ? `<div class="tooltip-row"><span class="tooltip-label">Risk:</span>${{riskBadge}} ${{(d.risk_score * 100).toFixed(0)}}%</div>` : ''}}
                    ${{d.dependent_count ? `<div class="tooltip-row"><span class="tooltip-label">Dependents:</span><span>${{d.dependent_count}}</span></div>` : ''}}
                `)
                .style('left', (event.pageX + 15) + 'px')
                .style('top', (event.pageY - 10) + 'px')
                .style('opacity', 1);
            }})
            .on('mouseout', () => tooltip.style('opacity', 0));
            
            // Build legend
            const nodeTypes = [...new Set(nodes.map(n => n.type))];
            const legend = d3.select('#legend');
            
            nodeTypes.forEach(type => {{
                const item = legend.append('div').attr('class', 'legend-item');
                item.append('div')
                    .attr('class', 'legend-color')
                    .style('background', config.node_colors[type] || '#6b7280');
                item.append('span').text(type.replace('_', ' '));
            }});
            
            // Drag functions
            function dragstarted(event) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }}
            
            function dragged(event) {{
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }}
            
            function dragended(event) {{
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }}
            
            // Animate reveal if configured
            if (config.animate_reveal) {{
                node.style('opacity', 0);
                link.style('opacity', 0);
                
                node.filter(d => d.type !== 'EXTERNAL_SUPPLIER')
                    .transition()
                    .duration(500)
                    .style('opacity', 1);
                
                link.filter(d => !d.predicted)
                    .transition()
                    .duration(500)
                    .style('opacity', 1);
                
                setTimeout(() => {{
                    node.filter(d => d.type === 'EXTERNAL_SUPPLIER')
                        .transition()
                        .duration(800)
                        .style('opacity', 1);
                    
                    link.filter(d => d.predicted)
                        .transition()
                        .duration(800)
                        .style('opacity', 1);
                }}, 1500);
            }}
        </script>
    </body>
    </html>
    """
    
    components.html(html, height=height)


def render_ego_graph(center_node: dict, connected_nodes: list, edges: list, 
                     config: dict = None, height: int = 500):
    """
    Render an ego-centric graph focused on a single node and its connections.
    Ideal for showing bottleneck dependencies.
    
    Args:
        center_node: Dict with keys: id, label, type, risk_score
        connected_nodes: List of nodes connected to the center
        edges: List of edges connecting to center node
        config: Optional configuration
        height: Height in pixels
    """
    # Add position hints for layout
    center_node['fx'] = 400  # Fix center position
    center_node['fy'] = height / 2
    center_node['is_center'] = True
    
    all_nodes = [center_node] + connected_nodes
    
    default_config = {
        "show_labels": True,
        "highlight_risks": True,
        "center_color": "#dc2626",  # Red for the bottleneck
        "node_colors": {
            "SUPPLIER": "#3b82f6",
            "PART": "#8b5cf6",
            "EXTERNAL_SUPPLIER": "#f59e0b",
        }
    }
    
    if config:
        default_config.update(config)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                overflow: hidden;
            }}
            #ego-container {{
                width: 100%;
                height: {height}px;
            }}
            .center-label {{
                font-size: 14px;
                font-weight: 700;
                fill: #f8fafc;
                text-anchor: middle;
            }}
            .node-label {{
                font-size: 10px;
                fill: #cbd5e1;
                pointer-events: none;
            }}
            .center-ring {{
                fill: none;
                stroke: #dc2626;
                stroke-width: 3;
                opacity: 0.6;
            }}
            @keyframes pulse {{
                0% {{ stroke-opacity: 0.6; stroke-width: 3; }}
                50% {{ stroke-opacity: 1; stroke-width: 5; }}
                100% {{ stroke-opacity: 0.6; stroke-width: 3; }}
            }}
            .pulse {{
                animation: pulse 2s infinite;
            }}
        </style>
    </head>
    <body>
        <div id="ego-container"></div>
        <script>
            const nodes = {json.dumps(all_nodes)};
            const links = {json.dumps(edges)};
            const config = {json.dumps(default_config)};
            
            const width = document.getElementById('ego-container').clientWidth;
            const height = {height};
            const centerX = width / 2;
            const centerY = height / 2;
            
            const svg = d3.select('#ego-container')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            // Radial layout for connected nodes
            const radius = Math.min(width, height) / 2 - 80;
            const angleStep = (2 * Math.PI) / (nodes.length - 1);
            
            nodes.forEach((node, i) => {{
                if (node.is_center) {{
                    node.x = centerX;
                    node.y = centerY;
                }} else {{
                    const angle = angleStep * (i - 1) - Math.PI / 2;
                    node.x = centerX + radius * Math.cos(angle);
                    node.y = centerY + radius * Math.sin(angle);
                }}
            }});
            
            // Draw links
            svg.append('g')
                .selectAll('line')
                .data(links)
                .join('line')
                .attr('x1', d => nodes.find(n => n.id === d.source)?.x || centerX)
                .attr('y1', d => nodes.find(n => n.id === d.source)?.y || centerY)
                .attr('x2', d => nodes.find(n => n.id === d.target)?.x || centerX)
                .attr('y2', d => nodes.find(n => n.id === d.target)?.y || centerY)
                .attr('stroke', '#475569')
                .attr('stroke-width', 2)
                .attr('stroke-dasharray', d => d.predicted ? '4,4' : 'none');
            
            // Pulsing ring around center
            svg.append('circle')
                .attr('class', 'center-ring pulse')
                .attr('cx', centerX)
                .attr('cy', centerY)
                .attr('r', 35);
            
            // Draw nodes
            svg.append('g')
                .selectAll('circle')
                .data(nodes)
                .join('circle')
                .attr('cx', d => d.x)
                .attr('cy', d => d.y)
                .attr('r', d => d.is_center ? 28 : 16)
                .attr('fill', d => {{
                    if (d.is_center) return config.center_color;
                    return config.node_colors[d.type] || '#6b7280';
                }})
                .attr('stroke', '#0f172a')
                .attr('stroke-width', 2);
            
            // Center label
            const centerNode = nodes.find(n => n.is_center);
            svg.append('text')
                .attr('class', 'center-label')
                .attr('x', centerX)
                .attr('y', centerY + 50)
                .text(centerNode.label || centerNode.id);
            
            // Connected node labels
            svg.append('g')
                .selectAll('text')
                .data(nodes.filter(n => !n.is_center))
                .join('text')
                .attr('class', 'node-label')
                .attr('x', d => d.x)
                .attr('y', d => d.y + 28)
                .attr('text-anchor', 'middle')
                .text(d => (d.label || d.id).substring(0, 20));
            
            // Dependent count badge
            svg.append('text')
                .attr('x', centerX)
                .attr('y', centerY + 5)
                .attr('text-anchor', 'middle')
                .attr('fill', '#fff')
                .attr('font-size', '16px')
                .attr('font-weight', 'bold')
                .text(nodes.length - 1);
        </script>
    </body>
    </html>
    """
    
    components.html(html, height=height)

