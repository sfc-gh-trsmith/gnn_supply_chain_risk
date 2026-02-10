from fastapi import APIRouter
from ..database import get_cursor, query_to_dicts, query_one

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/executive")
def get_executive_metrics():
    with get_cursor() as cursor:
        metrics = query_one(cursor, """
            SELECT 
                (SELECT COUNT(*) FROM VENDORS) as total_vendors,
                (SELECT COUNT(*) FROM RISK_SCORES WHERE RISK_CATEGORY = 'CRITICAL') as critical_count,
                (SELECT COUNT(*) FROM RISK_SCORES WHERE RISK_CATEGORY IN ('CRITICAL', 'HIGH')) as high_risk_count,
                (SELECT ROUND(AVG(RISK_SCORE), 3) FROM RISK_SCORES) as avg_risk_score,
                (SELECT COUNT(*) FROM BOTTLENECKS) as total_bottlenecks,
                (SELECT COUNT(*) FROM PREDICTED_LINKS) as predicted_links_count
        """)
        
        avg_risk = float(metrics['avg_risk_score'] or 0)
        critical_penalty = int(metrics['critical_count'] or 0) * 5
        bottleneck_penalty = int(metrics['total_bottlenecks'] or 0) * 2
        portfolio_health = max(0, min(100, (1 - avg_risk) * 100 - critical_penalty - bottleneck_penalty))
        
        return {
            "total_vendors": metrics['total_vendors'],
            "critical_count": metrics['critical_count'],
            "high_risk_count": metrics['high_risk_count'],
            "avg_risk_score": avg_risk,
            "total_bottlenecks": metrics['total_bottlenecks'],
            "predicted_links_count": metrics['predicted_links_count'],
            "portfolio_health": round(portfolio_health, 1)
        }

@router.get("/regional")
def get_regional_risk():
    with get_cursor() as cursor:
        return query_to_dicts(cursor, """
            SELECT 
                r.REGION_CODE as region_code,
                r.REGION_NAME as region_name,
                COUNT(DISTINCT v.VENDOR_ID) as vendor_count,
                ROUND(AVG(rs.RISK_SCORE), 3) as avg_risk,
                COUNT(CASE WHEN rs.RISK_CATEGORY IN ('CRITICAL', 'HIGH') THEN 1 END) as high_risk_count
            FROM REGIONS r
            LEFT JOIN VENDORS v ON v.COUNTRY_CODE = r.REGION_CODE
            LEFT JOIN RISK_SCORES rs ON rs.NODE_ID = v.VENDOR_ID
            GROUP BY r.REGION_CODE, r.REGION_NAME
            HAVING COUNT(DISTINCT v.VENDOR_ID) > 0
            ORDER BY avg_risk DESC NULLS LAST
        """)
