# Supply Chain Risk Intelligence for Manufacturing: Achieve N-Tier Visibility with Snowflake

**Uncover hidden supplier dependencies and concentration risks before they disrupt your production.**

---

## The Problem in Context

Procurement and supply chain teams believe they have diversified sourcing because their ERP shows multiple Tier-1 suppliers across different countries. But that data is incomplete—visibility ends at the first tier.

- **Tier-N blindness costs time and money.** When a disruption occurs at Tier-3, you're blindsided weeks later by sudden shortages, leaving no time to qualify alternatives.

- **Single points of failure hide in plain sight.** Three Tier-1 vendors across three countries may unknowingly source raw materials from the same refinery in a geologically unstable region.

- **Reactive firefighting replaces strategic planning.** Without predictive risk signals, procurement teams spend time managing crises instead of building resilient supply networks.

- **Compliance and audit gaps create exposure.** Regulations like UFLPA require traceability beyond Tier-1, but current systems cannot provide that visibility.

![Tier-N Visibility Gap](images/tier_visibility_gap.svg)
*Traditional ERP visibility ends at Tier-1. Risks fester unseen in deeper layers of the supply network.*

---

## What We'll Achieve

This solution transforms supply chain management from reactive response to proactive resilience.

- **Predictive risk scoring.** Alerts for latent risks before they manifest—"Part X has a 75% risk score because its estimated Tier-2 source is in a sanction zone."

- **Automatic concentration discovery.** Identify hidden bottlenecks where multiple Tier-1 suppliers converge on the same Tier-2+ source.

- **Proactive supplier qualification.** Find and qualify backup suppliers months before a crisis, not during one.

- **Faster time to insight.** Reduce supply chain due diligence from weeks of manual research to minutes of AI-powered analysis.

---

## Why Snowflake

- **Unified data foundation.** Internal ERP data and external trade intelligence join seamlessly in a governed platform—no data movement, no pipeline complexity.

- **Performance that scales.** GPU-enabled notebooks train graph neural networks on millions of trade records without infrastructure friction.

- **Collaboration without compromise.** Share risk insights with sourcing partners and internal teams while maintaining data governance and access controls.

- **Built-in AI/ML and apps.** From PyTorch Geometric models to interactive Streamlit dashboards, build and deploy intelligence closer to where decisions happen.

---

## The Data (At a Glance)

The solution fuses two data streams into a knowledge graph that reveals what your ERP cannot see.

![Data Architecture](images/data_architecture.svg)
*Internal ERP data forms the backbone; external trade intelligence fills in the hidden Tier-2+ relationships.*

- **Domains.** Vendors (Tier-1 suppliers), Materials (parts and BOMs), Regions (geographic risk factors), Trade Data (bills of lading linking shippers to consignees).

- **Freshness.** Batch ingestion for ERP data; periodic refresh for trade intelligence. Risk scores update when the GNN notebook executes.

- **Trust.** All data stays within Snowflake's governance boundary. Role-based access controls protect sensitive supplier financials and trade patterns.

| Data Source | Type | Purpose |
|-------------|------|---------|
| Vendor Master (ERP) | Internal | Known Tier-1 supplier nodes |
| Purchase Orders (ERP) | Internal | Supplier-to-material transaction edges |
| Bill of Materials (ERP) | Internal | Product assembly hierarchy |
| Trade Data (External) | Enrichment | Hidden Tier-2+ relationship inference |
| Regional Risk (External) | Enrichment | Geopolitical and disaster risk factors |

---

## How It Comes Together

![Solution Flow](images/solution_flow.svg)
*From raw data to actionable risk intelligence in five steps.*

1. **Ingest.** Load ERP exports (vendors, materials, purchase orders, BOMs) and external trade data into Snowflake tables. [→ SQL Setup Scripts]

2. **Build the Graph.** Construct a heterogeneous knowledge graph with suppliers, parts, and regions as nodes; transactions and trade flows as edges. [→ GNN Notebook]

3. **Infer Hidden Links.** Train a GraphSAGE model on trade patterns to predict likely Tier-2+ supplier relationships with probability scores. [→ GNN Notebook]

4. **Propagate Risk.** Calculate risk scores that flow through the network—a shock at Tier-3 propagates to impact Tier-1 and final products. [→ GNN Notebook]

5. **Visualize and Act.** Explore the supply network graph, analyze concentration points, and prioritize mitigation actions in an interactive dashboard. [→ Streamlit App]

