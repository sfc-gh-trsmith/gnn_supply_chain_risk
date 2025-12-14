"""
D3.js Geographic Map Component

World map visualization with supplier locations and trade routes.
"""

import json
import streamlit.components.v1 as components


def render_geo_map(locations: list, routes: list = None, config: dict = None, height: int = 500):
    """
    Render a world map with supplier locations and optional trade routes.
    
    Args:
        locations: List of dicts with keys: id, name, lat, lon, country_code, 
                   risk_score (optional), count (optional for bubble size)
        routes: Optional list of dicts with keys: source_lat, source_lon, 
                target_lat, target_lon, volume (optional)
        config: Optional configuration dict
        height: Height in pixels
    """
    default_config = {
        "show_routes": True,
        "bubble_scale": 1,
        "risk_colors": {
            "critical": "#dc2626",
            "high": "#ea580c",
            "medium": "#ca8a04",
            "low": "#16a34a",
            "default": "#3b82f6"
        }
    }
    
    if config:
        default_config.update(config)
    
    routes = routes or []
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <script src="https://d3js.org/topojson.v3.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: #0f172a;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            #map-container {{
                width: 100%;
                height: {height}px;
                position: relative;
            }}
            .country {{
                fill: #1e293b;
                stroke: #334155;
                stroke-width: 0.5;
            }}
            .country:hover {{
                fill: #334155;
            }}
            .location {{
                stroke: #0f172a;
                stroke-width: 1.5;
                cursor: pointer;
                transition: all 0.2s;
            }}
            .location:hover {{
                stroke-width: 3;
                stroke: #f8fafc;
            }}
            .route {{
                fill: none;
                stroke: #f59e0b;
                stroke-opacity: 0.4;
                stroke-width: 1.5;
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
                z-index: 100;
            }}
            .legend {{
                position: absolute;
                bottom: 20px;
                right: 20px;
                background: rgba(15, 23, 42, 0.9);
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 12px;
                color: #e2e8f0;
                font-size: 12px;
            }}
            .legend-title {{
                font-weight: 600;
                margin-bottom: 8px;
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                margin: 4px 0;
            }}
            .legend-dot {{
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 8px;
            }}
        </style>
    </head>
    <body>
        <div id="map-container">
            <div class="tooltip" id="tooltip"></div>
            <div class="legend">
                <div class="legend-title">Risk Level</div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #dc2626"></div>
                    <span>Critical (≥75%)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #ea580c"></div>
                    <span>High (50-75%)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #ca8a04"></div>
                    <span>Medium (25-50%)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #16a34a"></div>
                    <span>Low (<25%)</span>
                </div>
            </div>
        </div>
        <script>
            const locations = {json.dumps(locations)};
            const routes = {json.dumps(routes)};
            const config = {json.dumps(default_config)};
            
            const container = document.getElementById('map-container');
            const width = container.clientWidth;
            const height = {height};
            
            const svg = d3.select('#map-container')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            // Projection
            const projection = d3.geoNaturalEarth1()
                .scale(width / 5.5)
                .translate([width / 2, height / 2]);
            
            const path = d3.geoPath().projection(projection);
            
            // Load world map
            d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
                .then(world => {{
                    // Draw countries
                    svg.append('g')
                        .selectAll('path')
                        .data(topojson.feature(world, world.objects.countries).features)
                        .join('path')
                        .attr('class', 'country')
                        .attr('d', path);
                    
                    // Draw routes if provided
                    if (config.show_routes && routes.length > 0) {{
                        const routeGenerator = d3.line()
                            .curve(d3.curveBasis);
                        
                        svg.append('g')
                            .selectAll('.route')
                            .data(routes)
                            .join('path')
                            .attr('class', 'route')
                            .attr('d', d => {{
                                const source = projection([d.source_lon, d.source_lat]);
                                const target = projection([d.target_lon, d.target_lat]);
                                // Create curved path
                                const midX = (source[0] + target[0]) / 2;
                                const midY = (source[1] + target[1]) / 2 - 50;
                                return routeGenerator([source, [midX, midY], target]);
                            }})
                            .attr('stroke-width', d => Math.max(1, Math.sqrt(d.volume || 1) / 10));
                    }}
                    
                    // Draw locations
                    const tooltip = d3.select('#tooltip');
                    
                    svg.append('g')
                        .selectAll('.location')
                        .data(locations)
                        .join('circle')
                        .attr('class', 'location')
                        .attr('cx', d => projection([d.lon, d.lat])[0])
                        .attr('cy', d => projection([d.lon, d.lat])[1])
                        .attr('r', d => {{
                            const baseSize = 6;
                            const count = d.count || 1;
                            return Math.min(baseSize + Math.sqrt(count) * config.bubble_scale, 20);
                        }})
                        .attr('fill', d => {{
                            if (d.risk_score === undefined) return config.risk_colors.default;
                            if (d.risk_score >= 0.75) return config.risk_colors.critical;
                            if (d.risk_score >= 0.5) return config.risk_colors.high;
                            if (d.risk_score >= 0.25) return config.risk_colors.medium;
                            return config.risk_colors.low;
                        }})
                        .on('mouseover', (event, d) => {{
                            tooltip.html(`
                                <strong>${{d.name}}</strong><br/>
                                Country: ${{d.country_code}}<br/>
                                ${{d.risk_score !== undefined ? 'Risk: ' + (d.risk_score * 100).toFixed(0) + '%<br/>' : ''}}
                                ${{d.count ? 'Suppliers: ' + d.count : ''}}
                            `)
                            .style('left', (event.pageX + 10) + 'px')
                            .style('top', (event.pageY - 10) + 'px')
                            .style('opacity', 1);
                        }})
                        .on('mouseout', () => tooltip.style('opacity', 0));
                }});
        </script>
    </body>
    </html>
    """
    
    components.html(html, height=height)

