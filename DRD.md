# Demo Requirements Document (DRD): N-Tier Supply Chain Risk Intelligence

## 1. Strategic Overview

### Problem Statement

Modern supply chains suffer from "Tier-N Blindness" - visibility typically ends at Tier-1 (direct suppliers), leaving organizations vulnerable to hidden concentration risks. A manufacturer may believe their supply chain is resilient because they source critical components from multiple vendors across different countries. However, they lack visibility to see that those vendors unknowingly source raw materials from the same upstream supplier in a geologically unstable or geopolitically risky region. When a disruption occurs at Tier-2 or Tier-3, the manufacturer is blindsided weeks later by sudden shortages with no time to qualify alternatives.

Traditional BI analytics measure entities in isolation. Risk lives in connections.

### Target Business Goals (KPIs)

| KPI | Target | Measurement |
|-----|--------|-------------|
| Tier-2+ Visibility | Discover hidden supplier relationships | Number of inferred links with >50% confidence |
| Risk Assessment Speed | 75% faster than manual analysis | Time-to-insight from weeks to minutes |
| Bottleneck Identification | Automated severity ranking | Single points of failure identified and scored |
| Proactive Qualification | Identify backup suppliers before crisis | Lead time for supplier qualification |

### The "Wow" Moment

The discovery visualization: Three seemingly independent Tier-1 suppliers - sourced from different countries, appearing diversified in traditional ERP reporting - all converge on a single hidden Tier-2 supplier. The GNN reveals this concentration risk that standard analytics completely miss, transforming "we're safe with three vendors" into "we have a critical single point of failure."

---

## 2. User Personas & Stories

| Persona Level | Role Title | Key User Story (Demo Flow) |
|---------------|------------|---------------------------|
| **Strategic** | VP of Procurement | "As VP of Procurement, I want to see portfolio-wide concentration risks and hidden dependencies so I can make proactive qualification investments before disruptions occur." |
| **Operational** | Supply Chain Manager | "As a Supply Chain Manager, I want propagated risk scores that highlight which materials need attention so I don't have to manually trace supplier dependencies." |
| **Technical** | Supplier Quality Engineer | "As a Supplier Quality Engineer, I want to filter suppliers by risk category and network position to prioritize audits based on systemic importance, not just financials." |
| **Analytical** | Data Scientist | "As a Data Scientist, I want to train and iterate on GNN models using PyTorch Geometric in Snowflake Notebooks with GPU compute, close to governed data." |

---

## 3. Data Architecture

### Data Strategy

The solution fuses internal ERP data (the "known" graph) with external trade intelligence (the "inference" layer) to build a heterogeneous knowledge graph that reveals what ERP systems cannot see.

### Structured Data Schema

| Table | Description | Key Columns | Source |
|-------|-------------|-------------|--------|
| `VENDORS` | Tier-1 supplier master from ERP (SAP LFA1 equivalent) | `VENDOR_ID`, `NAME`, `COUNTRY_CODE`, `CITY`, `TIER`, `FINANCIAL_HEALTH_SCORE` | Internal ERP |
| `MATERIALS` | Parts and products hierarchy (SAP MARA equivalent) | `MATERIAL_ID`, `DESCRIPTION`, `MATERIAL_GROUP` (RAW/SEMI/FIN), `CRITICALITY_SCORE`, `INVENTORY_DAYS` | Internal ERP |
| `PURCHASE_ORDERS` | Known supplier-to-part relationships (SAP EKPO equivalent) | `PO_ID`, `VENDOR_ID`, `MATERIAL_ID`, `QUANTITY`, `UNIT_PRICE`, `ORDER_DATE` | Internal ERP |
| `BILL_OF_MATERIALS` | Part assembly hierarchy (SAP STPO equivalent) | `BOM_ID`, `PARENT_MATERIAL_ID`, `CHILD_MATERIAL_ID`, `QUANTITY_PER_UNIT` | Internal ERP |
| `TRADE_DATA` | External bills of lading revealing Tier-2+ relationships | `BOL_ID`, `SHIPPER_NAME`, `CONSIGNEE_NAME`, `HS_CODE`, `SHIP_DATE`, `WEIGHT_KG` | External (Panjiva, ImportGenius) |
| `REGIONS` | Geographic risk factors | `REGION_CODE`, `REGION_NAME`, `BASE_RISK_SCORE`, `GEOPOLITICAL_RISK`, `NATURAL_DISASTER_RISK` | External enrichment |

