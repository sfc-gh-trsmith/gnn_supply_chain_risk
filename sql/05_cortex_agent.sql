-- 05_cortex_agent.sql - Create Cortex Agent
-- Called by deploy.sh AFTER semantic view is created
-- Uses session variables: PROJECT_ROLE, FULL_PREFIX, PROJECT_SCHEMA, PROJECT_WH

USE ROLE IDENTIFIER($PROJECT_ROLE);
USE DATABASE IDENTIFIER($FULL_PREFIX);
USE SCHEMA IDENTIFIER($PROJECT_SCHEMA);

-- Create Cortex Agent with two tools:
-- 1. SUPPLY_CHAIN_ANALYTICS - Cortex Analyst text-to-SQL via semantic view
-- 2. RISK_SCENARIO_ANALYZER - Custom UDF for scenario analysis
CREATE OR REPLACE CORTEX AGENT SUPPLY_CHAIN_RISK_AGENT
  WAREHOUSES = ($PROJECT_WH)
  TOOLS = (
    SUPPLY_CHAIN_ANALYTICS = (
      TYPE = 'cortex_analyst_tool',
      SEMANTIC_MODEL = '@SEMANTIC_MODELS/supply_chain_risk.yaml'
    ),
    RISK_SCENARIO_ANALYZER = (
      TYPE = 'sql_exec_tool',
      SQL_EXPR = 'SELECT ANALYZE_RISK_SCENARIO(:scenario_type, :target_region, :target_vendor, :shock_intensity)'
    )
  )
  COMMENT = 'Supply Chain Risk Copilot - answers questions using semantic view and scenario analysis UDF';

SELECT 'SUPPLY_CHAIN_RISK_AGENT created.' as STATUS;
