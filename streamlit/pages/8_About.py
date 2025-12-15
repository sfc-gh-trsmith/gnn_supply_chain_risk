"""
About Page

Provides comprehensive information about the Supply Chain Risk Intelligence demo,
including data sources, the GNN notebook, and technical architecture.
"""

import streamlit as st
import sys
from pathlib import Path
from snowflake.snowpark.context import get_active_session

# Add parent directory to path for utils import (needed for Streamlit in Snowflake)
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.sidebar import render_sidebar, render_star_callout

st.set_page_config(
    page_title="About",
    page_icon="ℹ️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    .page-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 0.5rem;
    }
    .page-subheader {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #334155;
    }
    .info-card {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        height: 100%;
    }
    .info-card h3 {
        color: #f8fafc;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    .info-card p {
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .table-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .table-name {
        color: #3b82f6;
        font-weight: 700;
        font-size: 1rem;
        font-family: monospace;
    }
    .table-desc {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 0.25rem;
    }
    .badge-internal {
        background: #1e40af;
        color: #fff;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        text-transform: uppercase;
        margin-left: 8px;
    }
    .badge-external {
        background: #b45309;
        color: #fff;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        text-transform: uppercase;
        margin-left: 8px;
    }
    .badge-output {
        background: #166534;
        color: #fff;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        text-transform: uppercase;
        margin-left: 8px;
    }
    .tech-stack {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    .tech-badge {
        background: rgba(59, 130, 246, 0.2);
        border: 1px solid #3b82f6;
        color: #93c5fd;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    .workflow-step {
        background: rgba(30, 41, 59, 0.6);
        border-left: 3px solid #3b82f6;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .workflow-step h4 {
        color: #f8fafc;
        margin-bottom: 0.25rem;
    }
    .workflow-step p {
        color: #94a3b8;
        margin: 0;
    }
    
    /* Hide default multipage navigation */
    [data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)


def main():
    """Main application."""
    
    # Render STAR callout if demo mode is enabled
    render_star_callout("about")
    
    # Header
    st.markdown("""
    <div class="page-header">ℹ️ About This Demo</div>
    <div class="page-subheader">
        AI-Driven N-Tier Supply Chain Resilience using Graph Neural Networks
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================
    # OVERVIEW
    # ============================================
    st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>🎯 The Problem: Tier-N Blindness</h3>
            <p>
                Modern supply chains are brittle because visibility typically ends at "Tier 1"—the direct suppliers. 
                A company might believe its supply chain is resilient because it sources a critical component from 
                three different vendors across three different countries. However, they lack the visibility to see 
                that all three vendors unknowingly source their raw materials from the same single refinery.
            </p>
            <p style="margin-top: 1rem;">
                This "Tier-N Blindness" means that risks—whether geopolitical, environmental, or financial—fester 
                unseen in the deeper layers of the network. When a disruption occurs at Tier 3, the manufacturer 
                is blindsided weeks later by sudden shortages.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>💡 The Solution</h3>
            <p>
                We model the supply chain as a <strong>Knowledge Graph</strong> and use 
                <strong>Graph Neural Networks (GNNs)</strong> to:
            </p>
            <ul style="color: #94a3b8; margin-top: 0.5rem;">
                <li>Infer hidden Tier-2+ relationships</li>
                <li>Predict link probabilities</li>
                <li>Propagate risk scores</li>
                <li>Identify concentration points</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ============================================
    # DATA ARCHITECTURE
    # ============================================
    st.markdown('<div class="section-header">Data Architecture</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <p style="color: #94a3b8; margin-bottom: 1.5rem;">
        The solution fuses internal ERP data with external trade intelligence to build a multi-tier supply network graph.
    </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📊 Internal ERP Data")
        st.markdown("""
        <div class="table-card">
            <span class="table-name">VENDORS</span>
            <span class="badge-internal">ERP</span>
            <p class="table-desc">Tier-1 supplier master data including company info, country, and contact details</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="table-card">
            <span class="table-name">MATERIALS</span>
            <span class="badge-internal">ERP</span>
            <p class="table-desc">Parts and products catalog with material groups (RAW, SEMI, FIN) and units</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="table-card">
            <span class="table-name">PURCHASE_ORDERS</span>
            <span class="badge-internal">ERP</span>
            <p class="table-desc">Transaction history linking vendors to materials with quantities and prices</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="table-card">
            <span class="table-name">BOM</span>
            <span class="badge-internal">ERP</span>
            <p class="table-desc">Bill of Materials defining component-of relationships between parts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🌐 External Trade Intelligence")
        st.markdown("""
        <div class="table-card">
            <span class="table-name">BILLS_OF_LADING</span>
            <span class="badge-external">TRADE</span>
            <p class="table-desc">Global shipping records showing shipper-to-consignee relationships with HS codes</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="table-card">
            <span class="table-name">REGIONS</span>
            <span class="badge-external">TRADE</span>
            <p class="table-desc">Geographic risk factors including geopolitical, environmental, and economic scores</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="table-card">
            <span class="table-name">EXTERNAL_SUPPLIERS</span>
            <span class="badge-external">TRADE</span>
            <p class="table-desc">Tier-2+ suppliers discovered from trade data (not in internal ERP)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("#### 🤖 Model Outputs")
        st.markdown("""
        <div class="table-card">
            <span class="table-name">RISK_SCORES</span>
            <span class="badge-output">GNN</span>
            <p class="table-desc">Propagated risk scores for all nodes with categories (CRITICAL, HIGH, MEDIUM, LOW)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="table-card">
            <span class="table-name">PREDICTED_LINKS</span>
            <span class="badge-output">GNN</span>
            <p class="table-desc">Inferred Tier-2+ relationships with probability scores and confidence levels</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="table-card">
            <span class="table-name">BOTTLENECKS</span>
            <span class="badge-output">GNN</span>
            <p class="table-desc">Identified concentration points where multiple Tier-1 suppliers converge</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ============================================
    # GNN NOTEBOOK
    # ============================================
    st.markdown('<div class="section-header">GNN Analysis Notebook</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>📓 Notebook Overview</h3>
            <p>
                The Snowflake Notebook implements a complete Graph Neural Network pipeline using 
                <strong>PyTorch Geometric (PyG)</strong> running natively in Snowflake.
            </p>
            <p style="margin-top: 1rem;">
                <strong>Key Capabilities:</strong>
            </p>
            <ul style="color: #94a3b8;">
                <li><strong>Graph Construction:</strong> Builds a HeteroData object with Supplier, Part, and Region nodes</li>
                <li><strong>Link Prediction:</strong> GraphSAGE encoder predicts hidden Tier-2+ relationships</li>
                <li><strong>Risk Propagation:</strong> Calculates propagated risk scores across the network</li>
                <li><strong>Bottleneck Detection:</strong> Identifies single points of failure</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>⚙️ Technical Details</h3>
            <p><strong>Model Architecture:</strong></p>
            <ul style="color: #94a3b8;">
                <li><strong>Encoder:</strong> GraphSAGE with HeteroConv layers</li>
                <li><strong>Task:</strong> Link Prediction + Node Classification</li>
                <li><strong>Training:</strong> Negative sampling with edge-level supervision</li>
            </ul>
            <p style="margin-top: 1rem;"><strong>Graph Structure:</strong></p>
            <ul style="color: #94a3b8;">
                <li><strong>Node Types:</strong> Supplier, Part, Region, External Supplier</li>
                <li><strong>Edge Types:</strong> SUPPLIES, COMPONENT_OF, LOCATED_IN, SHIPS_TO</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Workflow steps
    st.markdown("#### 🔄 Analysis Workflow", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="workflow-step">
            <h4>1. Ingest</h4>
            <p>Load ERP and Trade data into Snowflake tables</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="workflow-step">
            <h4>2. Build</h4>
            <p>Construct the heterogeneous graph structure</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="workflow-step">
            <h4>3. Infer</h4>
            <p>Run GNN to predict links and propagate risk</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="workflow-step">
            <h4>4. Act</h4>
            <p>Write results to tables for dashboard visualization</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ============================================
    # APP PAGES
    # ============================================
    st.markdown('<div class="section-header">Application Pages</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>🏠 Home</h3>
            <p>Executive dashboard with key metrics, top concentration risk visualization, and navigation to analysis modules.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <h3>🔍 Exploratory Analysis</h3>
            <p>Data source overview showing connected tables, record counts, and the visibility gap between known Tier-1 and inferred Tier-2+ relationships.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <h3>🕸️ Supply Network</h3>
            <p>Interactive force-directed graph visualization of the multi-tier supply network with node filtering and relationship exploration.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>🔎 Tier-2 Analysis</h3>
            <p>Deep dive into concentration risk with bottleneck identification, predicted link analysis, and confidence scoring.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <h3>⚡ Risk Mitigation</h3>
            <p>Prioritized action items with impact/probability matrix, AI-assisted analysis, and mitigation recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <h3>ℹ️ About</h3>
            <p>This page! Documentation of the demo architecture, data sources, and technical implementation.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ============================================
    # TECH STACK
    # ============================================
    st.markdown('<div class="section-header">Technology Stack</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tech-stack">
        <span class="tech-badge">Snowflake</span>
        <span class="tech-badge">Snowpark</span>
        <span class="tech-badge">Snowflake Notebooks</span>
        <span class="tech-badge">Streamlit in Snowflake</span>
        <span class="tech-badge">PyTorch Geometric</span>
        <span class="tech-badge">GraphSAGE</span>
        <span class="tech-badge">Plotly</span>
        <span class="tech-badge">Python 3.11</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>☁️ Snowflake Platform</h3>
            <p>
                All data, compute, and AI run within Snowflake's secure governance boundary. 
                No data movement required.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>🧠 Graph Neural Networks</h3>
            <p>
                PyTorch Geometric enables sophisticated graph-based machine learning for 
                link prediction and risk propagation.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card">
            <h3>📊 Interactive Visualization</h3>
            <p>
                Streamlit provides a modern, responsive interface with Plotly charts 
                and custom D3.js components.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ============================================
    # GETTING STARTED
    # ============================================
    st.markdown('<div class="section-header">Getting Started</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h3>🚀 Quick Start Guide</h3>
        <ol style="color: #94a3b8; line-height: 2;">
            <li><strong>Run the Setup:</strong> Execute the SQL scripts to create the database, schema, and load sample data</li>
            <li><strong>Execute the Notebook:</strong> Open the GNN notebook in Snowflake and run all cells to generate risk scores, predicted links, and bottlenecks</li>
            <li><strong>Explore the Dashboard:</strong> Navigate through the Streamlit app pages to visualize the results</li>
            <li><strong>Analyze Risks:</strong> Use the Tier-2 Analysis page to identify concentration points and the Risk Mitigation page to prioritize actions</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("")
    st.markdown("""
    <p style="text-align: center; color: #64748b; font-size: 0.85rem; margin-top: 2rem;">
        Built with ❄️ Snowflake &nbsp;|&nbsp; 🔗 PyTorch Geometric &nbsp;|&nbsp; 🎨 Streamlit
    </p>
    """, unsafe_allow_html=True)
    
    # Sidebar
    render_sidebar()


if __name__ == "__main__":
    main()

