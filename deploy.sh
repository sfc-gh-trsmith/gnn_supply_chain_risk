#!/bin/bash
###############################################################################
# deploy.sh - Deploy GNN Supply Chain Risk Analysis to Snowflake
#
# This script performs one-time deployment:
#   1. Validates prerequisites
#   2. Runs account-level SQL setup (creates role, database, warehouse, compute pool)
#   3. Runs schema-level SQL setup (creates tables, stages, views)
#   4. Uploads pre-generated synthetic data to Snowflake stage
#   5. Loads data into tables
#   6. Deploys notebook to Snowflake
#   7. Deploys Streamlit app
#
# Data files are pre-generated and checked into the repo (data/synthetic/).
# This ensures deterministic demo data without requiring local Python execution.
#
# Usage:
#   ./deploy.sh                     # Use default connection (demo)
#   ./deploy.sh -c prod             # Use specific connection
#   ./deploy.sh --prefix DEV        # Deploy with DEV_ prefix
#   ./deploy.sh --skip-notebook     # Skip notebook deployment
###############################################################################

set -e
set -o pipefail

# Configuration
CONNECTION_NAME="demo"
SKIP_NOTEBOOK=false
SKIP_CORTEX=false
ENV_PREFIX=""
ONLY_COMPONENT=""  # Empty means deploy all

# Project settings (base name - may be prefixed)
PROJECT_PREFIX="GNN_SUPPLY_CHAIN_RISK"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy GNN Supply Chain Risk Analysis to Snowflake.

Options:
  -c, --connection NAME    Snowflake CLI connection name (default: demo)
  -p, --prefix PREFIX      Environment prefix for resources (e.g., DEV, PROD)
  --skip-notebook          Skip notebook deployment
  --skip-cortex            Skip Cortex Agent and Semantic View deployment
  --only-streamlit         Deploy only the Streamlit app (skips all other steps)
  --only-notebook          Deploy only the notebook (skips all other steps)
  --only-data              Upload and load data only (skips SQL setup, notebook, streamlit)
  --only-sql               Run SQL setup only (skips data, notebook, streamlit)
  --only-cortex            Deploy only Cortex components (UDF, semantic view, agent)
  -h, --help               Show this help message

Examples:
  $0                       # Full deployment
  $0 -c prod               # Use 'prod' connection
  $0 --prefix DEV          # Deploy with DEV_ prefix (creates DEV_GNN_SUPPLY_CHAIN_RISK)
  $0 -c prod --prefix PROD # Production deployment with PROD_ prefix
  $0 --only-streamlit      # Redeploy only the Streamlit app
  $0 --only-notebook       # Redeploy only the notebook
  $0 --only-cortex         # Redeploy Cortex Agent and Semantic View
EOF
    exit 0
}

# Error handler
error_exit() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -c|--connection)
            CONNECTION_NAME="$2"
            shift 2
            ;;
        -p|--prefix)
            ENV_PREFIX="$2"
            shift 2
            ;;
        --skip-notebook)
            SKIP_NOTEBOOK=true
            shift
            ;;
        --skip-cortex)
            SKIP_CORTEX=true
            shift
            ;;
        --only-streamlit)
            ONLY_COMPONENT="streamlit"
            shift
            ;;
        --only-notebook)
            ONLY_COMPONENT="notebook"
            shift
            ;;
        --only-data)
            ONLY_COMPONENT="data"
            shift
            ;;
        --only-sql)
            ONLY_COMPONENT="sql"
            shift
            ;;
        --only-cortex)
            ONLY_COMPONENT="cortex"
            shift
            ;;
        *)
            error_exit "Unknown option: $1\nUse --help for usage information"
            ;;
    esac
done

SNOW_CONN="-c $CONNECTION_NAME"

# Compute full prefix (adds underscore only if prefix provided)
if [ -n "$ENV_PREFIX" ]; then
    FULL_PREFIX="${ENV_PREFIX}_${PROJECT_PREFIX}"
else
    FULL_PREFIX="${PROJECT_PREFIX}"
fi

