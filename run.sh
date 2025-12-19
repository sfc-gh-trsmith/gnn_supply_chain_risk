#!/bin/bash
###############################################################################
# run.sh - Runtime operations for GNN Supply Chain Risk Analysis
#
# Commands:
#   main       - Execute the GNN notebook
#   status     - Check status of resources
#   notebook   - Get notebook URL
#   streamlit  - Get Streamlit app URL
#
# Usage:
#   ./run.sh main              # Execute notebook
#   ./run.sh status            # Check resource status
#   ./run.sh notebook          # Get notebook URL
#   ./run.sh streamlit         # Get Streamlit URL
#   ./run.sh -c demo  main     # Use specific connection
#   ./run.sh --prefix DEV main # Use DEV_ prefixed resources
###############################################################################

set -e
set -o pipefail

# Configuration
CONNECTION_NAME="demo"
COMMAND=""
ENV_PREFIX=""

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
Usage: $0 [OPTIONS] COMMAND

Runtime operations for GNN Supply Chain Risk Analysis.

Commands:
  main       Execute the GNN notebook to generate risk scores
  status     Check status of Snowflake resources
  notebook   Get URL to open the notebook in Snowsight
  streamlit  Get URL to open the Streamlit dashboard

Options:
  -c, --connection NAME    Snowflake CLI connection name (default: demo)
  -p, --prefix PREFIX      Environment prefix for resources (e.g., DEV, PROD)
  -h, --help               Show this help message

Examples:
  $0 main                  # Run the notebook
  $0 status                # Check resource status
  $0 -c demo streamlit     # Get Streamlit URL using demo connection
  $0 --prefix DEV status   # Check status of DEV_ prefixed resources
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
        main|status|notebook|streamlit)
            COMMAND="$1"
            shift
            ;;
        *)
            error_exit "Unknown option or command: $1\nUse --help for usage information"
            ;;
    esac
done

if [ -z "$COMMAND" ]; then
    usage
fi

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
NOTEBOOK_NAME="${FULL_PREFIX}_NOTEBOOK"

###############################################################################
# Command: main - Execute notebook
###############################################################################
cmd_main() {
    echo "=================================================="
    echo "Executing GNN Notebook"
    echo "=================================================="
    echo ""
    if [ -n "$ENV_PREFIX" ]; then
        echo "Environment Prefix: $ENV_PREFIX"
    fi
    echo "Database: $DATABASE"
    echo "Notebook: $NOTEBOOK_NAME"
    echo ""
    
    # Stop any existing services on the compute pool to ensure capacity
    echo "Stopping any existing services on compute pool..."
    snow sql $SNOW_CONN -q "
        USE ROLE ACCOUNTADMIN;
        ALTER COMPUTE POOL ${COMPUTE_POOL} STOP ALL;
    " 2>/dev/null && echo -e "${GREEN}[OK]${NC} Compute pool cleared" || echo -e "${YELLOW}[WARN]${NC} Could not clear compute pool (may already be empty)"
    echo ""
    
    echo "Starting notebook execution..."
    echo "This may take several minutes on first run (GPU initialization)."
    echo ""
    
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        
        EXECUTE NOTEBOOK ${NOTEBOOK_NAME}();
    "
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}[OK]${NC} Notebook execution complete"
        echo ""
        echo "Verifying results..."
        
        snow sql $SNOW_CONN -q "
            USE ROLE ${ROLE};
            USE DATABASE ${DATABASE};
            USE SCHEMA ${SCHEMA};
            
            SELECT 
                'RISK_SCORES' as TABLE_NAME, COUNT(*) as ROW_COUNT 
            FROM RISK_SCORES
            UNION ALL
            SELECT 
                'PREDICTED_LINKS', COUNT(*) 
            FROM PREDICTED_LINKS
            UNION ALL
            SELECT 
                'BOTTLENECKS', COUNT(*) 
            FROM BOTTLENECKS;
        "
        
        echo ""
        echo "Results written to tables. Open the Streamlit dashboard to explore."
        if [ -n "$ENV_PREFIX" ]; then
            echo "Run: ./run.sh --prefix ${ENV_PREFIX} streamlit"
        else
            echo "Run: ./run.sh streamlit"
        fi
    else
        error_exit "Notebook execution failed"
    fi
}

