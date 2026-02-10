from fastapi import APIRouter
from ..database import get_cursor, query_to_dicts

router = APIRouter(prefix="/network", tags=["network"])

@router.get("/graph")
def get_network_graph():
    with get_cursor() as cursor:
        vendors = query_to_dicts(cursor, """
            SELECT 
                v.VENDOR_ID as id,
                v.NAME as label,
                v.COUNTRY_CODE as country,
                v.TIER as tier,
                COALESCE(rs.RISK_SCORE, 0.5) as risk_score,
                COALESCE(rs.RISK_CATEGORY, 'MEDIUM') as risk_category
            FROM VENDORS v
            LEFT JOIN RISK_SCORES rs ON rs.NODE_ID = v.VENDOR_ID
        """)
        
        materials = query_to_dicts(cursor, """
            SELECT 
                MATERIAL_ID as id,
                DESCRIPTION as label,
                CRITICALITY_SCORE as criticality
            FROM MATERIALS
        """)
        
        regions = query_to_dicts(cursor, """
            SELECT 
                r.REGION_CODE as id,
                r.REGION_NAME as label,
                r.BASE_RISK_SCORE as base_risk,
                COUNT(DISTINCT v.VENDOR_ID) as vendor_count
            FROM REGIONS r
            LEFT JOIN VENDORS v ON v.COUNTRY_CODE = r.REGION_CODE
            GROUP BY r.REGION_CODE, r.REGION_NAME, r.BASE_RISK_SCORE
        """)
        
        bottleneck_ids = query_to_dicts(cursor, "SELECT NODE_ID as id FROM BOTTLENECKS")
        bottleneck_set = {b['id'] for b in bottleneck_ids}
        
        external = query_to_dicts(cursor, """
            SELECT DISTINCT
                rs.NODE_ID as id,
                rs.NODE_ID as label,
                rs.RISK_SCORE as risk_score
            FROM RISK_SCORES rs
            WHERE rs.NODE_TYPE = 'EXTERNAL_SUPPLIER'
        """)
        
        nodes = []
        for v in vendors:
            nodes.append({
                "id": v['id'],
                "type": "vendor",
                "position": {"x": 0, "y": 0},
                "data": {
                    "label": v['label'],
                    "vendor_id": v['id'],
                    "risk_score": float(v['risk_score']),
                    "risk_category": v['risk_category'],
                    "country": v['country'],
                    "tier": v['tier']
                }
            })
        
        for m in materials:
            nodes.append({
                "id": m['id'],
                "type": "material",
                "position": {"x": 0, "y": 0},
                "data": {
                    "label": m['label'],
                    "material_id": m['id'],
                    "criticality": float(m['criticality'] or 0.5)
                }
            })
        
        for r in regions:
            nodes.append({
                "id": r['id'],
                "type": "region",
                "position": {"x": 0, "y": 0},
                "data": {
                    "label": r['label'],
                    "region_code": r['id'],
                    "base_risk": float(r['base_risk'] or 0),
                    "vendor_count": r['vendor_count']
                }
            })
        
        for e in external:
            nodes.append({
                "id": e['id'],
                "type": "external",
                "position": {"x": 0, "y": 0},
                "data": {
                    "label": e['label'],
                    "node_id": e['id'],
                    "risk_score": float(e['risk_score']),
                    "is_bottleneck": e['id'] in bottleneck_set
                }
            })
        
        edges = []
        
        po_edges = query_to_dicts(cursor, """
            SELECT DISTINCT VENDOR_ID as source, MATERIAL_ID as target 
            FROM PURCHASE_ORDERS
        """)
        for e in po_edges:
            edges.append({
                "id": f"supplies-{e['source']}-{e['target']}",
                "source": e['source'],
                "target": e['target'],
                "type": "supplies",
                "data": {"edge_type": "supplies"}
            })
        
        for v in vendors:
            edges.append({
                "id": f"located-{v['id']}-{v['country']}",
                "source": v['id'],
                "target": v['country'],
                "type": "located_in",
                "data": {"edge_type": "located_in"}
            })
        
        predicted = query_to_dicts(cursor, """
            SELECT 
                SOURCE_NODE_ID as source,
                TARGET_NODE_ID as target,
                PROBABILITY as probability
            FROM PREDICTED_LINKS
            WHERE PROBABILITY > 0.5
        """)
        for p in predicted:
            edges.append({
                "id": f"predicted-{p['source']}-{p['target']}",
                "source": p['source'],
                "target": p['target'],
                "type": "predicted",
                "data": {"edge_type": "predicted", "probability": float(p['probability'])}
            })
        
        return {"nodes": nodes, "edges": edges}

@router.get("/ego/{node_id}")
def get_ego_graph(node_id: str):
    with get_cursor() as cursor:
        bottleneck = query_to_dicts(cursor, """
            SELECT 
                NODE_ID as id,
                NODE_TYPE as type,
                DEPENDENT_COUNT as dependent_count,
                IMPACT_SCORE as impact_score
            FROM BOTTLENECKS
            WHERE NODE_ID = %s
        """, (node_id,))
        
        if not bottleneck:
            return {"nodes": [], "edges": []}
        
        bn = bottleneck[0]
        
        dependents = query_to_dicts(cursor, """
            SELECT DISTINCT
                v.VENDOR_ID as id,
                v.NAME as label,
                v.COUNTRY_CODE as country,
                COALESCE(rs.RISK_SCORE, 0.5) as risk_score,
                COALESCE(rs.RISK_CATEGORY, 'MEDIUM') as risk_category
            FROM BOTTLENECKS b
            JOIN VENDORS v ON ARRAY_CONTAINS(v.VENDOR_ID::VARIANT, PARSE_JSON(b.DEPENDENT_NODES[0]))
            LEFT JOIN RISK_SCORES rs ON rs.NODE_ID = v.VENDOR_ID
            WHERE b.NODE_ID = %s
        """, (node_id,))
        
        import math
        num_deps = len(dependents)
        center_x = 400
        center_y = 300
        radius = max(250, num_deps * 12)
        
        nodes = [{
            "id": node_id,
            "type": "external",
            "position": {"x": center_x, "y": center_y},
            "data": {
                "label": node_id,
                "node_id": node_id,
                "risk_score": float(bn['impact_score']),
                "is_bottleneck": True
            }
        }]
        
        for i, d in enumerate(dependents):
            angle = (2 * math.pi * i) / max(num_deps, 1) - math.pi / 2
            nodes.append({
                "id": d['id'],
                "type": "vendor",
                "position": {"x": center_x + radius * math.cos(angle), "y": center_y + radius * math.sin(angle)},
                "data": {
                    "label": d['label'],
                    "vendor_id": d['id'],
                    "risk_score": float(d['risk_score']),
                    "risk_category": d['risk_category'],
                    "country": d['country'],
                    "tier": 1
                }
            })
        
        edges = [
            {
                "id": f"dep-{node_id}-{d['id']}",
                "source": node_id,
                "target": d['id'],
                "type": "predicted",
                "data": {"edge_type": "predicted", "probability": 0.9}
            }
            for d in dependents
        ]
        
        return {"nodes": nodes, "edges": edges}