### GNN Model Output Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `RISK_SCORES` | GNN-computed risk scores for all supply chain nodes | `NODE_ID`, `NODE_TYPE`, `RISK_SCORE`, `RISK_CATEGORY`, `CONFIDENCE`, `EMBEDDING` |
| `PREDICTED_LINKS` | Inferred Tier-2+ supplier relationships from link prediction | `SOURCE_NODE_ID`, `TARGET_NODE_ID`, `LINK_TYPE`, `PROBABILITY`, `EVIDENCE_STRENGTH` |
| `BOTTLENECKS` | Identified single points of failure | `NODE_ID`, `DEPENDENT_COUNT`, `IMPACT_SCORE`, `MITIGATION_STATUS` |

### Analytical Views

| View | Purpose |
|------|---------|
| `VW_SUPPLIER_RISK` | Combined supplier risk with regional factors and order statistics |
| `VW_MATERIAL_RISK` | Material risk with supplier count and average supplier risk |
| `VW_HIDDEN_DEPENDENCIES` | Predicted Tier-2+ links with entity resolution |
| `VW_RISK_SUMMARY` | Executive dashboard aggregations by category |

### External Data Sources (Snowflake Marketplace)

| Provider | Data Type | Integration Point |
|----------|-----------|-------------------|
| **S&P Global Panjiva** | Trade flow edges (shipper-consignee) | GNN link prediction training |
| **Oxford Economics TradePrism** | Forward-looking trade forecasts | Node feature enrichment |
| **FactSet** | Entity resolution, corporate hierarchy | Supplier node canonicalization |
| **Resilinc EventWatch AI** | Real-time disruption signals | Dynamic risk score updates |

---

## 4. ML/AI Specifications

### GNN Notebook Specification

| Parameter | Value |
|-----------|-------|
| **Objective** | Link Prediction + Risk Propagation |
| **Framework** | PyTorch Geometric (PyG) |
| **Model Architecture** | Heterogeneous GraphSAGE with HeteroConv |
| **Node Types** | Vendor, Material, Region, External Supplier |
| **Edge Types** | `supplies`, `component_of`, `located_in`, `ships_to` |
| **Embedding Dimension** | 64 |
| **Aggregation** | Mean pooling with learned transformation |
| **Training Loss** | Binary Cross-Entropy (BCE) for link prediction |
| **Validation** | Hold-out edge reconstruction |
| **Inference Output** | Risk scores written to `RISK_SCORES`, predicted links to `PREDICTED_LINKS` |

### Compute Resources

| Resource | Configuration |
|----------|---------------|
| **Compute Pool** | GPU-enabled (SYSTEM$GPU_RUNTIME) |
| **Warehouse** | Standard warehouse for inference queries |
| **External Access** | PyPI integration for PyTorch Geometric dependencies |

---

## 5. Cortex Intelligence Specifications

### Cortex Analyst (Semantic Model)

**Semantic Model:** `@SEMANTIC_MODELS/supply_chain_risk.yaml`

| Component | Specification |
|-----------|---------------|
| **Measures** | `risk_score`, `confidence`, `dependent_count`, `impact_score`, `financial_health` |
| **Dimensions** | `vendor_name`, `country`, `tier`, `node_type`, `risk_category`, `mitigation_status` |
| **Time Dimensions** | `calculated_at`, `identified_at` |

**Verified Queries:**

| Question | Purpose |
|----------|---------|
| "What is our overall portfolio risk?" | Portfolio-level KPIs |
| "Which regions have the highest supply chain risk?" | Geographic risk exposure |
| "What are our biggest bottlenecks?" | SPOF identification |
| "Which suppliers have critical risk scores?" | Action prioritization |

