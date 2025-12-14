#!/bin/bash

###############################################################################
# create_user.sh - Create a Snowflake user with access to a demo project
#
# This is a generic script that can be used with any Snowflake demo project.
# It creates a new user and grants them necessary permissions based on the
# project configuration provided via command-line options.
#
# Usage:
#   ./create_user.sh --user USERNAME --connection CONNECTION --database DB --schema SCHEMA [OPTIONS]
#
# Required:
#   --user, -u NAME           Username to create
#   --connection, -c NAME     Snowflake CLI connection name
#   --database, -d NAME       Project database name
#   --schema, -s NAME         Project schema name
#
# Optional:
#   --role, -r NAME           Role name (default: {DATABASE}_ROLE)
#   --warehouse, -w NAME      Warehouse name (default: {DATABASE}_WH)
#   --compute-pool NAME       Compute pool name (for notebook access)
#   --password, -p PASS       Initial password (if not set, user must use SSO)
#   --email EMAIL             User's email address
#   --first-name NAME         User's first name
#   --last-name NAME          User's last name
#   --comment TEXT            Comment for the user
#   --no-change-password      Do NOT force password change on first login
#   --dry-run                 Show SQL without executing
#   -h, --help                Show this help message
#
# Examples:
#   # GNN Supply Chain Risk project
#   ./create_user.sh -u demo_user -c demo -d GNN_SUPPLY_CHAIN_RISK -s GNN_SUPPLY_CHAIN_RISK -p TempPass123!
#
#   # With custom role and warehouse
#   ./create_user.sh -u analyst -c prod -d MY_PROJECT -s MY_SCHEMA -r CUSTOM_ROLE -w CUSTOM_WH
#
#   # Dry run to see SQL
#   ./create_user.sh -u test_user -c demo -d MY_DB -s MY_SCHEMA --dry-run
###############################################################################

set -e
set -o pipefail

# Required parameters
CONNECTION_NAME=""
USER_NAME=""
SNOWFLAKE_DATABASE=""
SNOWFLAKE_SCHEMA=""

# Optional parameters with defaults
SNOWFLAKE_ROLE=""
SNOWFLAKE_WAREHOUSE=""
COMPUTE_POOL_NAME=""
PASSWORD=""
EMAIL=""
FIRST_NAME=""
LAST_NAME=""
COMMENT=""
MUST_CHANGE_PASSWORD="TRUE"
DRY_RUN=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to display usage
usage() {
    cat << EOF
Usage: $0 --user USERNAME --connection CONNECTION --database DB --schema SCHEMA [OPTIONS]

Create a Snowflake user with access to a demo project.

Required:
  -u, --user NAME           Username to create
  -c, --connection NAME     Snowflake CLI connection name
  -d, --database NAME       Project database name
  -s, --schema NAME         Project schema name

Optional:
  -r, --role NAME           Role name (default: {DATABASE}_ROLE)
  -w, --warehouse NAME      Warehouse name (default: {DATABASE}_WH)
  --compute-pool NAME       Compute pool name (for notebook access)
  -p, --password PASS       Initial password (if not set, user must use SSO)
  --email EMAIL             User's email address
  --first-name NAME         User's first name
  --last-name NAME          User's last name
  --comment TEXT            Comment for the user
  --no-change-password      Do NOT force password change on first login
  --dry-run                 Show SQL without executing
  -h, --help                Show this help message

Examples:
  $0 -u demo_user -c demo -d GNN_SUPPLY_CHAIN_RISK -s GNN_SUPPLY_CHAIN_RISK -p TempPass123!
  $0 -u analyst -c prod -d MY_PROJECT -s MY_SCHEMA -r CUSTOM_ROLE -w CUSTOM_WH
  $0 -u test_user -c demo -d MY_DB -s MY_SCHEMA --dry-run

The user will receive:
  - Project role with full demo access
  - Access to database, schema, warehouse
  - Read access to all tables and views
  - Execute access to UDFs
  - Access to Streamlit apps (if any)
  - Access to Snowflake notebooks (if compute pool specified)
  - Snowflake Cortex LLM access
EOF
    exit 0
}

