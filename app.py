"""Luna Coherence - All-in-One Version"""
import streamlit as st
import re
from dataclasses import dataclass
from enum import Enum

class ProcessingState(Enum):
    PSI = "chaos"
    DELTA = "transform"
    OMEGA = "coherent"

@dataclass
class CoherenceMetrics:
    psi_score: float
    delta_score: float
    omega_score: float
    state: ProcessingState

class LunaFramework:
    HEDGING = re.compile(r'\b(maybe|perhaps|possibly|might|could|probably|likely|I think|I believe|I guess|I suppose|seems like|kind of|sort of|somewhat|rather|fairly)\b', re.IGNORECASE)
    UNCERTAINTY = re.compile(r'\b(unclear|ambiguous|uncertain|confused|unsure|unknown|don\'t know|can\'t tell|hard to say)\b', re.IGNORECASE)
    
    TRANSFORMS = [
        (re.compile(r'\bI think that\b', re.I), ''),
        (re.compile(r'\bI believe that\b', re.I), ''),
        (re.compile(r'\b(perhaps|maybe|possibly)\b', re.I), ''),
        (re.compile(r'\b(kind|sort) of\b', re.I), ''),
        (re.compile(r'\bmight be\b', re.I), 'is'),
        (re.compile(r'\bcould be\b', re.I), 'is'),
        (re.compile(r'\bseems to be\b', re.I), 'is'),
        (re.compile(r'\bappears to be\b', re.I), 'is'),
    ]
    
    def detect_chaos(self, text):
        if not text:
            return 0.0
        words = len(text.split())
        if words == 0:
            return 0.0
        
        hedging = len(self.HEDGING.findall(text))
        uncertainty = len(self.UNCERTAINTY.findall(text))
        questions = text.count('?') * 2
        
        chaos_markers = hedging + uncertainty + questions
        normalized = (chaos_markers / words) * 100
        return min(normalized / 20.0, 1.0)
    
    def process(self, text):
        psi_score = self.detect_chaos(text)
        result = text
        
        for pattern, replacement in self.TRANSFORMS:
            result = pattern.sub(replacement, result)
        
        result = re.sub(r'\s+', ' ', result).strip()
        
        final_chaos = self.detect_chaos(result)
        omega_score = 1.0 - final_chaos
        delta_score = max(0.0, min(1.0, (psi_score - final_chaos) / max(psi_score, 0.1)))
        
        if psi_score > 0.6:
            state = ProcessingState.PSI
        elif delta_score > 0.3:
            state = ProcessingState.DELTA
        else:
            state = ProcessingState.OMEGA
        
        metrics = CoherenceMetrics(
            psi_score=psi_score,
            delta_score=delta_score,
            omega_score=omega_score,
            state=state
        )
        
        return result, metrics

# Streamlit UI
st.set_page_config(page_title="Luna Coherence", page_icon="🌙")

if 'framework' not in st.session_state:
    st.session_state.framework = LunaFramework()

st.title("🌙 Luna Coherence")
st.caption("Ψ² + Δ² = Ω² | Transform chaos into clarity")

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
        
        st.divider()
        col3, col4, col5 = st.columns(3)
        col3.metric("Transformation", f"{metrics.delta_score:.2f}")
        col4.metric("State", metrics.state.value.upper())
        
        st.success("✨ Transformation complete!")
    else:
        st.warning("Enter some text first!")

st.divider()
st.caption("Created by Briana Luna")