# Derive all resource names
DATABASE="${FULL_PREFIX}"
SCHEMA="${PROJECT_PREFIX}"  # Schema name stays constant (unprefixed)
ROLE="${FULL_PREFIX}_ROLE"
WAREHOUSE="${FULL_PREFIX}_WH"
COMPUTE_POOL="${FULL_PREFIX}_COMPUTE_POOL"
NETWORK_RULE="${FULL_PREFIX}_EGRESS_RULE"
EXTERNAL_ACCESS="${FULL_PREFIX}_EXTERNAL_ACCESS"
NOTEBOOK_NAME="${FULL_PREFIX}_NOTEBOOK"

echo "=================================================="
echo "GNN Supply Chain Risk - Deployment"
echo "=================================================="
echo ""
echo "Configuration:"
echo "  Connection: $CONNECTION_NAME"
if [ -n "$ENV_PREFIX" ]; then
    echo "  Environment Prefix: $ENV_PREFIX"
fi
if [ -n "$ONLY_COMPONENT" ]; then
    echo "  Deploy Only: $ONLY_COMPONENT"
fi
echo "  Database: $DATABASE"
echo "  Schema: $SCHEMA"
echo "  Role: $ROLE"
echo "  Warehouse: $WAREHOUSE"
echo "  Compute Pool: $COMPUTE_POOL"
echo ""

# Helper function to check if a step should run
should_run_step() {
    local step_name="$1"
    # If no specific component requested, run all steps
    if [ -z "$ONLY_COMPONENT" ]; then
        return 0
    fi
    # Check if this step matches the requested component
    case "$ONLY_COMPONENT" in
        sql)
            [[ "$step_name" == "account_sql" || "$step_name" == "schema_sql" ]]
            ;;
        data)
            [[ "$step_name" == "upload_data" || "$step_name" == "load_data" ]]
            ;;
        notebook)
            [[ "$step_name" == "notebook" ]]
            ;;
        streamlit)
            [[ "$step_name" == "streamlit" ]]
            ;;
        cortex)
            [[ "$step_name" == "cortex_udf" || "$step_name" == "semantic_view" || "$step_name" == "cortex_agent" ]]
            ;;
        *)
            return 1
            ;;
    esac
}

###############################################################################
# Step 1: Check Prerequisites
###############################################################################
echo "Step 1: Checking prerequisites..."
echo "------------------------------------------------"

# Check for snow CLI
if ! command -v snow &> /dev/null; then
    error_exit "Snowflake CLI (snow) not found. Install with: pip install snowflake-cli"
fi
echo -e "${GREEN}[OK]${NC} Snowflake CLI found"

# Test Snowflake connection
echo "Testing Snowflake connection..."
if ! snow sql $SNOW_CONN -q "SELECT 1" &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Failed to connect to Snowflake"
    snow connection test $SNOW_CONN 2>&1 || true
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Connection '$CONNECTION_NAME' verified"

# Check required files (SQL setup, notebook, and pre-generated data)
for file in "sql/01_account_setup.sql" "sql/02_schema_setup.sql" "notebooks/gnn_supply_chain_risk.ipynb"; do
    if [ ! -f "$file" ]; then
        error_exit "Required file not found: $file"
    fi
done

# Check pre-generated synthetic data files
DATA_FILES=("vendors.csv" "materials.csv" "bill_of_materials.csv" "purchase_orders.csv" "trade_data.csv" "regions.csv")
for file in "${DATA_FILES[@]}"; do
    if [ ! -f "data/synthetic/$file" ]; then
        error_exit "Pre-generated data file not found: data/synthetic/$file\nRun 'python3 utils/generate_synthetic_data.py' to regenerate data files."
    fi
done
echo -e "${GREEN}[OK]${NC} Required files present"

echo ""

###############################################################################
# Step 2: Run Account-Level SQL Setup
###############################################################################
if should_run_step "account_sql"; then
    echo "Step 2: Running account-level SQL setup..."
    echo "------------------------------------------------"

    # Set session variables and run account-level setup
    # Combine SET statements with SQL file and pipe to snow sql
    {
        echo "-- Set session variables for account-level objects"
        echo "SET FULL_PREFIX = '${FULL_PREFIX}';"
        echo "SET PROJECT_ROLE = '${ROLE}';"
        echo "SET PROJECT_WH = '${WAREHOUSE}';"
        echo "SET PROJECT_COMPUTE_POOL = '${COMPUTE_POOL}';"
        echo "SET PROJECT_SCHEMA = '${SCHEMA}';"
        echo "SET PROJECT_NETWORK_RULE = '${NETWORK_RULE}';"
        echo "SET PROJECT_EXTERNAL_ACCESS = '${EXTERNAL_ACCESS}';"
        echo ""
        cat sql/01_account_setup.sql
    } | snow sql $SNOW_CONN -i

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[OK]${NC} Account-level setup completed"
    else
        error_exit "Account-level SQL setup failed"
    fi

    echo ""
