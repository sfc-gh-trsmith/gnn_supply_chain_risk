# GNN Supply Chain Risk - Full Test Cycle Guide

This document provides a complete guide for executing a full test cycle of the GNN Supply Chain Risk project, including all context about the deployment infrastructure, scripts, and verification procedures.

---

## Table of Contents

1. [Overview](#overview)
2. [Project Architecture](#project-architecture)
3. [Resource Inventory](#resource-inventory)
4. [The Three-Script Model](#the-three-script-model)
5. [Full Test Cycle Execution](#full-test-cycle-execution)
6. [Verification Procedures](#verification-procedures)
7. [Debugging Guide](#debugging-guide)
8. [Quick Reference](#quick-reference)

---

## Overview

The GNN Supply Chain Risk project uses Graph Neural Networks to analyze supply chain risk, identify hidden Tier 2+ supplier relationships, and detect bottlenecks. The project follows Snowflake deployment best practices with a three-script model for reproducible deployments.

### Core Philosophy

- **Clean Slate Testing**: Every full test cycle starts fresh to ensure reproducibility
- **Idempotency**: All scripts can be run multiple times safely
- **Fail Fast**: Scripts exit immediately on errors with clear messaging

---

## Project Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Full Test Cycle                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   clean.sh ─────────► deploy.sh ─────────► run.sh                           │
│      │                    │                   │                              │
│   Removes:             Creates:            Executes:                         │
│   • Compute Pool       • Role              • GNN Notebook                    │
│   • Warehouse          • Database          • Generates risk scores           │
│   • Database           • Warehouse         • Populates output tables         │
│   • Role               • Compute Pool      • Returns Streamlit URL           │
│   • Network Rules      • Tables/Views                                        │
│   • External Access    • Stages                                              │
│                        • Notebook                                            │
│                        • Streamlit App                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Source Data    │     │   GNN Notebook   │     │   Streamlit      │
│   (CSV Files)    │────►│   (GPU Runtime)  │────►│   Dashboard      │
│                  │     │                  │     │                  │
│  • vendors.csv   │     │  PyTorch         │     │  8 Pages:        │
│  • materials.csv │     │  Geometric       │     │  • Executive     │
│  • purchase_     │     │                  │     │  • Exploratory   │
│    orders.csv    │     │  Risk            │     │  • Network       │
│  • trade_data.csv│     │  Propagation     │     │  • Tier2         │
│  • regions.csv   │     │                  │     │  • Simulator     │
│  • bill_of_      │     │  Link            │     │  • Command       │
│    materials.csv │     │  Prediction      │     │  • Mitigation    │
│                  │     │                  │     │  • About         │
└──────────────────┘     └──────────────────┘     └──────────────────┘
         │                        │
         ▼                        ▼
┌──────────────────┐     ┌──────────────────┐
│  Source Tables   │     │  Output Tables   │
│                  │     │                  │
│  VENDORS         │     │  RISK_SCORES     │
│  MATERIALS       │     │  PREDICTED_LINKS │
│  PURCHASE_ORDERS │     │  BOTTLENECKS     │
│  BILL_OF_MATERIALS│    │                  │
│  TRADE_DATA      │     │                  │
│  REGIONS         │     │                  │
└──────────────────┘     └──────────────────┘
```

---

## Resource Inventory

### Snowflake Objects Created

| Resource Type | Name | Purpose |
|---------------|------|---------|
| **Role** | `GNN_SUPPLY_CHAIN_RISK_ROLE` | Project-specific role for all operations |
| **Database** | `GNN_SUPPLY_CHAIN_RISK` | Contains all project objects |
| **Schema** | `GNN_SUPPLY_CHAIN_RISK` | Main schema within database |
| **Warehouse** | `GNN_SUPPLY_CHAIN_RISK_WH` | SMALL warehouse, auto-suspend 300s |
| **Compute Pool** | `GNN_SUPPLY_CHAIN_RISK_COMPUTE_POOL` | GPU_NV_S for PyTorch GNN |
| **Network Rule** | `GNN_SUPPLY_CHAIN_RISK_EGRESS_RULE` | Allows PyPI access |
| **External Access** | `GNN_SUPPLY_CHAIN_RISK_EXTERNAL_ACCESS` | Integration for notebook |
| **Notebook** | `GNN_SUPPLY_CHAIN_RISK_NOTEBOOK` | Container runtime notebook |
| **Streamlit App** | `GNN_SUPPLY_CHAIN_RISK_APP` | Multi-page dashboard |

### Stages

| Stage | Purpose |
|-------|---------|
| `DATA_STAGE` | CSV data files for table loading |
| `MODELS_STAGE` | Notebook and environment files |

### Tables

#### Source Tables (populated from CSV)

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `VENDORS` | Tier 1 supplier master data | VENDOR_ID, NAME, COUNTRY_CODE, TIER |
| `MATERIALS` | Parts and products | MATERIAL_ID, DESCRIPTION, MATERIAL_GROUP |
| `PURCHASE_ORDERS` | Supplier-to-part relationships | PO_ID, VENDOR_ID, MATERIAL_ID |
| `BILL_OF_MATERIALS` | Part assembly hierarchy | BOM_ID, PARENT_MATERIAL_ID, CHILD_MATERIAL_ID |
| `TRADE_DATA` | External bills of lading | BOL_ID, SHIPPER_NAME, CONSIGNEE_NAME, HS_CODE |
| `REGIONS` | Geographic risk factors | REGION_CODE, BASE_RISK_SCORE |

#### Output Tables (populated by notebook)

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `RISK_SCORES` | GNN risk propagation results | NODE_ID, NODE_TYPE, RISK_SCORE, RISK_CATEGORY |
| `PREDICTED_LINKS` | Inferred Tier 2+ relationships | SOURCE_NODE_ID, TARGET_NODE_ID, PROBABILITY |
| `BOTTLENECKS` | Single points of failure | NODE_ID, DEPENDENT_COUNT, IMPACT_SCORE |

### Views

| View | Purpose |
|------|---------|
| `VW_SUPPLIER_RISK` | Supplier risk overview with region and GNN scores |
| `VW_MATERIAL_RISK` | Material risk with supplier counts |
| `VW_HIDDEN_DEPENDENCIES` | Predicted Tier 2+ relationships |
| `VW_RISK_SUMMARY` | Executive dashboard summary |

---

## The Three-Script Model

### Script Overview

| Script | Responsibility | Typical Duration |
|--------|----------------|------------------|
| `clean.sh` | Complete teardown of all resources | 15-60 seconds |
| `deploy.sh` | Infrastructure creation and data loading | 3-10 minutes |
| `run.sh` | Runtime operations (execute, status, URLs) | Varies |

### clean.sh

**Purpose**: Remove all project resources from Snowflake

**Usage**:
```bash
./clean.sh                # Interactive (prompts for confirmation)
./clean.sh --force        # Non-interactive
./clean.sh --yes          # Alias for --force
./clean.sh -y             # Short alias for --force
./clean.sh -c prod        # Use specific connection
./clean.sh --prefix DEV   # Clean DEV_ prefixed resources
```

**Cleanup Order**:
1. Compute Pool (must be dropped before role)
2. Warehouse
3. Network Rules and External Access Integration
4. Database (cascades to all contained objects)
5. Role (must be dropped last)

### deploy.sh

**Purpose**: Create all infrastructure and deploy applications

**Usage**:
```bash
./deploy.sh                   # Full deployment
./deploy.sh -c prod           # Use specific connection
./deploy.sh --prefix DEV      # Deploy with DEV_ prefix
./deploy.sh --skip-notebook   # Skip notebook deployment
./deploy.sh --only-sql        # SQL setup only
./deploy.sh --only-data       # Data upload/load only
./deploy.sh --only-notebook   # Notebook deployment only
./deploy.sh --only-streamlit  # Streamlit deployment only
```

**Deployment Steps**:
1. Prerequisites check (snow CLI, connection, files)
2. Account-level SQL setup (`sql/01_account_setup.sql`)
3. Schema-level SQL setup (`sql/02_schema_setup.sql`)
4. Upload CSV files to `@DATA_STAGE/raw/`
5. Load data into tables via `COPY INTO`
6. Deploy notebook with GPU runtime and external access
7. Deploy Streamlit app

### run.sh

**Purpose**: Execute runtime operations

**Usage**:
```bash
./run.sh main           # Execute the GNN notebook
./run.sh status         # Check resource status and table counts
./run.sh notebook       # Get notebook URL
./run.sh streamlit      # Get Streamlit dashboard URL
./run.sh -c prod main   # Use specific connection
```

**Commands**:
- `main`: Executes the notebook, then verifies output tables
- `status`: Shows compute pool, warehouse, all table row counts
- `notebook`: Provides instructions to open notebook in Snowsight
- `streamlit`: Retrieves Streamlit app URL

---

## Full Test Cycle Execution

### Quick Start (Non-Interactive)

```bash
./clean.sh --force && ./deploy.sh && ./run.sh main
```

### Step-by-Step Execution

#### Step 1: Clean Previous Deployment

```bash
./clean.sh --force
```

**Expected Output**:
```
==================================================
GNN Supply Chain Risk - Cleanup
==================================================

WARNING: This will permanently delete all project resources!

Resources to be deleted:
  - Compute Pool: GNN_SUPPLY_CHAIN_RISK_COMPUTE_POOL
  - Warehouse: GNN_SUPPLY_CHAIN_RISK_WH
  - Database: GNN_SUPPLY_CHAIN_RISK (includes all tables, stages, notebooks, apps)
  - Role: GNN_SUPPLY_CHAIN_RISK_ROLE
  - Network Rule: GNN_SUPPLY_CHAIN_RISK_EGRESS_RULE
  - External Access: GNN_SUPPLY_CHAIN_RISK_EXTERNAL_ACCESS

Starting cleanup...

Step 1: Dropping compute pool...
[OK] Compute pool dropped
Step 2: Dropping warehouse...
[OK] Warehouse dropped
Step 3: Dropping network rules...
[OK] Network rules dropped
Step 4: Dropping database...
[OK] Database dropped
Step 5: Dropping role...
[OK] Role dropped

==================================================
Cleanup Complete!
==================================================
```

**Note**: `[WARN]` messages are acceptable for resources that don't exist.

#### Step 2: Deploy Infrastructure and Applications

```bash
./deploy.sh
```

**Expected Output** (abbreviated):
```
==================================================
GNN Supply Chain Risk - Deployment
==================================================

Configuration:
  Connection: demo
  Database: GNN_SUPPLY_CHAIN_RISK
  Schema: GNN_SUPPLY_CHAIN_RISK
  Role: GNN_SUPPLY_CHAIN_RISK_ROLE
  Warehouse: GNN_SUPPLY_CHAIN_RISK_WH
  Compute Pool: GNN_SUPPLY_CHAIN_RISK_COMPUTE_POOL

Step 1: Checking prerequisites...
[OK] Snowflake CLI found
[OK] Connection 'demo' verified
[OK] Required files present

Step 2: Running account-level SQL setup...
[OK] Account-level setup completed

Step 3: Running schema-level SQL setup...
[OK] Schema-level setup completed

Step 4: Uploading pre-generated data to Snowflake stage...
[OK] Data files uploaded to stage

Step 5: Loading data into tables...
[OK] Data loaded into tables

Step 6: Deploying notebook...
[OK] Notebook files uploaded
[OK] Notebook created

Step 7: Deploying Streamlit app...
[OK] Streamlit app deployed

==================================================
Deployment Complete!
==================================================
```

#### Step 3: Execute GNN Notebook

```bash
./run.sh main
```

**Expected Output**:
```
==================================================
Executing GNN Notebook
==================================================

Database: GNN_SUPPLY_CHAIN_RISK
Notebook: GNN_SUPPLY_CHAIN_RISK_NOTEBOOK

Starting notebook execution...
This may take several minutes on first run (GPU initialization).

[OK] Notebook execution complete

Verifying results...
+----------------+-----------+
| TABLE_NAME     | ROW_COUNT |
+----------------+-----------+
| RISK_SCORES    |       XXX |
| PREDICTED_LINKS|       XXX |
| BOTTLENECKS    |       XXX |
+----------------+-----------+

Results written to tables. Open the Streamlit dashboard to explore.
Run: ./run.sh streamlit
```

**Note**: First execution may take 5-10 minutes for GPU compute pool initialization.

#### Step 4: Verify Results

```bash
./run.sh status
```

This displays:
- Compute pool status (should be ACTIVE or IDLE)
- Warehouse status
- All table row counts (source and output tables)
- Notebook status
- Streamlit app status

#### Step 5: Access Streamlit Dashboard

```bash
./run.sh streamlit
```

This retrieves and displays the Streamlit app URL. Open in browser to verify the dashboard loads correctly.

---

## Verification Procedures

### Minimal Verification Checklist

After a successful test cycle, verify:

| Check | Command | Expected Result |
|-------|---------|-----------------|
| Resources exist | `./run.sh status` | All resources listed |
| Source data loaded | See table counts in status | Rows > 0 for all source tables |
| Notebook produced output | See table counts in status | Rows > 0 for RISK_SCORES, PREDICTED_LINKS, BOTTLENECKS |
| Streamlit accessible | `./run.sh streamlit` | Valid URL returned |

### Manual Verification Queries

```sql
-- Check compute pool state
DESCRIBE COMPUTE POOL GNN_SUPPLY_CHAIN_RISK_COMPUTE_POOL;

-- Verify staged files
USE DATABASE GNN_SUPPLY_CHAIN_RISK;
LIST @GNN_SUPPLY_CHAIN_RISK.DATA_STAGE/raw/;

-- Check all table row counts
USE ROLE GNN_SUPPLY_CHAIN_RISK_ROLE;
USE DATABASE GNN_SUPPLY_CHAIN_RISK;
USE SCHEMA GNN_SUPPLY_CHAIN_RISK;

SELECT 
    table_name, 
    row_count 
FROM information_schema.tables 
WHERE table_schema = 'GNN_SUPPLY_CHAIN_RISK'
  AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Verify notebook exists with live version
SHOW NOTEBOOKS LIKE 'GNN_SUPPLY_CHAIN_RISK_NOTEBOOK';

-- Verify Streamlit app
SHOW STREAMLITS LIKE 'GNN_SUPPLY_CHAIN_RISK_APP';

-- Check risk score distribution
SELECT 
    RISK_CATEGORY, 
    COUNT(*) as COUNT,
    ROUND(AVG(RISK_SCORE), 3) as AVG_SCORE
FROM RISK_SCORES
GROUP BY RISK_CATEGORY
ORDER BY AVG_SCORE DESC;
```

---

## Debugging Guide

### Layered Debugging Approach

When a test cycle fails, debug in layers:

```
Layer 1: Prerequisites
   └── Is snow CLI installed and connected?
   └── Do required files exist?

Layer 2: Infrastructure
   └── Did role, database, warehouse create?
   └── Is the compute pool running?

Layer 3: Data
   └── Did files upload to stages?
   └── Did table loading succeed?
   └── Are row counts correct?

Layer 4: Applications
   └── Did notebook deploy?
   └── Did Streamlit app deploy?

Layer 5: Execution
   └── Does the notebook run?
   └── Are outputs generated?
   └── Is the Streamlit accessible?
```

### Common Issues and Solutions

#### Issue: Compute Pool Not Starting

**Symptom**: Compute pool stuck in `STARTING` or `SUSPENDED` state

**Diagnosis**:
```bash
snow sql -c demo -q "DESCRIBE COMPUTE POOL GNN_SUPPLY_CHAIN_RISK_COMPUTE_POOL;"
```

**Solutions**:
1. Wait longer (GPU pools can take 2-5 minutes)
2. Check account compute pool limits
3. Resume if suspended:
   ```sql
   ALTER COMPUTE POOL GNN_SUPPLY_CHAIN_RISK_COMPUTE_POOL RESUME;
   ```

#### Issue: Live Version Not Found

**Symptom**: `099108 (22000): Live version is not found`

**Cause**: Container runtime notebooks require a committed "live version" for CLI execution.

**Solution**:
```bash
snow sql -c demo -q "
    USE ROLE GNN_SUPPLY_CHAIN_RISK_ROLE;
    USE DATABASE GNN_SUPPLY_CHAIN_RISK;
    ALTER NOTEBOOK GNN_SUPPLY_CHAIN_RISK_NOTEBOOK ADD LIVE VERSION FROM LAST;
"
```

#### Issue: Permission Denied

**Symptom**: Operations fail with insufficient privileges

**Diagnosis**:
```bash
snow sql -c demo -q "SELECT CURRENT_USER(), CURRENT_ROLE();"
```

**Solution**: Ensure the role has been granted to your user:
```sql
USE ROLE ACCOUNTADMIN;
GRANT ROLE GNN_SUPPLY_CHAIN_RISK_ROLE TO USER <your_username>;
```

#### Issue: Data Loading Fails

**Symptom**: COPY INTO fails or tables empty

**Diagnosis**:
```bash
# Check staged files
snow sql -c demo -q "
    USE DATABASE GNN_SUPPLY_CHAIN_RISK;
    LIST @GNN_SUPPLY_CHAIN_RISK.DATA_STAGE/raw/;
"

# Check for load errors
snow sql -c demo -q "
    USE DATABASE GNN_SUPPLY_CHAIN_RISK;
    SELECT * FROM TABLE(VALIDATE(GNN_SUPPLY_CHAIN_RISK.VENDORS, JOB_ID => '_last'));
"
```

**Solutions**:
1. Re-upload files: `./deploy.sh --only-data`
2. Check CSV file format matches table schema
3. Verify file paths in COPY statement

#### Issue: Streamlit Not Loading

**Symptom**: 404 error or app doesn't display

**Diagnosis**:
```bash
snow sql -c demo -q "
    USE ROLE GNN_SUPPLY_CHAIN_RISK_ROLE;
    USE DATABASE GNN_SUPPLY_CHAIN_RISK;
    SHOW STREAMLITS LIKE 'GNN_SUPPLY_CHAIN_RISK_APP';
"
```

**Solution**: Redeploy Streamlit:
```bash
./deploy.sh --only-streamlit
```

### Incremental Recovery

When deployment fails partway through:

```bash
# Resume from data loading
./deploy.sh --only-data

# Resume from notebook deployment
./deploy.sh --only-notebook

# Resume from Streamlit deployment
./deploy.sh --only-streamlit
```

---

## Quick Reference

### Full Test Cycle Commands

| Purpose | Command |
|---------|---------|
| Non-interactive full cycle | `./clean.sh --force && ./deploy.sh && ./run.sh main` |
| Interactive full cycle | `./clean.sh && ./deploy.sh && ./run.sh main` |
| Streamlit-only iteration | `./deploy.sh --only-streamlit && ./run.sh streamlit` |
| Notebook-only iteration | `./deploy.sh --only-notebook && ./run.sh main` |
| Status check | `./run.sh status` |

### Common Flag Combinations

| Flags | Purpose |
|-------|---------|
| `-c CONNECTION` | Use specific Snowflake CLI connection |
| `-p PREFIX` or `--prefix PREFIX` | Environment prefix (DEV, PROD) |
| `--force` / `--yes` / `-y` | Skip confirmation prompts |
| `--only-COMPONENT` | Deploy single component |
| `--skip-notebook` | Skip notebook deployment |

### Key File Paths

| File | Purpose |
|------|---------|
| `clean.sh` | Cleanup script |
| `deploy.sh` | Deployment script |
| `run.sh` | Runtime operations |
| `sql/01_account_setup.sql` | Account-level DDL |
| `sql/02_schema_setup.sql` | Schema-level DDL |
| `data/synthetic/*.csv` | Pre-generated demo data |
| `notebooks/gnn_supply_chain_risk.ipynb` | GNN notebook |
| `notebooks/environment.yml` | Notebook dependencies |
| `streamlit/snowflake.yml` | Streamlit configuration |
| `streamlit/streamlit_app.py` | Streamlit entry point |

---

## Related Documentation

- [SNOWFLAKE_DEMO_FULL_TEST_CYCLE.md](../.cursor/SNOWFLAKE_DEMO_FULL_TEST_CYCLE.md) - General test cycle philosophy
- [SNOWFLAKE_DEPLOYMENT_SCRIPT_GUIDELINES.md](../.cursor/SNOWFLAKE_DEPLOYMENT_SCRIPT_GUIDELINES.md) - Script patterns
- [SNOWFLAKE_DDL_GUIDELINES.md](../.cursor/SNOWFLAKE_DDL_GUIDELINES.md) - DDL conventions
- [SNOWFLAKE_NOTEBOOK_GUIDELINES.md](../.cursor/SNOWFLAKE_NOTEBOOK_GUIDELINES.md) - Notebook best practices
- [SNOWFLAKE_STREAMLIT_GUIDELINES.md](../.cursor/SNOWFLAKE_STREAMLIT_GUIDELINES.md) - Streamlit deployment

