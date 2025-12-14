"""
Reusable sidebar navigation component for the Supply Chain Risk application.

Provides consistent navigation across all pages.
"""

import streamlit as st


def render_sidebar():
    """
    Render the standard sidebar navigation for the application.
    
    Includes:
    - Application title/branding
    - Navigation links to all pages
    - Refresh data button
    
    Should be called at the end of each page's main() function.
    """
    with st.sidebar:
        st.markdown("### 🔗 Supply Chain Risk")
        st.markdown("---")
        st.page_link("streamlit_app.py", label="Home", icon="🏠")
        st.page_link("pages/2_Exploratory_Analysis.py", label="Exploratory Analysis", icon="🔍")
        st.page_link("pages/3_Supply_Network.py", label="Supply Network", icon="🕸️")
        st.page_link("pages/4_Tier2_Analysis.py", label="Tier-2 Analysis", icon="🔎")
        st.page_link("pages/5_Risk_Mitigation.py", label="Risk Mitigation", icon="⚡")
        st.page_link("pages/1_About.py", label="About", icon="ℹ️")
        st.markdown("---")
        
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

