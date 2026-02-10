-- 03_cortex_udf.sql - Create Risk Analysis UDF for Cortex Agent
-- Called by deploy.sh after data is loaded and notebook has run
-- Uses session variables: PROJECT_ROLE, DATABASE, SCHEMA

USE ROLE IDENTIFIER($PROJECT_ROLE);
USE DATABASE IDENTIFIER($FULL_PREFIX);
USE SCHEMA IDENTIFIER($PROJECT_SCHEMA);

CREATE OR REPLACE FUNCTION ANALYZE_RISK_SCENARIO(
    scenario_type VARCHAR,
    target_region VARCHAR DEFAULT NULL,
    target_vendor VARCHAR DEFAULT NULL,
    shock_intensity FLOAT DEFAULT 0.5
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
SELECT OBJECT_CONSTRUCT(
    'scenario_type', scenario_type,
    'target', COALESCE(target_region, target_vendor, 'all'),
    'shock_intensity', shock_intensity,
    'analysis', CASE 
        WHEN scenario_type = 'REGIONAL_DISRUPTION' THEN
            (SELECT OBJECT_CONSTRUCT(
                'affected_vendors', COUNT(DISTINCT v.VENDOR_ID),
                'avg_current_risk', ROUND(AVG(rs.RISK_SCORE), 3),
                'projected_risk', ROUND(LEAST(1.0, AVG(rs.RISK_SCORE) + (shock_intensity * 0.3)), 3),
                'recommendation', CASE 
                    WHEN COUNT(*) > 5 THEN 'High concentration risk - diversify suppliers'
                    ELSE 'Moderate exposure - monitor closely'
                END
            )
            FROM VENDORS v
            JOIN RISK_SCORES rs ON v.VENDOR_ID = rs.NODE_ID
            WHERE v.COUNTRY_CODE = target_region
            )
        WHEN scenario_type = 'VENDOR_FAILURE' THEN
            (SELECT OBJECT_CONSTRUCT(
                'vendor_name', v.NAME,
                'current_risk', rs.RISK_SCORE,
                'dependent_materials', (
                    SELECT COUNT(DISTINCT MATERIAL_ID) 
                    FROM PURCHASE_ORDERS 
                    WHERE VENDOR_ID = target_vendor
                ),
                'bottleneck_impact', COALESCE(b.IMPACT_SCORE, 0),
                'recommendation', CASE
                    WHEN rs.RISK_SCORE > 0.7 THEN 'Immediate action required - identify alternates'
                    WHEN rs.RISK_SCORE > 0.4 THEN 'Develop contingency plan'
                    ELSE 'Low priority - standard monitoring'
                END
            )
            FROM VENDORS v
            JOIN RISK_SCORES rs ON v.VENDOR_ID = rs.NODE_ID
            LEFT JOIN BOTTLENECKS b ON v.VENDOR_ID = b.NODE_ID
            WHERE v.VENDOR_ID = target_vendor
            )
        WHEN scenario_type = 'PORTFOLIO_SUMMARY' THEN
            (SELECT OBJECT_CONSTRUCT(
                'total_vendors', COUNT(DISTINCT VENDOR_ID),
                'critical_count', SUM(CASE WHEN rs.RISK_CATEGORY = 'CRITICAL' THEN 1 ELSE 0 END),
                'high_risk_count', SUM(CASE WHEN rs.RISK_CATEGORY IN ('CRITICAL', 'HIGH') THEN 1 ELSE 0 END),
                'avg_portfolio_risk', ROUND(AVG(rs.RISK_SCORE), 3),
                'total_bottlenecks', (SELECT COUNT(*) FROM BOTTLENECKS),
                'health_score', ROUND((1 - AVG(rs.RISK_SCORE)) * 100, 1)
            )
            FROM VENDORS v
            JOIN RISK_SCORES rs ON v.VENDOR_ID = rs.NODE_ID
            )
        ELSE
            OBJECT_CONSTRUCT('error', 'Unknown scenario type. Use: REGIONAL_DISRUPTION, VENDOR_FAILURE, or PORTFOLIO_SUMMARY')
    END
)
$$;

SELECT 'ANALYZE_RISK_SCENARIO UDF created.' as STATUS;