### Cortex Agent

**Agent Name:** `SUPPLY_CHAIN_RISK_AGENT`

| Tool | Type | Purpose |
|------|------|---------|
| `SUPPLY_CHAIN_ANALYTICS` | `cortex_analyst_tool` | Natural language queries via semantic model |
| `RISK_SCENARIO_ANALYZER` | `sql_exec_tool` | Scenario analysis (regional disruption, vendor failure, portfolio summary) |

**Sample Interactions:**

- "What is our exposure to suppliers in China?"
- "Run a regional disruption scenario for Southeast Asia with high shock intensity"
- "Which critical materials are single-sourced?"

### Risk Analysis UDF

**Function:** `ANALYZE_RISK_SCENARIO(scenario_type, target_region, target_vendor, shock_intensity)`

| Scenario Type | Analysis |
|---------------|----------|
| `REGIONAL_DISRUPTION` | Affected vendors, projected risk increase, diversification recommendation |
| `VENDOR_FAILURE` | Material dependencies, bottleneck impact, mitigation priority |
| `PORTFOLIO_SUMMARY` | Overall health score, critical counts, bottleneck totals |

---

## 6. Streamlit Application UX/UI

### Application Structure

| Page | Purpose | Key Features |
|------|---------|--------------|
| **Home** | The "Illusion of Diversity" narrative | Hero metrics, Traditional BI comparison, Concentration visualization |
| **Executive Summary** | Portfolio health KPIs | Risk distribution, regional exposure, trend analysis |
| **Exploratory Analysis** | Data exploration | Vendor/material distributions, spend analysis |
| **Supply Network** | Interactive graph visualization | Multi-tier relationship exploration, filtering |
| **Tier-2 Analysis** | Concentration deep-dive | Predicted links, probability scores, evidence |
| **Scenario Simulator** | What-if analysis | Regional disruption, vendor failure scenarios |
| **Command Center** | Cortex Agent chat interface | Natural language queries, scenario execution |
| **Risk Mitigation** | Action prioritization | Ranked bottlenecks, mitigation status tracking |
| **About** | Technical documentation | Architecture, data sources, methodology |

### Design System

| Element | Specification |
|---------|---------------|
| **Theme** | Dark mode (Slate background: `#0f172a` to `#1e293b`) |
| **Primary Color** | Snowflake Blue (`#29B5E8`) |
| **Alert Colors** | Critical: `#dc2626`, Warning: `#f59e0b`, Success: `#10b981` |
| **Typography** | System UI, sans-serif |
| **Chart Library** | Plotly (transparent backgrounds, slate grid lines) |

### Key Visualizations

| Visualization | Library | Purpose |
|---------------|---------|---------|
| Concentration Graph | Plotly Scatter (radial layout) | Show convergence on hidden Tier-2 |
| Risk Distribution | Plotly Bar | Category breakdown |
| Geographic Exposure | Plotly Choropleth/Bar | Regional supplier concentration |
| Criticality Scatter | Plotly Scatter | Material risk vs supplier count |
| Network Graph | Plotly/NetworkX | Full supply chain topology |

---

## 7. Deployment & Operations

### Deployment Scripts

| Script | Purpose |
|--------|---------|
| `deploy.sh` | Full deployment: SQL setup, data load, notebook, Streamlit, Cortex components |
| `run.sh` | Execute notebook, open Streamlit, check status |
| `clean.sh` | Teardown all resources |

### Component-Only Deployment Options

```bash
./deploy.sh --only-sql        # SQL setup only
./deploy.sh --only-data       # Data upload and load only
./deploy.sh --only-notebook   # Notebook deployment only
./deploy.sh --only-streamlit  # Streamlit app only
./deploy.sh --only-cortex     # Cortex UDF, semantic view, agent only
```

### Resource Naming Convention

