"""Luna Coherence Framework - Production Version"""
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
    # Enhanced chaos detection patterns
    HEDGING = re.compile(
        r'\b(maybe|perhaps|possibly|might|could|probably|likely|'
        r'I think|I believe|I guess|I suppose|I feel like|seems like|'
        r'kind of|sort of|somewhat|rather|fairly|basically|actually)\b',
        re.IGNORECASE
    )
    
    UNCERTAINTY = re.compile(
        r'\b(unclear|ambiguous|uncertain|confused|unsure|unknown|not sure|'
        r'don\'t know|can\'t tell|hard to say|difficult to|not certain|'
        r'questionable|doubtful|mixed up)\b',
        re.IGNORECASE
    )
    
    # Grammar and transformation rules
    TRANSFORMS = [
        # Fix common grammar issues first
        (re.compile(r'\bill be able to\b', re.I), "I'll be able to"),
        (re.compile(r'\bits all been\b', re.I), "it's all been"),
        (re.compile(r'\bits been\b', re.I), "it's been"),
        (re.compile(r'\bI dont\b', re.I), "I don't"),
        (re.compile(r'\bI don\'t if\b', re.I), "I don't know if"),
        
        # Remove uncertainty phrases completely
        (re.compile(r'\bI don\'t know if\b', re.I), ''),
        (re.compile(r'\bI\'m not sure if\b', re.I), ''),
        (re.compile(r'\bI don\'t know\b', re.I), ''),
        (re.compile(r'\bI need your help\b', re.I), ''),
        
        # Remove thinking phrases
        (re.compile(r'\bI think that\b', re.I), ''),
        (re.compile(r'\bI believe that\b', re.I), ''),
        (re.compile(r'\bI guess that\b', re.I), ''),
        (re.compile(r'\bI feel like\b', re.I), ''),
        (re.compile(r'\bI think\b', re.I), ''),
        (re.compile(r'\bI believe\b', re.I), ''),
        (re.compile(r'\bI guess\b', re.I), ''),
        
        # Remove hedging words
        (re.compile(r'\bperhaps\s*,?\s*', re.I), ''),
        (re.compile(r'\bmaybe\s*,?\s*', re.I), ''),
        (re.compile(r'\bpossibly\s*,?\s*', re.I), ''),
        (re.compile(r'\bprobably\s*,?\s*', re.I), ''),
        (re.compile(r'\bbasically\s*,?\s*', re.I), ''),
        (re.compile(r'\bactually\s*,?\s*', re.I), ''),
        (re.compile(r'\b(kind|sort) of\b', re.I), ''),
        (re.compile(r'\bsomewhat\b', re.I), ''),
        
        # Handle "able to" constructions
        (re.compile(r'\bmight be able to\b', re.I), 'can'),
        (re.compile(r'\bcould be able to\b', re.I), 'can'),
        (re.compile(r'\bwould be able to\b', re.I), 'can'),
        
        # Replace weak verbs
        (re.compile(r'\bmight be\b', re.I), 'is'),
        (re.compile(r'\bcould be\b', re.I), 'is'),
        (re.compile(r'\bseems to be\b', re.I), 'is'),
        (re.compile(r'\bappears to be\b', re.I), 'is'),
        (re.compile(r'\btends to be\b', re.I), 'is'),
        
        # Remove mixed up phrases
        (re.compile(r'\b(all been|been) a mix up in my head\b', re.I), 'unclear'),
        (re.compile(r'\bmixed up\b', re.I), 'unclear'),
    ]
    
    def detect_chaos(self, text):
        """Calculate chaos score from 0.0 to 1.0"""
        if not text or not text.strip():
            return 0.0
        
        words = text.split()
        word_count = len(words)
        if word_count == 0:
            return 0.0
        
        # Count markers
        hedging = len(self.HEDGING.findall(text))
        uncertainty = len(self.UNCERTAINTY.findall(text))
        questions = text.count('?') * 1.5
        
        total_markers = hedging + uncertainty + questions
        
        # Normalize
        normalized = (total_markers / word_count) * 100
        chaos_score = min(normalized / 15.0, 1.0)  # Lower threshold for sensitivity
        
        return chaos_score
    
    def highlight_chaos(self, text):
        """Return HTML with chaos words highlighted"""
        if not text or not text.strip():
            return ""
        
        result = text
        chaos_positions = []
        
        # Find all chaos words
        for match in self.HEDGING.finditer(text):
            chaos_positions.append((match.start(), match.end(), match.group(), 'hedging'))
        for match in self.UNCERTAINTY.finditer(text):
            chaos_positions.append((match.start(), match.end(), match.group(), 'uncertainty'))
        
        # Sort reverse order
        chaos_positions.sort(key=lambda x: x[0], reverse=True)
        
        # Apply highlighting
        for start, end, word, type_ in chaos_positions:
            color = '#ff4444' if type_ == 'uncertainty' else '#ff8c00'
            result = (result[:start] + 
                     f'<span style="background-color: {color}; color: white; padding: 2px 6px; '
                     f'border-radius: 3px; font-weight: 500; margin: 0 2px;">{word}</span>' + 
                     result[end:])
        
        return result
    
    def process(self, text):
        """Transform text and return metrics"""
        if not text or not text.strip():
            return text, CoherenceMetrics(0.0, 0.0, 1.0, ProcessingState.OMEGA)
        
        # Initial chaos measurement
        psi_score = self.detect_chaos(text)
        
        result = text
        
        # Apply all transformations
        for pattern, replacement in self.TRANSFORMS:
            result = pattern.sub(replacement, result)
        
        # Clean up whitespace
        result = re.sub(r'\s+', ' ', result).strip()
        result = re.sub(r'\s+([.,!?;:])', r'\1', result)
        result = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', result)
        
        # Fix double spaces
        result = re.sub(r'  +', ' ', result)
        
        # Capitalize first letter
        if result:
            result = result[0].upper() + result[1:] if len(result) > 1 else result.upper()
        
        # Final chaos measurement
        final_chaos = self.detect_chaos(result)
        omega_score = 1.0 - final_chaos
        
        # Calculate delta
        if psi_score > 0:
            delta_score = max(0.0, min(1.0, (psi_score - final_chaos) / psi_score))
        else:
            delta_score = 0.0
        
        # Determine state
        if psi_score > 0.5:
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