# Error exit function
error_exit() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -u|--user)
            USER_NAME="$2"
            shift 2
            ;;
        -c|--connection)
            CONNECTION_NAME="$2"
            shift 2
            ;;
        -d|--database)
            SNOWFLAKE_DATABASE="$2"
            shift 2
            ;;
        -s|--schema)
            SNOWFLAKE_SCHEMA="$2"
            shift 2
            ;;
        -r|--role)
            SNOWFLAKE_ROLE="$2"
            shift 2
            ;;
        -w|--warehouse)
            SNOWFLAKE_WAREHOUSE="$2"
            shift 2
            ;;
        --compute-pool)
            COMPUTE_POOL_NAME="$2"
            shift 2
            ;;
        -p|--password)
            PASSWORD="$2"
            shift 2
            ;;
        --email)
            EMAIL="$2"
            shift 2
            ;;
        --first-name)
            FIRST_NAME="$2"
            shift 2
            ;;
        --last-name)
            LAST_NAME="$2"
            shift 2
            ;;
        --comment)
            COMMENT="$2"
            shift 2
            ;;
        --no-change-password)
            MUST_CHANGE_PASSWORD="FALSE"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            error_exit "Unknown option: $1\nUse --help for usage information"
            ;;
    esac
done

# Validate required parameters
if [ -z "$USER_NAME" ]; then
    error_exit "Missing required parameter: --user\nUse --help for usage information"
fi

if [ -z "$CONNECTION_NAME" ]; then
    error_exit "Missing required parameter: --connection\nUse --help for usage information"
fi

if [ -z "$SNOWFLAKE_DATABASE" ]; then
    error_exit "Missing required parameter: --database\nUse --help for usage information"
fi

if [ -z "$SNOWFLAKE_SCHEMA" ]; then
    error_exit "Missing required parameter: --schema\nUse --help for usage information"
fi

# Set defaults for optional parameters
if [ -z "$SNOWFLAKE_ROLE" ]; then
    SNOWFLAKE_ROLE="${SNOWFLAKE_DATABASE}_ROLE"
fi

if [ -z "$SNOWFLAKE_WAREHOUSE" ]; then
    SNOWFLAKE_WAREHOUSE="${SNOWFLAKE_DATABASE}_WH"
fi

if [ -z "$COMMENT" ]; then
    COMMENT="${SNOWFLAKE_DATABASE} Demo User"
fi

# Validate username format (alphanumeric and underscore only)
if ! [[ "$USER_NAME" =~ ^[A-Za-z][A-Za-z0-9_]*$ ]]; then
    error_exit "Invalid username format. Must start with a letter and contain only letters, numbers, and underscores."
fi

# Convert username to uppercase (Snowflake convention)
USER_NAME_UPPER=$(echo "$USER_NAME" | tr '[:lower:]' '[:upper:]')

echo "=================================================="
echo "Snowflake Demo - Create User"
echo "=================================================="
echo ""
echo "Configuration:"
echo "  User:       $USER_NAME_UPPER"
echo "  Database:   $SNOWFLAKE_DATABASE"
echo "  Schema:     $SNOWFLAKE_SCHEMA"
echo "  Role:       $SNOWFLAKE_ROLE"
echo "  Warehouse:  $SNOWFLAKE_WAREHOUSE"
if [ -n "$COMPUTE_POOL_NAME" ]; then
    echo "  Compute Pool: $COMPUTE_POOL_NAME"
fi
echo ""

###############################################################################
# Step 1: Check Prerequisites
###############################################################################
echo "Step 1: Checking prerequisites..."
echo "------------------------------------------------"

# Check if snow CLI is installed
if ! command -v snow &> /dev/null; then
    error_exit "snow CLI not found. Install with: pip install snowflake-cli"
fi
echo -e "${GREEN}[OK]${NC} Snowflake CLI found"

# Test actual connection with a simple query
echo "Testing Snowflake connection..."
CONNECTION_TEST=$(snow sql -c "$CONNECTION_NAME" -q "SELECT CURRENT_USER()" 2>&1)
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Failed to connect to Snowflake"
    echo ""
    echo "Connection test output:"
    echo "$CONNECTION_TEST"
    echo ""
    echo "Possible causes:"
    echo "  - JWT private key passphrase not set"
    echo "  - Invalid credentials"
    echo "  - Network connectivity issues"
    echo ""
    echo "For JWT authentication, ensure you've set the passphrase:"
    echo "  export SNOWFLAKE_PRIVATE_KEY_PASSPHRASE='your_passphrase'"
    echo ""
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Connection '$CONNECTION_NAME' verified"