| Resource | Naming Pattern |
|----------|----------------|
| Database | `[PREFIX_]GNN_SUPPLY_CHAIN_RISK` |
| Schema | `GNN_SUPPLY_CHAIN_RISK` |
| Role | `[PREFIX_]GNN_SUPPLY_CHAIN_RISK_ROLE` |
| Warehouse | `[PREFIX_]GNN_SUPPLY_CHAIN_RISK_WH` |
| Compute Pool | `[PREFIX_]GNN_SUPPLY_CHAIN_RISK_COMPUTE_POOL` |
| Notebook | `[PREFIX_]GNN_SUPPLY_CHAIN_RISK_NOTEBOOK` |
| Streamlit App | `GNN_SUPPLY_CHAIN_RISK_APP` |
| Cortex Agent | `SUPPLY_CHAIN_RISK_AGENT` |

---

## 8. Success Criteria

### Technical Validators

| Validator | Target |
|-----------|--------|
| GNN Training | Converges within 200 epochs |
| Link Prediction AUC | > 0.75 |
| Query Response Time | < 3 seconds for dashboard queries |
| Cortex Agent Response | Natural language query returns results < 5 seconds |

### Business Validators

| Validator | Current State | Future State |
|-----------|---------------|--------------|
| Time to Risk Assessment | Weeks of manual research | Minutes of AI-powered analysis |
| Tier Visibility | Tier-1 only | N-tier (Tier-2+ inferred) |
| Bottleneck Discovery | Manual, ad-hoc | Automated, continuous |
| Scenario Analysis | Spreadsheet-based | Real-time simulation |

---

## 9. Pilot Program

### 6-Week Implementation Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| **Data Integration** | 2 weeks | Connect ERP (vendor master, POs, BOMs), ingest trade intelligence feeds |
| **Model Training** | 2 weeks | Build supply chain graph, train GNN on customer network |
| **Deployment** | 2 weeks | Risk dashboards, Cortex Agent integration, user training |

### Deliverables

1. Deployed GNN model generating risk scores and predicted links
2. Interactive Streamlit dashboard with concentration analysis
3. Cortex Agent for natural language supply chain queries
4. Documentation and training materials

---

## 10. Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Data Platform** | Snowflake | Unified storage, compute, governance |
| **ML Framework** | PyTorch Geometric (PyG) | Graph neural network implementation |
| **ML Compute** | Snowflake Notebooks (SPCS) | GPU-accelerated model training |
| **Intelligence** | Cortex Analyst + Agent | Natural language interface |
| **Visualization** | Streamlit in Snowflake | Interactive dashboard |
| **Orchestration** | Snowflake CLI (snow) | Deployment automation |

---

## 11. Repository Structure

```
gnn_supply_chain_risk/
├── DRD.md                           # This document
├── deploy.sh                        # Deployment script
├── run.sh                           # Execution script
├── clean.sh                         # Cleanup script
├── data/
│   └── synthetic/                   # Pre-generated demo data (CSV)
├── notebooks/
│   ├── gnn_supply_chain_risk.ipynb  # GNN training notebook
│   └── environment.yml              # Conda environment
├── semantic_models/
│   └── supply_chain_risk.yaml       # Cortex Analyst semantic model
├── sql/
│   ├── 01_account_setup.sql         # Role, database, warehouse, compute pool
│   ├── 02_schema_setup.sql          # Tables, views, stages
│   ├── 03_cortex_udf.sql            # Risk analysis UDF
│   ├── 04_semantic_view.sql         # Semantic model stage
│   └── 05_cortex_agent.sql          # Cortex Agent definition
├── streamlit/
│   ├── streamlit_app.py             # Main application
│   ├── pages/                       # Multi-page app structure
│   ├── utils/                       # Data loaders, helpers
│   └── snowflake.yml                # Deployment config
├── react/                           # Optional React + FastAPI frontend
└── solution_presentation/
    ├── slides/                      # Executive presentation SVGs
    ├── images/                      # Architecture diagrams
    └── *.md                         # Supporting documentation
```

---

*Generated for N-Tier Supply Chain Risk Intelligence Solution*
*Built with Snowflake | PyTorch Geometric | Streamlit*