###############################################################################
# Command: status - Check resource status
###############################################################################
cmd_status() {
    echo "=================================================="
    echo "GNN Supply Chain Risk - Status"
    echo "=================================================="
    echo ""
    if [ -n "$ENV_PREFIX" ]; then
        echo "Environment Prefix: $ENV_PREFIX"
    fi
    echo "Database: $DATABASE"
    echo ""
    
    echo "Checking resources..."
    echo ""
    
    # Check compute pool
    echo "Compute Pool:"
    snow sql $SNOW_CONN -q "
        SHOW COMPUTE POOLS LIKE '${COMPUTE_POOL}';
    " 2>/dev/null || echo "  Not found or no access"
    
    echo ""
    echo "Warehouse:"
    snow sql $SNOW_CONN -q "
        SHOW WAREHOUSES LIKE '${WAREHOUSE}';
    " 2>/dev/null || echo "  Not found or no access"
    
    echo ""
    echo "Table Row Counts:"
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        
        SELECT 'VENDORS' as TABLE_NAME, COUNT(*) as ROWS FROM VENDORS
        UNION ALL SELECT 'MATERIALS', COUNT(*) FROM MATERIALS
        UNION ALL SELECT 'PURCHASE_ORDERS', COUNT(*) FROM PURCHASE_ORDERS
        UNION ALL SELECT 'TRADE_DATA', COUNT(*) FROM TRADE_DATA
        UNION ALL SELECT 'RISK_SCORES', COUNT(*) FROM RISK_SCORES
        UNION ALL SELECT 'PREDICTED_LINKS', COUNT(*) FROM PREDICTED_LINKS
        UNION ALL SELECT 'BOTTLENECKS', COUNT(*) FROM BOTTLENECKS;
    " 2>/dev/null || echo "  Error querying tables"
    
    echo ""
    echo "Notebook:"
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        SHOW NOTEBOOKS LIKE '${NOTEBOOK_NAME}';
    " 2>/dev/null || echo "  Not found"
    
    echo ""
    echo "Streamlit App:"
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        SHOW STREAMLITS LIKE 'GNN_SUPPLY_CHAIN_RISK_APP';
    " 2>/dev/null || echo "  Not found"
}

###############################################################################
# Command: notebook - Get notebook URL
###############################################################################
cmd_notebook() {
    echo "=================================================="
    echo "GNN Supply Chain Risk - Notebook URL"
    echo "=================================================="
    echo ""
    if [ -n "$ENV_PREFIX" ]; then
        echo "Environment Prefix: $ENV_PREFIX"
    fi
    echo ""
    
    # Get account info
    ACCOUNT_INFO=$(snow sql $SNOW_CONN -q "SELECT CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT() as ACCOUNT" --format json 2>/dev/null)
    
    echo "To open the notebook:"
    echo ""
    echo "1. Go to Snowsight (https://app.snowflake.com)"
    echo "2. Navigate to: Projects > Notebooks"
    echo "3. Open: ${NOTEBOOK_NAME}"
    echo ""
    echo "Or run this SQL in a worksheet:"
    echo "  USE DATABASE ${DATABASE};"
    echo "  USE SCHEMA ${SCHEMA};"
    echo "  -- Click on ${NOTEBOOK_NAME} in the sidebar"
}

###############################################################################
# Command: streamlit - Get Streamlit URL
###############################################################################
cmd_streamlit() {
    echo "=================================================="
    echo "GNN Supply Chain Risk - Streamlit Dashboard"
    echo "=================================================="
    echo ""
    if [ -n "$ENV_PREFIX" ]; then
        echo "Environment Prefix: $ENV_PREFIX"
    fi
    echo ""
    
    # Try to get URL
    URL=$(snow streamlit get-url GNN_SUPPLY_CHAIN_RISK_APP \
        $SNOW_CONN \
        --database $DATABASE \
        --schema $SCHEMA \
        --role $ROLE 2>/dev/null) || true
    
    if [ -n "$URL" ]; then
        echo "Streamlit Dashboard URL:"
        echo ""
        echo "  $URL"
        echo ""
    else
        echo "Could not retrieve URL automatically."
        echo ""
        echo "To open the dashboard:"
        echo "1. Go to Snowsight (https://app.snowflake.com)"
        echo "2. Navigate to: Projects > Streamlit"
        echo "3. Open: GNN_SUPPLY_CHAIN_RISK_APP"
    fi
}

###############################################################################
# Execute command
###############################################################################
case $COMMAND in
    main)
        cmd_main
        ;;
    status)
        cmd_status
        ;;
    notebook)
        cmd_notebook
        ;;
    streamlit)
        cmd_streamlit
        ;;
    *)
        error_exit "Unknown command: $COMMAND"
        ;;
esac
