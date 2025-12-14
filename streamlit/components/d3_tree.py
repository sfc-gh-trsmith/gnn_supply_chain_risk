"""
D3.js Collapsible Tree Component

Hierarchical visualization for Bill of Materials and org structures.
"""

import json
import streamlit.components.v1 as components


def render_tree(data: dict, config: dict = None, height: int = 600):
    """
    Render a collapsible tree diagram.
    
    Args:
        data: Hierarchical dict with keys: name, children (list of same structure)
              Optional keys: value, risk_score, type
        config: Optional configuration dict
        height: Height in pixels
    """
    default_config = {
        "orientation": "horizontal",  # horizontal or vertical
        "node_radius": 8,
        "colors": {
            "FIN": "#10b981",    # Finished goods - green
            "SEMI": "#8b5cf6",   # Semi-finished - purple
            "RAW": "#f59e0b",    # Raw materials - amber
            "default": "#6b7280"
        },
        "expand_all": True
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
                overflow: auto;
            }}
            #tree-container {{
                width: 100%;
                min-height: {height}px;
                padding: 20px;
                box-sizing: border-box;
            }}
            .node circle {{
                stroke: #0f172a;
                stroke-width: 2px;
                cursor: pointer;
                transition: all 0.2s;
            }}
            .node circle:hover {{
                stroke: #3b82f6;
                stroke-width: 3px;
            }}
            .node text {{
                font-size: 12px;
                fill: #e2e8f0;
            }}
            .node--internal text {{
                font-weight: 500;
            }}
            .link {{
                fill: none;
                stroke: #475569;
                stroke-width: 1.5px;
            }}
            .node--collapsed circle {{
                fill: #475569 !important;
            }}
            .quantity-badge {{
                font-size: 10px;
                fill: #94a3b8;
            }}
            .type-badge {{
                font-size: 9px;
                fill: #64748b;
                text-transform: uppercase;
            }}
        </style>
    </head>
    <body>
        <div id="tree-container"></div>
        <script>
            const treeData = {json.dumps(data)};
            const config = {json.dumps(default_config)};
            
            const container = document.getElementById('tree-container');
            const width = container.clientWidth;
            const height = {height};
            const margin = {{ top: 40, right: 150, bottom: 40, left: 100 }};
            
            // Create hierarchy
            const root = d3.hierarchy(treeData);
            
            // Calculate tree dimensions based on depth and breadth
            const treeHeight = root.height;
            const leafCount = root.leaves().length;
            const dynamicHeight = Math.max(height, leafCount * 40 + margin.top + margin.bottom);
            const dynamicWidth = Math.max(width, treeHeight * 200 + margin.left + margin.right);
            
            const svg = d3.select('#tree-container')
                .append('svg')
                .attr('width', dynamicWidth)
                .attr('height', dynamicHeight);
            
            const g = svg.append('g')
                .attr('transform', `translate(${{margin.left}},${{margin.top}})`);
            
            // Tree layout
            const tree = d3.tree()
                .size([dynamicHeight - margin.top - margin.bottom, 
                       dynamicWidth - margin.left - margin.right - 100]);
            
            // Initial layout
            let nodes = tree(root);
            
            // Links
            const link = g.selectAll('.link')
                .data(root.links())
                .join('path')
                .attr('class', 'link')
                .attr('d', d3.linkHorizontal()
                    .x(d => d.y)
                    .y(d => d.x));
            
            // Nodes
            const node = g.selectAll('.node')
                .data(root.descendants())
                .join('g')
                .attr('class', d => 'node' + (d.children ? ' node--internal' : ' node--leaf'))
                .attr('transform', d => `translate(${{d.y}},${{d.x}})`);
            
            // Node circles
            node.append('circle')
                .attr('r', config.node_radius)
                .attr('fill', d => {{
                    const type = d.data.type || d.data.material_group;
                    return config.colors[type] || config.colors.default;
                }});
            
            // Node labels
            node.append('text')
                .attr('dy', '0.35em')
                .attr('x', d => d.children ? -15 : 15)
                .attr('text-anchor', d => d.children ? 'end' : 'start')
                .text(d => {{
                    const name = d.data.name || d.data.description || d.data.id;
                    return name.length > 30 ? name.substring(0, 27) + '...' : name;
                }});
            
            // Quantity badges for non-root nodes
            node.filter(d => d.data.quantity)
                .append('text')
                .attr('class', 'quantity-badge')
                .attr('dy', '1.5em')
                .attr('x', d => d.children ? -15 : 15)
                .attr('text-anchor', d => d.children ? 'end' : 'start')
                .text(d => `Qty: ${{d.data.quantity}}`);
            
            // Type badges
            node.filter(d => d.data.type || d.data.material_group)
                .append('text')
                .attr('class', 'type-badge')
                .attr('dy', '-1em')
                .attr('x', d => d.children ? -15 : 15)
                .attr('text-anchor', d => d.children ? 'end' : 'start')
                .text(d => d.data.type || d.data.material_group);
        </script>
    </body>
    </html>
    """
    
    components.html(html, height=height, scrolling=True)

