"""
D3.js Sankey Diagram Component

Flow visualization for data pipelines and material flows.
"""

import json
import streamlit.components.v1 as components


def render_sankey(nodes: list, links: list, config: dict = None, height: int = 500):
    """
    Render a Sankey diagram showing flows between nodes.
    
    Args:
        nodes: List of dicts with keys: id, name, category (optional)
        links: List of dicts with keys: source, target, value
        config: Optional configuration dict
        height: Height in pixels
    """
    default_config = {
        "node_width": 20,
        "node_padding": 20,
        "colors": {
            "ERP": "#3b82f6",
            "TRADE": "#f59e0b",
            "GRAPH": "#8b5cf6",
            "INFERENCE": "#10b981",
            "default": "#6b7280"
        }
    }
    
    if config:
        default_config.update(config)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            #sankey-container {{
                width: 100%;
                height: {height}px;
            }}
            .node-label {{
                font-size: 12px;
                fill: #e2e8f0;
                font-weight: 500;
            }}
            .link {{
                fill: none;
                stroke-opacity: 0.4;
            }}
            .link:hover {{
                stroke-opacity: 0.7;
            }}
            .value-label {{
                font-size: 10px;
                fill: #94a3b8;
            }}
        </style>
    </head>
    <body>
        <div id="sankey-container"></div>
        <script>
            const nodesData = {json.dumps(nodes)};
            const linksData = {json.dumps(links)};
            const config = {json.dumps(default_config)};
            
            const container = document.getElementById('sankey-container');
            const width = container.clientWidth;
            const height = {height};
            const margin = {{ top: 20, right: 120, bottom: 20, left: 120 }};
            
            const svg = d3.select('#sankey-container')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            const sankey = d3.sankey()
                .nodeId(d => d.id)
                .nodeWidth(config.node_width)
                .nodePadding(config.node_padding)
                .nodeAlign(d3.sankeyLeft)
                .extent([[margin.left, margin.top], [width - margin.right, height - margin.bottom]]);
            
            // Process data
            const graph = sankey({{
                nodes: nodesData.map(d => ({{...d}})),
                links: linksData.map(d => ({{...d}}))
            }});
            
            // Draw links
            const link = svg.append('g')
                .selectAll('.link')
                .data(graph.links)
                .join('path')
                .attr('class', 'link')
                .attr('d', d3.sankeyLinkHorizontal())
                .attr('stroke', d => {{
                    const sourceColor = config.colors[d.source.category] || config.colors.default;
                    return sourceColor;
                }})
                .attr('stroke-width', d => Math.max(1, d.width));
            
            // Draw nodes
            const node = svg.append('g')
                .selectAll('.node')
                .data(graph.nodes)
                .join('rect')
                .attr('class', 'node')
                .attr('x', d => d.x0)
                .attr('y', d => d.y0)
                .attr('height', d => d.y1 - d.y0)
                .attr('width', d => d.x1 - d.x0)
                .attr('fill', d => config.colors[d.category] || config.colors.default)
                .attr('stroke', '#0f172a')
                .attr('stroke-width', 1)
                .attr('rx', 3);
            
            // Node labels
            svg.append('g')
                .selectAll('.node-label')
                .data(graph.nodes)
                .join('text')
                .attr('class', 'node-label')
                .attr('x', d => d.x0 < width / 2 ? d.x0 - 8 : d.x1 + 8)
                .attr('y', d => (d.y0 + d.y1) / 2)
                .attr('dy', '0.35em')
                .attr('text-anchor', d => d.x0 < width / 2 ? 'end' : 'start')
                .text(d => d.name);
            
            // Value labels on links
            svg.append('g')
                .selectAll('.value-label')
                .data(graph.links)
                .join('text')
                .attr('class', 'value-label')
                .attr('x', d => (d.source.x1 + d.target.x0) / 2)
                .attr('y', d => (d.y0 + d.y1) / 2)
                .attr('text-anchor', 'middle')
                .attr('dy', '0.35em')
                .text(d => d.value.toLocaleString());
        </script>
    </body>
    </html>
    """
    
    components.html(html, height=height)