else
    echo "Step 2: Skipped (--only-$ONLY_COMPONENT)"
fi

###############################################################################
# Step 3: Run Schema-Level SQL Setup
###############################################################################
if should_run_step "schema_sql"; then
    echo "Step 3: Running schema-level SQL setup..."
    echo "------------------------------------------------"

    # Switch to project role and run schema-level setup
    {
        echo "USE ROLE ${ROLE};"
        echo "USE DATABASE ${DATABASE};"
        echo "USE SCHEMA ${SCHEMA};"
        echo "USE WAREHOUSE ${WAREHOUSE};"
        echo ""
        cat sql/02_schema_setup.sql
    } | snow sql $SNOW_CONN -i

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[OK]${NC} Schema-level setup completed"
    else
        error_exit "Schema-level SQL setup failed"
    fi

    echo ""
else
    echo "Step 3: Skipped (--only-$ONLY_COMPONENT)"
fi

###############################################################################
# Step 4: Upload Data to Stage
###############################################################################
if should_run_step "upload_data"; then
    echo "Step 4: Uploading pre-generated data to Snowflake stage..."
    echo "------------------------------------------------"

    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        
        -- Upload CSV files
        PUT file://data/synthetic/vendors.csv @DATA_STAGE/raw/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
        PUT file://data/synthetic/materials.csv @DATA_STAGE/raw/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
        PUT file://data/synthetic/bill_of_materials.csv @DATA_STAGE/raw/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
        PUT file://data/synthetic/purchase_orders.csv @DATA_STAGE/raw/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
        PUT file://data/synthetic/trade_data.csv @DATA_STAGE/raw/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
        PUT file://data/synthetic/regions.csv @DATA_STAGE/raw/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
    "

    echo -e "${GREEN}[OK]${NC} Data files uploaded to stage"

    echo ""
else
    echo "Step 4: Skipped (--only-$ONLY_COMPONENT)"
fi

###############################################################################
# Step 5: Load Data into Tables
###############################################################################
if should_run_step "load_data"; then
    echo "Step 5: Loading data into tables..."
    echo "------------------------------------------------"

    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        USE WAREHOUSE ${WAREHOUSE};
        
        -- Load Regions first (no FK dependencies)
        COPY INTO REGIONS (REGION_CODE, REGION_NAME, BASE_RISK_SCORE, GEOPOLITICAL_RISK, NATURAL_DISASTER_RISK, INFRASTRUCTURE_SCORE)
        FROM @DATA_STAGE/raw/regions.csv
        FILE_FORMAT = CSV_FORMAT
        ON_ERROR = 'CONTINUE';
        
        -- Load Vendors
        COPY INTO VENDORS (VENDOR_ID, NAME, COUNTRY_CODE, CITY, PHONE, TIER, FINANCIAL_HEALTH_SCORE)
        FROM @DATA_STAGE/raw/vendors.csv
        FILE_FORMAT = CSV_FORMAT
        ON_ERROR = 'CONTINUE';
        
        -- Load Materials
        COPY INTO MATERIALS (MATERIAL_ID, DESCRIPTION, MATERIAL_GROUP, UNIT_OF_MEASURE, CRITICALITY_SCORE, INVENTORY_DAYS)
        FROM @DATA_STAGE/raw/materials.csv
        FILE_FORMAT = CSV_FORMAT
        ON_ERROR = 'CONTINUE';
        
        -- Load Bill of Materials
        COPY INTO BILL_OF_MATERIALS (BOM_ID, PARENT_MATERIAL_ID, CHILD_MATERIAL_ID, QUANTITY_PER_UNIT)
        FROM @DATA_STAGE/raw/bill_of_materials.csv
        FILE_FORMAT = CSV_FORMAT
        ON_ERROR = 'CONTINUE';
        
        -- Load Purchase Orders
        COPY INTO PURCHASE_ORDERS (PO_ID, VENDOR_ID, MATERIAL_ID, QUANTITY, UNIT_PRICE, ORDER_DATE, DELIVERY_DATE, STATUS)
        FROM @DATA_STAGE/raw/purchase_orders.csv
        FILE_FORMAT = CSV_FORMAT
        ON_ERROR = 'CONTINUE';
        
        -- Load Trade Data
        COPY INTO TRADE_DATA (BOL_ID, SHIPPER_NAME, SHIPPER_COUNTRY, CONSIGNEE_NAME, CONSIGNEE_COUNTRY, HS_CODE, HS_DESCRIPTION, SHIP_DATE, WEIGHT_KG, VALUE_USD, PORT_OF_ORIGIN, PORT_OF_DESTINATION)
        FROM @DATA_STAGE/raw/trade_data.csv
        FILE_FORMAT = CSV_FORMAT
        ON_ERROR = 'CONTINUE';
        
        SELECT 'Data loading complete!' as STATUS;
    "

    echo -e "${GREEN}[OK]${NC} Data loaded into tables"

    echo ""