---

## The Discovery Moment

![Concentration Risk Visualization](images/concentration_alert.svg)
*The "aha" moment: Three seemingly independent Tier-1 suppliers all depend on the same hidden Tier-2 refinery.*

Traditional analytics show a diversified supply base. Graph intelligence reveals the convergence.

**Before:** "We're safe—we source from three different vendors in three countries."

**After:** "All three vendors rely on one Tier-2 supplier in a high-risk region. We need to qualify alternatives now."

---

## Dashboard Experience

The Streamlit application guides users from executive summary to detailed analysis.

### Home — Executive Overview
Key metrics at a glance: nodes analyzed, critical risks identified, bottlenecks discovered, and hidden links inferred.

![Home Dashboard](images/dashboard_home.png)

### Supply Network — Interactive Graph
Explore the multi-tier supply network. Filter by node type, zoom into relationships, and trace dependency paths.

![Supply Network Graph](images/dashboard_network.png)

### Tier-2 Analysis — Concentration Deep Dive
Examine predicted Tier-2+ links, probability scores, and the suppliers most affected by hidden dependencies.

![Tier-2 Analysis](images/dashboard_tier2.png)

### Risk Mitigation — Prioritized Actions
Action items ranked by impact and probability. AI-assisted analysis provides context for deeper investigation.

![Risk Mitigation](images/dashboard_mitigation.png)

---

## Personas and Value

| Persona | Key Need | How This Solution Helps |
|---------|----------|------------------------|
| **VP of Procurement** | Reduce supplier-driven production disruptions | See concentration risks before they cause shortages; make proactive qualification investments |
| **Supply Chain Manager** | Faster risk assessment for critical materials | Propagated risk scores highlight which parts need attention—no manual tracing required |
| **Supplier Quality Engineer** | Identify high-risk suppliers for audit | Filter by risk category; prioritize reviews based on network position, not just financials |
| **Data Scientist** | Build and iterate on risk models | PyTorch Geometric runs in Snowflake Notebooks with GPU; experiment close to governed data |

---

## Technology Foundation

| Component | Role |
|-----------|------|
| **Snowflake Tables** | Store ERP data, trade intelligence, and model outputs |
| **Snowflake Notebooks (SPCS)** | Execute GNN training with GPU acceleration |
| **PyTorch Geometric** | GraphSAGE model for link prediction and risk propagation |
| **Streamlit in Snowflake** | Interactive dashboard for exploration and action planning |
| **Snowflake CLI** | Orchestrate deployment, execution, and cleanup |

![Technology Stack](images/technology_stack.svg)

---

## Call to Action

### Primary: Run the Demo in Your Account

1. Clone the repository and deploy to your Snowflake account:
   ```bash
   ./deploy.sh -c your_connection
   ```

2. Execute the GNN notebook to generate risk scores:
   ```bash
   ./run.sh main
   ```

3. Open the Streamlit dashboard:
   ```bash
   ./run.sh streamlit
   ```

### Secondary: Explore with Your Data

- Review the data architecture and map to your ERP schema
- Identify trade data sources for Tier-2+ enrichment (Panjiva, ImportGenius, UN Comtrade)
- Schedule a working session to design a proof-of-concept with your critical materials

---

## Image Index

The following images should be added to the `solution_presentation/images/` directory:

| Filename | Description |
|----------|-------------|
| `tier_visibility_gap.svg` | Diagram showing visibility ending at Tier-1 with hidden Tier-2/3 suppliers |
| `data_architecture.svg` | Data flow from ERP + Trade sources to Knowledge Graph |
| `solution_flow.svg` | 5-step pipeline: Ingest → Build → Infer → Propagate → Visualize |
| `concentration_alert.svg` | Radial graph showing multiple Tier-1 suppliers connected to one Tier-2 bottleneck |
| `dashboard_home.png` | Screenshot of the Streamlit Home page with key metrics |
| `dashboard_network.png` | Screenshot of the interactive Supply Network visualization |
| `dashboard_tier2.png` | Screenshot of the Tier-2 Analysis page |
| `dashboard_mitigation.png` | Screenshot of the Risk Mitigation prioritization view |
| `technology_stack.svg` | Visual of the Snowflake + PyG + Streamlit stack |

---

<p align="center">
Built with ❄️ Snowflake &nbsp;|&nbsp; 🔗 PyTorch Geometric &nbsp;|&nbsp; 🎨 Streamlit
</p>

