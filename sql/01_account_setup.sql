-- =============================================================================
-- GNN Supply Chain Risk - Account-Level Setup
-- =============================================================================
-- This script creates account-level Snowflake objects:
--   - Role
--   - Database and Schema
--   - Warehouse
--   - Compute Pool
--   - Network Rules and External Access Integration
--
-- Required Session Variables (set by shell script before executing):
--   $FULL_PREFIX        - Full database/resource prefix (e.g., DEV_GNN_SUPPLY_CHAIN_RISK)
--   $PROJECT_ROLE       - Role name (e.g., DEV_GNN_SUPPLY_CHAIN_RISK_ROLE)
--   $PROJECT_WH         - Warehouse name (e.g., DEV_GNN_SUPPLY_CHAIN_RISK_WH)
--   $PROJECT_COMPUTE_POOL - Compute pool name
--   $PROJECT_SCHEMA     - Schema name (unprefixed, e.g., GNN_SUPPLY_CHAIN_RISK)
--   $PROJECT_NETWORK_RULE - Network rule name
--   $PROJECT_EXTERNAL_ACCESS - External access integration name
-- =============================================================================

-- =============================================================================
-- 1. Create Role (ACCOUNTADMIN)
-- =============================================================================
USE ROLE ACCOUNTADMIN;

CREATE ROLE IF NOT EXISTS IDENTIFIER($PROJECT_ROLE)
    COMMENT = 'Role for GNN Supply Chain Risk project';

-- Grant role to current user
SET MY_USER = (SELECT CURRENT_USER());
GRANT ROLE IDENTIFIER($PROJECT_ROLE) TO USER IDENTIFIER($MY_USER);
GRANT ROLE IDENTIFIER($PROJECT_ROLE) TO ROLE SYSADMIN;

-- =============================================================================
-- 2. Create Database and Schema
-- =============================================================================
CREATE DATABASE IF NOT EXISTS IDENTIFIER($FULL_PREFIX);

-- Build fully qualified schema name for creation
SET FQ_SCHEMA = $FULL_PREFIX || '.' || $PROJECT_SCHEMA;
CREATE SCHEMA IF NOT EXISTS IDENTIFIER($FQ_SCHEMA);

-- Grant ownership on database
GRANT OWNERSHIP ON DATABASE IDENTIFIER($FULL_PREFIX)
    TO ROLE IDENTIFIER($PROJECT_ROLE) COPY CURRENT GRANTS;

-- Grant ownership on schema
GRANT OWNERSHIP ON SCHEMA IDENTIFIER($FQ_SCHEMA)
    TO ROLE IDENTIFIER($PROJECT_ROLE) COPY CURRENT GRANTS;

-- =============================================================================
-- 3. Create Warehouse
-- =============================================================================
CREATE WAREHOUSE IF NOT EXISTS IDENTIFIER($PROJECT_WH)
    WAREHOUSE_SIZE = SMALL
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Warehouse for GNN Supply Chain Risk SQL operations';

GRANT OWNERSHIP ON WAREHOUSE IDENTIFIER($PROJECT_WH)
    TO ROLE IDENTIFIER($PROJECT_ROLE) COPY CURRENT GRANTS;

-- =============================================================================
-- 4. Create Compute Pool for GPU Notebooks
-- =============================================================================
CREATE COMPUTE POOL IF NOT EXISTS IDENTIFIER($PROJECT_COMPUTE_POOL)
    MIN_NODES = 1
    MAX_NODES = 1
    INSTANCE_FAMILY = GPU_NV_S
    AUTO_RESUME = TRUE
    AUTO_SUSPEND_SECS = 600
    COMMENT = 'GPU compute pool for PyTorch Geometric GNN training';

GRANT OWNERSHIP ON COMPUTE POOL IDENTIFIER($PROJECT_COMPUTE_POOL)
    TO ROLE IDENTIFIER($PROJECT_ROLE) COPY CURRENT GRANTS;

-- =============================================================================
-- 5. Create Network Access for PyPI (PyTorch Geometric installation)
-- =============================================================================
-- Switch to database/schema context for network rule creation
USE DATABASE IDENTIFIER($FULL_PREFIX);
USE SCHEMA IDENTIFIER($PROJECT_SCHEMA);

CREATE OR REPLACE NETWORK RULE IDENTIFIER($PROJECT_NETWORK_RULE)
    TYPE = HOST_PORT
    MODE = EGRESS
    VALUE_LIST = (
        'pypi.org:443',
        'files.pythonhosted.org:443',
        'download.pytorch.org:443',
        'data.pyg.org:443'
    )
    COMMENT = 'Required for PyTorch Geometric and dependencies';

-- External access integration references the network rule by name
-- IDENTIFIER() doesn't work inside ALLOWED_NETWORK_RULES, so use EXECUTE IMMEDIATE
SET FQ_NETWORK_RULE = $FULL_PREFIX || '.' || $PROJECT_SCHEMA || '.' || $PROJECT_NETWORK_RULE;

-- Note: Session variables limited to 256 bytes, so keep dynamic SQL short
SET CREATE_EAI_SQL = 'CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION ' || $PROJECT_EXTERNAL_ACCESS ||
    ' ALLOWED_NETWORK_RULES = (' || $FQ_NETWORK_RULE || ') ENABLED = TRUE';
EXECUTE IMMEDIATE $CREATE_EAI_SQL;

SET GRANT_EAI_SQL = 'GRANT USAGE ON INTEGRATION ' || $PROJECT_EXTERNAL_ACCESS || ' TO ROLE ' || $PROJECT_ROLE;
EXECUTE IMMEDIATE $GRANT_EAI_SQL;

-- =============================================================================
-- 6. Grant Cortex LLM Access
-- =============================================================================
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE IDENTIFIER($PROJECT_ROLE);

-- =============================================================================
-- 7. Display Summary
-- =============================================================================
SELECT 'Account-level setup completed successfully!' AS STATUS,
       $FULL_PREFIX AS DATABASE_NAME,
       $PROJECT_ROLE AS ROLE_NAME,
       $PROJECT_WH AS WAREHOUSE_NAME,
       $PROJECT_COMPUTE_POOL AS COMPUTE_POOL_NAME;