else
    echo "Step 5: Skipped (--only-$ONLY_COMPONENT)"
fi

###############################################################################
# Step 6: Deploy Notebook
###############################################################################
if should_run_step "notebook" && [ "$SKIP_NOTEBOOK" = false ]; then
    echo "Step 6: Deploying notebook..."
    echo "------------------------------------------------"
    
    # Upload notebook and environment file
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        
        PUT file://notebooks/gnn_supply_chain_risk.ipynb @MODELS_STAGE/notebooks/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
        PUT file://notebooks/environment.yml @MODELS_STAGE/notebooks/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
    "
    
    echo -e "${GREEN}[OK]${NC} Notebook files uploaded"
    
    # Create notebook with external access integration for PyPI
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        
        CREATE OR REPLACE NOTEBOOK ${NOTEBOOK_NAME}
            FROM '@MODELS_STAGE/notebooks/'
            MAIN_FILE = 'gnn_supply_chain_risk.ipynb'
            RUNTIME_NAME = 'SYSTEM\$GPU_RUNTIME'
            COMPUTE_POOL = '${COMPUTE_POOL}'
            QUERY_WAREHOUSE = '${WAREHOUSE}'
            EXTERNAL_ACCESS_INTEGRATIONS = (${EXTERNAL_ACCESS})
            IDLE_AUTO_SHUTDOWN_TIME_SECONDS = 1800
            COMMENT = 'GNN Supply Chain Risk Analysis notebook';
        
        ALTER NOTEBOOK ${NOTEBOOK_NAME} ADD LIVE VERSION FROM LAST;
    "
    
    echo -e "${GREEN}[OK]${NC} Notebook created"
elif [ "$SKIP_NOTEBOOK" = true ]; then
    echo "Step 6: Skipped (--skip-notebook)"
else
    echo "Step 6: Skipped (--only-$ONLY_COMPONENT)"
fi

echo ""

###############################################################################
# Step 7: Deploy Streamlit App
###############################################################################
if should_run_step "streamlit"; then
    echo "Step 7: Deploying Streamlit app..."
    echo "------------------------------------------------"

    # Clean up existing Streamlit app and stage files for fresh deployment
    echo "Cleaning up existing Streamlit deployment..."
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        DROP STREAMLIT IF EXISTS GNN_SUPPLY_CHAIN_RISK_APP;
        REMOVE @streamlit/GNN_SUPPLY_CHAIN_RISK_APP;
    " 2>/dev/null || true
    
    # Clear local bundle cache
    rm -rf streamlit/output/bundle 2>/dev/null || true

    cd streamlit

    snow streamlit deploy \
        $SNOW_CONN \
        --database $DATABASE \
        --schema $SCHEMA \
        --role $ROLE \
        --replace

    cd ..

    echo -e "${GREEN}[OK]${NC} Streamlit app deployed"

    echo ""
else
    echo "Step 7: Skipped (--only-$ONLY_COMPONENT)"
fi

###############################################################################
# Step 8: Deploy Cortex UDF
###############################################################################
if should_run_step "cortex_udf" && [ "$SKIP_CORTEX" = false ]; then
    echo "Step 8: Creating Cortex Risk Analysis UDF..."
    echo "------------------------------------------------"

    {
        echo "SET PROJECT_ROLE = '${ROLE}';"
        echo "SET FULL_PREFIX = '${FULL_PREFIX}';"
        echo "SET PROJECT_SCHEMA = '${SCHEMA}';"
        echo ""
        cat sql/03_cortex_udf.sql
    } | snow sql $SNOW_CONN -i

    echo -e "${GREEN}[OK]${NC} Cortex UDF created"
    echo ""