# Verify that the project is deployed (database exists)
DB_CHECK=$(snow sql -c "$CONNECTION_NAME" -q "SHOW DATABASES LIKE '$SNOWFLAKE_DATABASE'" 2>&1)
if ! echo "$DB_CHECK" | grep -q "$SNOWFLAKE_DATABASE"; then
    error_exit "Database '$SNOWFLAKE_DATABASE' not found. Deploy the project first."
fi
echo -e "${GREEN}[OK]${NC} Database '$SNOWFLAKE_DATABASE' exists"

# Check if user already exists
USER_EXISTS=false
USER_CHECK=$(snow sql -c "$CONNECTION_NAME" -q "SHOW USERS LIKE '$USER_NAME_UPPER'" 2>&1)
if echo "$USER_CHECK" | grep -qi "$USER_NAME_UPPER"; then
    USER_EXISTS=true
    echo -e "${YELLOW}[INFO]${NC} User '$USER_NAME_UPPER' already exists - will grant project access"
fi

echo ""

###############################################################################
# Step 2: Build SQL Commands
###############################################################################
echo "Step 2: Building SQL commands..."
echo "------------------------------------------------"

# Build optional user properties (only used for new users)
USER_OPTIONS=""
if [ -n "$PASSWORD" ]; then
    USER_OPTIONS="${USER_OPTIONS} PASSWORD = '${PASSWORD}'"
fi
if [ -n "$EMAIL" ]; then
    USER_OPTIONS="${USER_OPTIONS} EMAIL = '${EMAIL}'"
fi
if [ -n "$FIRST_NAME" ]; then
    USER_OPTIONS="${USER_OPTIONS} FIRST_NAME = '${FIRST_NAME}'"
fi
if [ -n "$LAST_NAME" ]; then
    USER_OPTIONS="${USER_OPTIONS} LAST_NAME = '${LAST_NAME}'"
fi

# Build compute pool grants if specified
COMPUTE_POOL_GRANTS=""
if [ -n "$COMPUTE_POOL_NAME" ]; then
    COMPUTE_POOL_GRANTS="
-- ============================================================
-- GRANT COMPUTE POOL ACCESS (for notebook execution)
-- ============================================================

GRANT USAGE ON COMPUTE POOL ${COMPUTE_POOL_NAME} TO ROLE ${SNOWFLAKE_ROLE};
GRANT MONITOR ON COMPUTE POOL ${COMPUTE_POOL_NAME} TO ROLE ${SNOWFLAKE_ROLE};
"
fi

# Build user creation SQL (only if user doesn't exist)
USER_CREATE_SQL=""
if [ "$USER_EXISTS" = false ]; then
    USER_CREATE_SQL="
-- ============================================================
-- 1. CREATE USER
-- ============================================================

CREATE USER IF NOT EXISTS ${USER_NAME_UPPER}
    ${USER_OPTIONS}
    MUST_CHANGE_PASSWORD = ${MUST_CHANGE_PASSWORD}
    DEFAULT_WAREHOUSE = '${SNOWFLAKE_WAREHOUSE}'
    DEFAULT_NAMESPACE = '${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA}'
    DEFAULT_ROLE = '${SNOWFLAKE_ROLE}'
    COMMENT = '${COMMENT}';
"
fi

# Build the SQL header based on whether user exists
if [ "$USER_EXISTS" = true ]; then
    SQL_HEADER="GRANT ACCESS TO USER: ${USER_NAME_UPPER}"
else
    SQL_HEADER="CREATE USER: ${USER_NAME_UPPER}"
fi