# Custom CSS for modern design
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Headers */
    h1 {
        color: #1a1a1a;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        color: #2d2d2d;
        font-weight: 500;
    }
    
    /* Buttons - Green theme */
    .stButton button {
        background-color: #10b981 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    
    .stButton button:hover {
        background-color: #059669 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    }
    
    /* Text areas */
    .stTextArea textarea {
        border-radius: 8px !important;
        border: 2px solid #e5e7eb !important;
        font-size: 14px !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #10b981 !important;
        box-shadow: 0 0 0 1px #10b981 !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        color: #1a1a1a !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f9fafb;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f3f4f6;
        border-radius: 8px;
    }
    
    /* Success/Info messages */
    .stSuccess, .stInfo {
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# App Config
st.set_page_config(
    page_title="Luna Coherence",
    page_icon="🌙",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initialize
if 'framework' not in st.session_state:
    st.session_state.framework = LunaFramework()

# Header
st.title("Luna Coherence")
st.caption("Ψ² + Δ² = Ω² | Transform uncertain writing into confident communication")
st.markdown("---")

# Main Input
text_input = st.text_area(
    "Enter your text:",
    height=150,
    placeholder="Type or paste text with uncertain language...",
    key="main_text_input",
    value=st.session_state.get('example_to_load', '')
)

# Real-time highlighting
if text_input and text_input.strip():
    chaos_score = st.session_state.framework.detect_chaos(text_input)
    
    if chaos_score > 0.1:
        highlighted = st.session_state.framework.highlight_chaos(text_input)
        hedging_count = len(st.session_state.framework.HEDGING.findall(text_input))
        uncertainty_count = len(st.session_state.framework.UNCERTAINTY.findall(text_input))
        total_chaos = hedging_count + uncertainty_count
        
        with st.expander(f"Detected {total_chaos} uncertain phrase(s) - Click to view", expanded=False):
            st.markdown(highlighted, unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            col_a.metric("Hedging Words", hedging_count)
            col_b.metric("Uncertainty Phrases", uncertainty_count)

# Transform Button
if st.button("Transform Text", type="primary", use_container_width=True):
    if text_input and text_input.strip():
        with st.spinner("Processing..."):
            result, metrics = st.session_state.framework.process(text_input)
        
        # Results
        st.markdown("### Results")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Before:**")
            st.text_area("", value=text_input, height=130, disabled=True, key="display_before", label_visibility="collapsed")
            st.metric("Chaos Score (Ψ)", f"{metrics.psi_score:.2f}")
        
        with col2:
            st.markdown("**After:**")
            st.text_area("", value=result, height=130, disabled=True, key="display_after", label_visibility="collapsed")
            improvement = metrics.omega_score - metrics.psi_score
            st.metric("Coherence Score (Ω)", f"{metrics.omega_score:.2f}", delta=f"{improvement:+.2f}")
        
        # Additional Metrics
        st.markdown("---")
        col3, col4, col5 = st.columns(3)
        
        with col3:
            st.metric("Transform Power", f"{metrics.delta_score:.2f}")
        
        with col4:
            words_before = len(text_input.split())
            words_after = len(result.split())
            words_removed = max(0, words_before - words_after)
            st.metric("Words Removed", words_removed)
        
        with col5:
            st.metric("State", metrics.state.value.upper())
        
        # Feedback
        if metrics.delta_score > 0.5:
            st.success("Excellent! Your text is now significantly more confident.")
        elif metrics.delta_score > 0.2:
            st.info("Good improvement. Removed hedging language.")
        elif metrics.psi_score < 0.2:
            st.info("Your text was already fairly confident!")
        else:
            st.warning("Limited improvement. Try adding more direct language.")
    else:
        st.warning("Please enter text first.")

# Sidebar
with st.sidebar:
    st.markdown("### Quick Examples")
    st.caption("Click any example to test:")
    
    examples = {
        "Uncertain Email": "their team is doing better than us I don't know if ill be able to pull this off I need your help I don't if we should hire them or fire them its all been a mix up in my head",
        "Business Proposal": "I think maybe this could possibly be an interesting approach for our next quarter, perhaps we should consider it.",
        "Report Writing": "The results seem to be somewhat unclear and kind of ambiguous in their implications.",
        "Sales Pitch": "I believe our product might be able to help you solve this problem, probably better than competitors."
    }
    
    for name, example_text in examples.items():
        if st.button(name, key=f"ex_{name}", use_container_width=True):
            st.session_state.example_to_load = example_text
            st.rerun()
    
    if st.button("Clear", key="clear_btn", use_container_width=True):
        st.session_state.example_to_load = ''
        st.rerun()
    
    st.markdown("---")
    st.markdown("### How It Works")
    st.markdown("""
    **Luna removes:**
    - Hedging language (maybe, perhaps)
    - Uncertainty phrases (I don't know)
    - Weak qualifiers (kind of, sort of)
    
    **Perfect for:**
    - Professional emails
    - Business reports
    - LinkedIn posts  
    - Sales communications
    """)
    
    st.markdown("---")
    st.caption("**Created by Briana Luna**")
    st.caption("[Get API Access](#) | [Documentation](#)")