elif [ "$SKIP_CORTEX" = true ]; then
    echo "Step 8: Skipped (--skip-cortex)"
else
    echo "Step 8: Skipped (--only-$ONLY_COMPONENT)"
fi

###############################################################################
# Step 9: Deploy Semantic View
###############################################################################
if should_run_step "semantic_view" && [ "$SKIP_CORTEX" = false ]; then
    echo "Step 9: Deploying Semantic View..."
    echo "------------------------------------------------"

    # Create semantic models stage
    {
        echo "SET PROJECT_ROLE = '${ROLE}';"
        echo "SET FULL_PREFIX = '${FULL_PREFIX}';"
        echo "SET PROJECT_SCHEMA = '${SCHEMA}';"
        echo ""
        cat sql/04_semantic_view.sql
    } | snow sql $SNOW_CONN -i

    # Upload semantic model YAML
    echo "Uploading semantic model YAML..."
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        PUT file://semantic_models/supply_chain_risk.yaml @SEMANTIC_MODELS/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
    "

    echo -e "${GREEN}[OK]${NC} Semantic model uploaded"
    echo ""
elif [ "$SKIP_CORTEX" = true ]; then
    echo "Step 9: Skipped (--skip-cortex)"
else
    echo "Step 9: Skipped (--only-$ONLY_COMPONENT)"
fi

###############################################################################
# Step 10: Deploy Cortex Agent
###############################################################################
if should_run_step "cortex_agent" && [ "$SKIP_CORTEX" = false ]; then
    echo "Step 10: Creating Cortex Agent..."
    echo "------------------------------------------------"

    {
        echo "SET PROJECT_ROLE = '${ROLE}';"
        echo "SET FULL_PREFIX = '${FULL_PREFIX}';"
        echo "SET PROJECT_SCHEMA = '${SCHEMA}';"
        echo "SET PROJECT_WH = '${WAREHOUSE}';"
        echo ""
        cat sql/05_cortex_agent.sql
    } | snow sql $SNOW_CONN -i

    echo -e "${GREEN}[OK]${NC} Cortex Agent created"
    echo ""
elif [ "$SKIP_CORTEX" = true ]; then
    echo "Step 10: Skipped (--skip-cortex)"
else
    echo "Step 10: Skipped (--only-$ONLY_COMPONENT)"
fi

###############################################################################
# Summary
###############################################################################
echo ""
echo "=================================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=================================================="
echo ""

if [ -n "$ONLY_COMPONENT" ]; then
    echo "Deployed component: $ONLY_COMPONENT"
    echo ""
else
    echo "Next Steps:"
    echo "  1. Run the GNN notebook to generate risk scores:"
    if [ -n "$ENV_PREFIX" ]; then
        echo "     ./run.sh --prefix ${ENV_PREFIX} main"
    else
        echo "     ./run.sh main"
    fi
    echo ""
    echo "  2. Open the Streamlit dashboard:"
    if [ -n "$ENV_PREFIX" ]; then
        echo "     ./run.sh --prefix ${ENV_PREFIX} streamlit"
    else
        echo "     ./run.sh streamlit"
    fi
    echo ""
    echo "  3. Check status:"
    if [ -n "$ENV_PREFIX" ]; then
        echo "     ./run.sh --prefix ${ENV_PREFIX} status"
    else
        echo "     ./run.sh status"
    fi
    echo ""
    echo "Resources Created:"
    echo "  - Database: $DATABASE"
    echo "  - Schema: $DATABASE.$SCHEMA"
    echo "  - Role: $ROLE"
    echo "  - Warehouse: $WAREHOUSE"
    echo "  - Compute Pool: $COMPUTE_POOL"
    echo "  - Notebook: ${NOTEBOOK_NAME}"
    echo "  - Streamlit App: GNN_SUPPLY_CHAIN_RISK_APP"
    if [ "$SKIP_CORTEX" = false ]; then
        echo "  - Cortex UDF: ANALYZE_RISK_SCENARIO"
        echo "  - Semantic Model: @SEMANTIC_MODELS/supply_chain_risk.yaml"
        echo "  - Cortex Agent: SUPPLY_CHAIN_RISK_AGENT"
    fi
    echo ""
fi
