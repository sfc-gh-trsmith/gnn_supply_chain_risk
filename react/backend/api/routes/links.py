from fastapi import APIRouter
from ..database import get_cursor, query_to_dicts

router = APIRouter(prefix="/links", tags=["links"])

@router.get("/predicted")
def get_predicted_links():
    with get_cursor() as cursor:
        return query_to_dicts(cursor, """
            SELECT 
                LINK_ID as link_id,
                SOURCE_NODE_ID as source_node_id,
                SOURCE_NODE_TYPE as source_node_type,
                TARGET_NODE_ID as target_node_id,
                TARGET_NODE_TYPE as target_node_type,
                LINK_TYPE as link_type,
                PROBABILITY as probability,
                EVIDENCE_STRENGTH as evidence_strength
            FROM PREDICTED_LINKS
            ORDER BY PROBABILITY DESC
        """)