# Build the SQL script
SQL_SCRIPT=$(cat << EOF
-- ============================================================
-- ${SQL_HEADER}
-- For: ${SNOWFLAKE_DATABASE} Demo
-- ============================================================

USE ROLE ACCOUNTADMIN;
${USER_CREATE_SQL}
-- ============================================================
-- GRANT PROJECT ROLE TO USER
-- ============================================================

GRANT ROLE ${SNOWFLAKE_ROLE} TO USER ${USER_NAME_UPPER};

-- ============================================================
-- GRANT WAREHOUSE USAGE
-- ============================================================

GRANT USAGE ON WAREHOUSE ${SNOWFLAKE_WAREHOUSE} TO USER ${USER_NAME_UPPER};

-- ============================================================
-- 4. GRANT DATABASE ACCESS
-- ============================================================

GRANT USAGE ON DATABASE ${SNOWFLAKE_DATABASE} TO ROLE ${SNOWFLAKE_ROLE};
GRANT USAGE ON SCHEMA ${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA} TO ROLE ${SNOWFLAKE_ROLE};

-- ============================================================
-- 5. GRANT TABLE ACCESS
-- ============================================================

GRANT SELECT ON ALL TABLES IN SCHEMA ${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA} TO ROLE ${SNOWFLAKE_ROLE};
GRANT SELECT ON FUTURE TABLES IN SCHEMA ${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA} TO ROLE ${SNOWFLAKE_ROLE};

-- ============================================================
-- 6. GRANT VIEW ACCESS
-- ============================================================

GRANT SELECT ON ALL VIEWS IN SCHEMA ${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA} TO ROLE ${SNOWFLAKE_ROLE};
GRANT SELECT ON FUTURE VIEWS IN SCHEMA ${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA} TO ROLE ${SNOWFLAKE_ROLE};

-- ============================================================
-- 7. GRANT STAGE ACCESS
-- ============================================================

GRANT READ ON ALL STAGES IN SCHEMA ${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA} TO ROLE ${SNOWFLAKE_ROLE};
GRANT READ ON FUTURE STAGES IN SCHEMA ${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA} TO ROLE ${SNOWFLAKE_ROLE};

-- ============================================================
-- 8. GRANT FUNCTION ACCESS
-- ============================================================

GRANT USAGE ON ALL FUNCTIONS IN SCHEMA ${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA} TO ROLE ${SNOWFLAKE_ROLE};
GRANT USAGE ON FUTURE FUNCTIONS IN SCHEMA ${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA} TO ROLE ${SNOWFLAKE_ROLE};

-- ============================================================
-- 9. GRANT STREAMLIT ACCESS
-- ============================================================

GRANT USAGE ON ALL STREAMLITS IN SCHEMA ${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA} TO ROLE ${SNOWFLAKE_ROLE};
GRANT USAGE ON FUTURE STREAMLITS IN SCHEMA ${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA} TO ROLE ${SNOWFLAKE_ROLE};
${COMPUTE_POOL_GRANTS}
-- ============================================================
-- 10. GRANT CORTEX LLM ACCESS
-- ============================================================

GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE ${SNOWFLAKE_ROLE};

-- ============================================================
-- 11. GRANT FILE FORMAT ACCESS
-- ============================================================

GRANT USAGE ON ALL FILE FORMATS IN SCHEMA ${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA} TO ROLE ${SNOWFLAKE_ROLE};

-- ============================================================
-- VERIFICATION
-- ============================================================

DESCRIBE USER ${USER_NAME_UPPER};
SHOW GRANTS TO USER ${USER_NAME_UPPER};

SELECT 'User ${USER_NAME_UPPER} created successfully!' AS status;
EOF
)

###############################################################################
# Step 3: Execute or Display SQL
###############################################################################
if [ "$DRY_RUN" = true ]; then
    echo ""
    echo -e "${YELLOW}[DRY RUN] The following SQL would be executed:${NC}"
    echo "=================================================="
    echo ""
    echo "$SQL_SCRIPT"
    echo ""
    echo "=================================================="
    echo -e "${YELLOW}[DRY RUN] No changes were made.${NC}"
    echo ""
    exit 0
fi

if [ "$USER_EXISTS" = true ]; then
    echo "Granting project access to existing user '${USER_NAME_UPPER}'..."
else
    echo "Creating user '${USER_NAME_UPPER}'..."
fi
echo ""

###############################################################################
# Step 3: Execute SQL
###############################################################################
echo "Step 3: Executing SQL..."
echo "------------------------------------------------"

