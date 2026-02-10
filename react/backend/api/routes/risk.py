from fastapi import APIRouter
from ..database import get_cursor, query_to_dicts

router = APIRouter(prefix="/risk", tags=["risk"])

@router.get("/scores")
def get_risk_scores():
    with get_cursor() as cursor:
        return query_to_dicts(cursor, """
            SELECT 
                SCORE_ID as score_id,
                NODE_ID as node_id,
                NODE_TYPE as node_type,
                RISK_SCORE as risk_score,
                RISK_CATEGORY as risk_category,
                CONFIDENCE as confidence
            FROM RISK_SCORES
            ORDER BY RISK_SCORE DESC
        """)

@router.get("/bottlenecks")
def get_bottlenecks():
    with get_cursor() as cursor:
        return query_to_dicts(cursor, """
            SELECT 
                BOTTLENECK_ID as bottleneck_id,
                NODE_ID as node_id,
                NODE_TYPE as node_type,
                DEPENDENT_COUNT as dependent_count,
                IMPACT_SCORE as impact_score,
                DESCRIPTION as description,
                MITIGATION_STATUS as mitigation_status
            FROM BOTTLENECKS
            ORDER BY IMPACT_SCORE DESC
        """)

@router.get("/bottleneck/{node_id}/dependents")
def get_bottleneck_dependents(node_id: str):
    with get_cursor() as cursor:
        return query_to_dicts(cursor, """
            SELECT DISTINCT
                v.VENDOR_ID as vendor_id,
                v.NAME as name,
                v.COUNTRY_CODE as country_code,
                v.CITY as city,
                v.TIER as tier,
                v.FINANCIAL_HEALTH_SCORE as financial_health_score,
                rs.RISK_SCORE as risk_score,
                rs.RISK_CATEGORY as risk_category
            FROM BOTTLENECKS b
            JOIN VENDORS v ON ARRAY_CONTAINS(v.VENDOR_ID::VARIANT, b.DEPENDENT_NODES)
            LEFT JOIN RISK_SCORES rs ON rs.NODE_ID = v.VENDOR_ID
            WHERE b.NODE_ID = %s
            ORDER BY rs.RISK_SCORE DESC NULLS LAST
        """, (node_id,))

@router.get("/distribution")
def get_risk_distribution():
    with get_cursor() as cursor:
        return query_to_dicts(cursor, """
            SELECT 
                RISK_CATEGORY as category,
                COUNT(*) as count
            FROM RISK_SCORES
            GROUP BY RISK_CATEGORY
            ORDER BY 
                CASE RISK_CATEGORY 
                    WHEN 'CRITICAL' THEN 1 
                    WHEN 'HIGH' THEN 2 
                    WHEN 'MEDIUM' THEN 3 
                    WHEN 'LOW' THEN 4 
                END
        """)
