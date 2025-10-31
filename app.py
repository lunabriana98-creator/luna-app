"""
Luna Framework - MVP Web App
Deploy instantly: streamlit run app.py
"""

import streamlit as st
from luna_framework import LunaFramework

st.set_page_config(page_title="Luna Coherence", page_icon="🌙", layout="centered")

# Initialize
if 'framework' not in st.session_state:
    st.session_state.framework = LunaFramework()

# Header
st.title("🌙 Luna Coherence")
st.caption("Ψ² + Δ² = Ω² | Transform chaos into clarity")

# Input
text_input = st.text_area(
    "Paste your text:",
    height=150,
    placeholder="I think maybe this could be interesting..."
)

if st.button("✨ Transform", type="primary"):
    if text_input:
        result, metrics = st.session_state.framework.process(text_input)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Before")
            st.text_area("", value=text_input, height=100, disabled=True, key="before")
            st.metric("Chaos (Ψ)", f"{metrics.psi_score:.2f}")
        
        with col2:
            st.subheader("After")
            st.text_area("", value=result, height=100, disabled=True, key="after")
            st.metric("Coherence (Ω)", f"{metrics.omega_score:.2f}", 
                     delta=f"+{(metrics.omega_score - metrics.psi_score):.2f}")
        
        # Metrics
        st.divider()
        col3, col4, col5 = st.columns(3)
        col3.metric("Transformation", f"{metrics.delta_score:.2f}")
        col4.metric("Conservation", f"{metrics.geometric_conservation:.2f}")
        col5.metric("Efficiency", f"{metrics.coherence_efficiency:.1%}")
        
        st.info(f"**State:** {metrics.state.value.upper()}")
    else:
        st.warning("Enter some text first!")

# Footer
st.divider()
st.caption("Created by Briana Luna | [Upgrade to Pro](#) for batch processing")