# Execute the SQL
snow sql -c "$CONNECTION_NAME" -q "$SQL_SCRIPT"

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    if [ "$USER_EXISTS" = true ]; then
        echo -e "${GREEN}[OK] Project Access Granted Successfully!${NC}"
    else
        echo -e "${GREEN}[OK] User Created Successfully!${NC}"
    fi
    echo "=================================================="
    echo ""
    
    # Retrieve account information
    echo "Retrieving account information..."
    ACCOUNT_INFO=$(snow sql -c "$CONNECTION_NAME" -q "SELECT CURRENT_ACCOUNT() AS account, CURRENT_ORGANIZATION_NAME() AS org, CURRENT_REGION() AS region" --format json 2>/dev/null || echo "[]")
    
    # Parse account info
    ACCOUNT_NAME=$(echo "$ACCOUNT_INFO" | grep -o '"ACCOUNT"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/' || echo "")
    ORG_NAME=$(echo "$ACCOUNT_INFO" | grep -o '"ORG"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/' || echo "")
    
    # Build account URL
    if [ -n "$ORG_NAME" ] && [ -n "$ACCOUNT_NAME" ]; then
        ACCOUNT_URL="https://app.snowflake.com/${ORG_NAME}/${ACCOUNT_NAME}"
        ACCOUNT_IDENTIFIER="${ORG_NAME}-${ACCOUNT_NAME}"
    elif [ -n "$ACCOUNT_NAME" ]; then
        ACCOUNT_URL="https://${ACCOUNT_NAME}.snowflakecomputing.com"
        ACCOUNT_IDENTIFIER="${ACCOUNT_NAME}"
    else
        ACCOUNT_URL="[Could not retrieve - check connection]"
        ACCOUNT_IDENTIFIER="[Check with administrator]"
    fi
    
    echo ""
    echo "============================================================"
    echo "  USER ACCESS INFORMATION"
    echo "============================================================"
    echo ""
    echo "SNOWFLAKE LOGIN"
    echo "---------------"
    echo "  Web Login URL:      ${ACCOUNT_URL}"
    echo "  Account Identifier: ${ACCOUNT_IDENTIFIER}"
    echo "  Username:           ${USER_NAME_UPPER}"
    if [ "$USER_EXISTS" = true ]; then
        echo "  Password:           [Existing user - use current credentials]"
    elif [ -n "$PASSWORD" ]; then
        echo "  Temporary Password: ${PASSWORD}"
        if [ "$MUST_CHANGE_PASSWORD" = "TRUE" ]; then
            echo "  (Password change required on first login)"
        fi
    else
        echo "  Password:           [Contact administrator for SSO setup]"
    fi
    echo ""
    echo "PROJECT DETAILS"
    echo "---------------"
    echo "  Database:           ${SNOWFLAKE_DATABASE}"
    echo "  Schema:             ${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA}"
    echo "  Role:               ${SNOWFLAKE_ROLE}"
    echo "  Warehouse:          ${SNOWFLAKE_WAREHOUSE}"
    if [ -n "$COMPUTE_POOL_NAME" ]; then
        echo "  Compute Pool:       ${COMPUTE_POOL_NAME}"
    fi
    echo ""
    echo "QUICK START SQL"
    echo "---------------"
    echo "  USE ROLE ${SNOWFLAKE_ROLE};"
    echo "  USE DATABASE ${SNOWFLAKE_DATABASE};"
    echo "  USE SCHEMA ${SNOWFLAKE_SCHEMA};"
    echo "  USE WAREHOUSE ${SNOWFLAKE_WAREHOUSE};"
    echo ""
    echo "============================================================"
    echo ""
    echo "Admin Notes:"
    echo "  To remove this user later:"
    echo "    snow sql -c ${CONNECTION_NAME} -q \"DROP USER IF EXISTS ${USER_NAME_UPPER};\""
    echo ""
    echo "  To reset password:"
    echo "    snow sql -c ${CONNECTION_NAME} -q \"ALTER USER ${USER_NAME_UPPER} SET PASSWORD = 'NewPassword!';\""
    echo ""
else
    if [ "$USER_EXISTS" = true ]; then
        error_exit "Failed to grant project access. Check the error messages above."
    else
        error_exit "Failed to create user. Check the error messages above."
    fi
fi
