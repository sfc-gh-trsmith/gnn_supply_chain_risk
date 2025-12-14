-- =============================================================================
-- GNN Supply Chain Risk - Schema-Level Setup
-- =============================================================================
-- This script creates schema-level Snowflake objects:
--   - Stages
--   - Tables (ERP data, trade data, GNN outputs)
--   - Views
--   - File formats
--
-- Prerequisites:
--   - Database and schema must exist (created by 01_account_setup.sql)
--   - Must be run with project role, database, schema, and warehouse set
-- =============================================================================

-- =============================================================================
-- 1. Create Stages
-- =============================================================================
CREATE STAGE IF NOT EXISTS MODELS_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for ML models and notebooks';

CREATE STAGE IF NOT EXISTS DATA_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for data files';

-- =============================================================================
-- 2. Create Tables - ERP Data (Internal Backbone)
-- =============================================================================

-- Vendor Master (SAP LFA1 equivalent)
-- Represents Tier 1 suppliers in the supply chain
CREATE TABLE IF NOT EXISTS VENDORS (
    VENDOR_ID VARCHAR(20) PRIMARY KEY,
    NAME VARCHAR(255) NOT NULL,
    COUNTRY_CODE VARCHAR(3) NOT NULL,  -- ISO 3166-1 alpha-3 codes
    CITY VARCHAR(100),
    PHONE VARCHAR(50),
    TIER NUMBER DEFAULT 1,
    FINANCIAL_HEALTH_SCORE FLOAT DEFAULT 0.5,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Vendor master data - known Tier 1 suppliers from ERP';

-- Material Master (SAP MARA equivalent)
-- Represents parts and products in the BOM hierarchy
CREATE TABLE IF NOT EXISTS MATERIALS (
    MATERIAL_ID VARCHAR(20) PRIMARY KEY,
    DESCRIPTION VARCHAR(255) NOT NULL,
    MATERIAL_GROUP VARCHAR(10) NOT NULL,  -- RAW, SEMI, FIN (validated at application level)
    UNIT_OF_MEASURE VARCHAR(10) DEFAULT 'PC',
    CRITICALITY_SCORE FLOAT DEFAULT 0.5,
    INVENTORY_DAYS NUMBER DEFAULT 30,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Material master - parts and products hierarchy';

-- Purchase Orders (SAP EKPO equivalent)
-- Represents the known supplier-to-part relationships
CREATE TABLE IF NOT EXISTS PURCHASE_ORDERS (
    PO_ID VARCHAR(20) PRIMARY KEY,
    VENDOR_ID VARCHAR(20) NOT NULL,
    MATERIAL_ID VARCHAR(20) NOT NULL,
    QUANTITY NUMBER NOT NULL,
    UNIT_PRICE FLOAT NOT NULL,
    ORDER_DATE DATE NOT NULL,
    DELIVERY_DATE DATE,
    STATUS VARCHAR(20) DEFAULT 'OPEN',
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (VENDOR_ID) REFERENCES VENDORS(VENDOR_ID),
    FOREIGN KEY (MATERIAL_ID) REFERENCES MATERIALS(MATERIAL_ID)
)
COMMENT = 'Purchase orders - known supplier to part edges';

-- Bill of Materials (SAP STPO equivalent)
-- Represents part-to-part assembly relationships
CREATE TABLE IF NOT EXISTS BILL_OF_MATERIALS (
    BOM_ID VARCHAR(20) PRIMARY KEY,
    PARENT_MATERIAL_ID VARCHAR(20) NOT NULL,
    CHILD_MATERIAL_ID VARCHAR(20) NOT NULL,
    QUANTITY_PER_UNIT FLOAT NOT NULL DEFAULT 1.0,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (PARENT_MATERIAL_ID) REFERENCES MATERIALS(MATERIAL_ID),
    FOREIGN KEY (CHILD_MATERIAL_ID) REFERENCES MATERIALS(MATERIAL_ID)
    -- Note: PARENT_MATERIAL_ID != CHILD_MATERIAL_ID validated at application level
)
COMMENT = 'Bill of materials - part assembly hierarchy';

-- =============================================================================
-- 3. Create Tables - External Trade Data (Intelligence Layer)
-- =============================================================================

-- Trade Data / Bills of Lading
-- External data revealing hidden Tier 2+ relationships
CREATE TABLE IF NOT EXISTS TRADE_DATA (
    BOL_ID VARCHAR(20) PRIMARY KEY,
    SHIPPER_NAME VARCHAR(255) NOT NULL,
    SHIPPER_COUNTRY VARCHAR(3),  -- ISO 3166-1 alpha-3 codes
    CONSIGNEE_NAME VARCHAR(255) NOT NULL,
    CONSIGNEE_COUNTRY VARCHAR(3),  -- ISO 3166-1 alpha-3 codes
    HS_CODE VARCHAR(10) NOT NULL,
    HS_DESCRIPTION VARCHAR(255),
    SHIP_DATE DATE NOT NULL,
    WEIGHT_KG FLOAT,
    VALUE_USD FLOAT,
    PORT_OF_ORIGIN VARCHAR(100),
    PORT_OF_DESTINATION VARCHAR(100),
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'External trade data - bills of lading for Tier 2+ inference';

-- Region Risk Data
-- Risk scores by geographic region
CREATE TABLE IF NOT EXISTS REGIONS (
    REGION_CODE VARCHAR(3) PRIMARY KEY,  -- ISO 3166-1 alpha-3 codes
    REGION_NAME VARCHAR(100) NOT NULL,
    BASE_RISK_SCORE FLOAT DEFAULT 0.0,
    GEOPOLITICAL_RISK FLOAT DEFAULT 0.0,
    NATURAL_DISASTER_RISK FLOAT DEFAULT 0.0,
    INFRASTRUCTURE_SCORE FLOAT DEFAULT 0.5,
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Geographic region risk factors';

-- =============================================================================
-- 4. Create Tables - GNN Model Outputs
-- =============================================================================

-- Risk Scores
-- Output from GNN risk propagation
CREATE TABLE IF NOT EXISTS RISK_SCORES (
    SCORE_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    NODE_ID VARCHAR(50) NOT NULL,
    NODE_TYPE VARCHAR(20) NOT NULL,  -- SUPPLIER, PART, REGION
    RISK_SCORE FLOAT NOT NULL,  -- Range 0-1, validated at application level
    RISK_CATEGORY VARCHAR(20),  -- LOW, MEDIUM, HIGH, CRITICAL
    CONFIDENCE FLOAT,
    EMBEDDING ARRAY,  -- Node embedding vector from GNN
    CONTRIBUTING_FACTORS VARIANT,  -- JSON with risk breakdown
    MODEL_VERSION VARCHAR(50),
    CALCULATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'GNN-computed risk scores for all supply chain nodes';

-- Predicted Links
-- Inferred Tier 2+ supplier relationships from link prediction
CREATE TABLE IF NOT EXISTS PREDICTED_LINKS (
    LINK_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    SOURCE_NODE_ID VARCHAR(50) NOT NULL,
    SOURCE_NODE_TYPE VARCHAR(20) NOT NULL,
    TARGET_NODE_ID VARCHAR(50) NOT NULL,
    TARGET_NODE_TYPE VARCHAR(20) NOT NULL,
    LINK_TYPE VARCHAR(50) NOT NULL,  -- INFERRED_SUPPLIES, INFERRED_SOURCES_FROM
    PROBABILITY FLOAT NOT NULL,  -- Range 0-1, validated at application level
    EVIDENCE_STRENGTH VARCHAR(20),  -- WEAK, MODERATE, STRONG
    SUPPORTING_DATA VARIANT,  -- JSON with evidence details
    MODEL_VERSION VARCHAR(50),
    PREDICTED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'GNN-predicted hidden supplier relationships';

-- Single Points of Failure
-- Identified bottlenecks in the supply chain
CREATE TABLE IF NOT EXISTS BOTTLENECKS (
    BOTTLENECK_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    NODE_ID VARCHAR(50) NOT NULL,
    NODE_TYPE VARCHAR(20) NOT NULL,
    DEPENDENT_COUNT NUMBER NOT NULL,
    DEPENDENT_NODES ARRAY,
    IMPACT_SCORE FLOAT NOT NULL,
    DESCRIPTION VARCHAR(500),
    MITIGATION_STATUS VARCHAR(20) DEFAULT 'UNMITIGATED',
    IDENTIFIED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Identified single points of failure in supply chain';

-- =============================================================================
-- 5. Create Views for Analytics
-- =============================================================================

-- Supplier Risk Overview
CREATE OR REPLACE VIEW VW_SUPPLIER_RISK AS
SELECT 
    v.VENDOR_ID,
    v.NAME AS VENDOR_NAME,
    v.COUNTRY_CODE,
    v.TIER,
    r.BASE_RISK_SCORE AS REGION_RISK,
    rs.RISK_SCORE AS GNN_RISK_SCORE,
    rs.RISK_CATEGORY,
    rs.CONFIDENCE,
    COALESCE(po_stats.TOTAL_ORDERS, 0) AS TOTAL_ORDERS,
    COALESCE(po_stats.TOTAL_VALUE, 0) AS TOTAL_ORDER_VALUE
FROM VENDORS v
LEFT JOIN REGIONS r ON v.COUNTRY_CODE = r.REGION_CODE
LEFT JOIN RISK_SCORES rs ON v.VENDOR_ID = rs.NODE_ID AND rs.NODE_TYPE = 'SUPPLIER'
LEFT JOIN (
    SELECT VENDOR_ID, COUNT(*) AS TOTAL_ORDERS, SUM(QUANTITY * UNIT_PRICE) AS TOTAL_VALUE
    FROM PURCHASE_ORDERS
    GROUP BY VENDOR_ID
) po_stats ON v.VENDOR_ID = po_stats.VENDOR_ID;

-- Material Risk Overview
CREATE OR REPLACE VIEW VW_MATERIAL_RISK AS
SELECT 
    m.MATERIAL_ID,
    m.DESCRIPTION,
    m.MATERIAL_GROUP,
    m.CRITICALITY_SCORE,
    rs.RISK_SCORE AS GNN_RISK_SCORE,
    rs.RISK_CATEGORY,
    COALESCE(supplier_count.NUM_SUPPLIERS, 0) AS NUM_SUPPLIERS,
    COALESCE(supplier_count.AVG_SUPPLIER_RISK, 0) AS AVG_SUPPLIER_RISK
FROM MATERIALS m
LEFT JOIN RISK_SCORES rs ON m.MATERIAL_ID = rs.NODE_ID AND rs.NODE_TYPE = 'PART'
LEFT JOIN (
    SELECT 
        po.MATERIAL_ID,
        COUNT(DISTINCT po.VENDOR_ID) AS NUM_SUPPLIERS,
        AVG(COALESCE(rs2.RISK_SCORE, 0.5)) AS AVG_SUPPLIER_RISK
    FROM PURCHASE_ORDERS po
    LEFT JOIN RISK_SCORES rs2 ON po.VENDOR_ID = rs2.NODE_ID AND rs2.NODE_TYPE = 'SUPPLIER'
    GROUP BY po.MATERIAL_ID
) supplier_count ON m.MATERIAL_ID = supplier_count.MATERIAL_ID;

-- Predicted Hidden Dependencies
CREATE OR REPLACE VIEW VW_HIDDEN_DEPENDENCIES AS
SELECT 
    pl.LINK_ID,
    pl.SOURCE_NODE_ID,
    pl.SOURCE_NODE_TYPE,
    CASE 
        WHEN pl.SOURCE_NODE_TYPE = 'SUPPLIER' THEN v1.NAME
        ELSE pl.SOURCE_NODE_ID
    END AS SOURCE_NAME,
    pl.TARGET_NODE_ID,
    pl.TARGET_NODE_TYPE,
    CASE 
        WHEN pl.TARGET_NODE_TYPE = 'SUPPLIER' THEN v2.NAME
        ELSE pl.TARGET_NODE_ID
    END AS TARGET_NAME,
    pl.PROBABILITY,
    pl.EVIDENCE_STRENGTH,
    pl.PREDICTED_AT
FROM PREDICTED_LINKS pl
LEFT JOIN VENDORS v1 ON pl.SOURCE_NODE_ID = v1.VENDOR_ID
LEFT JOIN VENDORS v2 ON pl.TARGET_NODE_ID = v2.VENDOR_ID
WHERE pl.PROBABILITY >= 0.5
ORDER BY pl.PROBABILITY DESC;

-- High Risk Summary for Executive Dashboard
CREATE OR REPLACE VIEW VW_RISK_SUMMARY AS
SELECT 
    'SUPPLIERS' AS CATEGORY,
    COUNT(*) AS TOTAL_COUNT,
    SUM(CASE WHEN RISK_CATEGORY = 'CRITICAL' THEN 1 ELSE 0 END) AS CRITICAL_COUNT,
    SUM(CASE WHEN RISK_CATEGORY = 'HIGH' THEN 1 ELSE 0 END) AS HIGH_COUNT,
    SUM(CASE WHEN RISK_CATEGORY = 'MEDIUM' THEN 1 ELSE 0 END) AS MEDIUM_COUNT,
    SUM(CASE WHEN RISK_CATEGORY = 'LOW' THEN 1 ELSE 0 END) AS LOW_COUNT,
    AVG(RISK_SCORE) AS AVG_RISK_SCORE
FROM RISK_SCORES WHERE NODE_TYPE = 'SUPPLIER'
UNION ALL
SELECT 
    'PARTS' AS CATEGORY,
    COUNT(*) AS TOTAL_COUNT,
    SUM(CASE WHEN RISK_CATEGORY = 'CRITICAL' THEN 1 ELSE 0 END) AS CRITICAL_COUNT,
    SUM(CASE WHEN RISK_CATEGORY = 'HIGH' THEN 1 ELSE 0 END) AS HIGH_COUNT,
    SUM(CASE WHEN RISK_CATEGORY = 'MEDIUM' THEN 1 ELSE 0 END) AS MEDIUM_COUNT,
    SUM(CASE WHEN RISK_CATEGORY = 'LOW' THEN 1 ELSE 0 END) AS LOW_COUNT,
    AVG(RISK_SCORE) AS AVG_RISK_SCORE
FROM RISK_SCORES WHERE NODE_TYPE = 'PART';

-- =============================================================================
-- 6. Create File Formats for Data Loading
-- =============================================================================
CREATE FILE FORMAT IF NOT EXISTS CSV_FORMAT
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    NULL_IF = ('NULL', 'null', '')
    EMPTY_FIELD_AS_NULL = TRUE;

-- =============================================================================
-- 7. Display Summary
-- =============================================================================
SELECT 'Schema-level setup completed successfully!' AS STATUS;

-- Show created objects
SHOW TABLES;
SHOW VIEWS;
SHOW STAGES;

