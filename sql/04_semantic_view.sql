-- 04_semantic_view.sql - Create Semantic View for Cortex Analyst
-- Called by deploy.sh after UDF is created
-- Uses session variables: PROJECT_ROLE, FULL_PREFIX, PROJECT_SCHEMA

USE ROLE IDENTIFIER($PROJECT_ROLE);
USE DATABASE IDENTIFIER($FULL_PREFIX);
USE SCHEMA IDENTIFIER($PROJECT_SCHEMA);

-- Create stage for semantic models
CREATE STAGE IF NOT EXISTS SEMANTIC_MODELS
  DIRECTORY = (ENABLE = TRUE);

-- Note: YAML file must be uploaded before running 05_cortex_agent.sql
-- The deploy.sh script handles the upload automatically

SELECT 'SEMANTIC_MODELS stage created. Ready for YAML upload.' as STATUS;
