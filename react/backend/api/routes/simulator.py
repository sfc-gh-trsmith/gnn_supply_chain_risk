from fastapi import APIRouter
from pydantic import BaseModel
from ..database import get_cursor, query_to_dicts
import math

router = APIRouter(prefix="/simulator", tags=["simulator"])

class ShockRequest(BaseModel):
    region: str
    intensity: float = 0.5

@router.get("/propagation/{region}")
def get_propagation_data(region: str, intensity: float = 0.5):
    with get_cursor() as cursor:
        region_info = query_to_dicts(cursor, """
            SELECT REGION_CODE, REGION_NAME, BASE_RISK_SCORE
            FROM REGIONS WHERE REGION_CODE = %s
        """, (region,))
        
        region_name = region_info[0]['region_name'] if region_info else region
        
        vendors = query_to_dicts(cursor, """
            SELECT 
                v.VENDOR_ID as id,
                v.NAME as name,
                v.COUNTRY_CODE as country,
                v.TIER as tier,
                COALESCE(rs.RISK_SCORE, 0.5) as risk_score,
                COALESCE(rs.RISK_CATEGORY, 'MEDIUM') as risk_category
            FROM VENDORS v
            LEFT JOIN RISK_SCORES rs ON rs.NODE_ID = v.VENDOR_ID
        """)
        
        affected_vendors = [v for v in vendors if v['country'] == region]
        affected_ids = {v['id'] for v in affected_vendors}
        
        downstream_links = query_to_dicts(cursor, """
            SELECT DISTINCT VENDOR_ID as source, MATERIAL_ID as target 
            FROM PURCHASE_ORDERS
        """)
        
        materials_affected = set()
        for link in downstream_links:
            if link['source'] in affected_ids:
                materials_affected.add(link['target'])
        
        materials = query_to_dicts(cursor, """
            SELECT 
                MATERIAL_ID as id,
                DESCRIPTION as name,
                CRITICALITY_SCORE as criticality
            FROM MATERIALS
        """)
        
        vendors_with_materials = set()
        for link in downstream_links:
            if link['target'] in materials_affected and link['source'] not in affected_ids:
                vendors_with_materials.add(link['source'])
        
        step0 = [v['id'] for v in affected_vendors]
        step1 = list(materials_affected)
        step2 = list(vendors_with_materials)
        
        nodes = []
        edges = []
        
        num_affected = len(affected_vendors)
        center_x = 1200
        center_y = 1200
        
        region_node = {
            "id": f"region_{region}",
            "type": "region",
            "position": {"x": center_x, "y": center_y},
            "data": {
                "label": region_name,
                "region_code": region,
                "base_risk": float(region_info[0]['base_risk_score']) if region_info else 0.5,
                "vendor_count": num_affected,
                "is_source": True
            }
        }
        nodes.append(region_node)
        
        radius1 = 400
        for i, v in enumerate(affected_vendors):
            angle = (2 * math.pi * i) / max(num_affected, 1) - math.pi / 2
            nodes.append({
                "id": v['id'],
                "type": "vendor",
                "position": {"x": center_x + radius1 * math.cos(angle), "y": center_y + radius1 * math.sin(angle)},
                "data": {
                    "label": v['name'],
                    "vendor_id": v['id'],
                    "risk_score": float(v['risk_score']),
                    "risk_category": v['risk_category'],
                    "country": v['country'],
                    "tier": v['tier'],
                    "propagation_step": 0
                }
            })
            edges.append({
                "id": f"prop-{region}-{v['id']}",
                "source": f"region_{region}",
                "target": v['id'],
                "type": "propagation",
                "data": {"edge_type": "propagation", "step": 0}
            })
        
        affected_material_list = [m for m in materials if m['id'] in materials_affected]
        radius2 = 700
        num_materials = len(affected_material_list)
        for i, m in enumerate(affected_material_list):
            angle = (2 * math.pi * i) / max(num_materials, 1) - math.pi / 2
            nodes.append({
                "id": m['id'],
                "type": "material",
                "position": {"x": center_x + radius2 * math.cos(angle), "y": center_y + radius2 * math.sin(angle)},
                "data": {
                    "label": m['name'],
                    "material_id": m['id'],
                    "criticality": float(m['criticality'] or 0.5),
                    "propagation_step": 1
                }
            })
        
        for link in downstream_links:
            if link['source'] in affected_ids and link['target'] in materials_affected:
                edges.append({
                    "id": f"prop-{link['source']}-{link['target']}",
                    "source": link['source'],
                    "target": link['target'],
                    "type": "propagation",
                    "data": {"edge_type": "propagation", "step": 1}
                })
        
        secondary_vendors = [v for v in vendors if v['id'] in vendors_with_materials]
        radius3 = 1000
        num_secondary = len(secondary_vendors)
        for i, v in enumerate(secondary_vendors):
            angle = (2 * math.pi * i) / max(num_secondary, 1) - math.pi / 2
            nodes.append({
                "id": v['id'],
                "type": "vendor",
                "position": {"x": center_x + radius3 * math.cos(angle), "y": center_y + radius3 * math.sin(angle)},
                "data": {
                    "label": v['name'],
                    "vendor_id": v['id'],
                    "risk_score": float(v['risk_score']),
                    "risk_category": v['risk_category'],
                    "country": v['country'],
                    "tier": v['tier'],
                    "propagation_step": 2
                }
            })
        
        for link in downstream_links:
            if link['target'] in materials_affected and link['source'] in vendors_with_materials:
                edges.append({
                    "id": f"prop-{link['target']}-{link['source']}",
                    "source": link['target'],
                    "target": link['source'],
                    "type": "propagation",
                    "data": {"edge_type": "propagation", "step": 2}
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "propagation_steps": [
                {"step": 0, "label": f"Initial Shock: {region_name}", "node_ids": step0, "count": len(step0)},
                {"step": 1, "label": "Affected Materials", "node_ids": step1, "count": len(step1)},
                {"step": 2, "label": "Secondary Vendors", "node_ids": step2, "count": len(step2)},
            ],
            "intensity": intensity,
            "region": region,
            "region_name": region_name,
            "total_affected": len(step0) + len(step2)
        }

@router.post("/shock")
def simulate_shock(request: ShockRequest):
    with get_cursor() as cursor:
        affected = query_to_dicts(cursor, """
            SELECT 
                COUNT(DISTINCT v.VENDOR_ID) as affected_vendors,
                ROUND(AVG(rs.RISK_SCORE), 3) as current_avg_risk,
                ROUND(AVG(rs.RISK_SCORE) + (%s * 0.3), 3) as projected_risk,
                ARRAY_AGG(DISTINCT v.NAME) as vendor_names
            FROM VENDORS v
            JOIN RISK_SCORES rs ON rs.NODE_ID = v.VENDOR_ID
            WHERE v.COUNTRY_CODE = %s
        """, (request.intensity, request.region))
        
        if not affected or affected[0]['affected_vendors'] == 0:
            return {
                "affected_vendors": 0,
                "current_avg_risk": 0,
                "projected_risk": 0,
                "risk_increase": 0,
                "vendor_names": []
            }
        
        result = affected[0]
        return {
            "affected_vendors": result['affected_vendors'],
            "current_avg_risk": float(result['current_avg_risk'] or 0),
            "projected_risk": min(1.0, float(result['projected_risk'] or 0)),
            "risk_increase": round((float(result['projected_risk'] or 0) - float(result['current_avg_risk'] or 0)) * 100, 1),
            "vendor_names": result['vendor_names'] or []
        }
