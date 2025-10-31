"""Luna Coherence - All-in-One Version with Grammar & Highlighting"""
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
    
    # Grammar-aware transformations
    TRANSFORMS = [
        # Remove thinking phrases
        (re.compile(r'\bI think that\b', re.I), ''),
        (re.compile(r'\bI believe that\b', re.I), ''),
        (re.compile(r'\bI guess that\b', re.I), ''),
        
        # Handle "able to" constructions properly
        (re.compile(r'\bwe might be able to\b', re.I), 'we can'),
        (re.compile(r'\bwe could be able to\b', re.I), 'we can'),
        (re.compile(r'\byou might be able to\b', re.I), 'you can'),
        (re.compile(r'\bI might be able to\b', re.I), 'I can'),
        (re.compile(r'\bthey might be able to\b', re.I), 'they can'),
        
        # Only replace might/could when it's safe
        (re.compile(r'\bmight be (interesting|good|useful|effective|possible|important)\b', re.I), r'is \1'),
        (re.compile(r'\bcould be (interesting|good|useful|effective|possible|important)\b', re.I), r'is \1'),
        
        # Safe removals
        (re.compile(r'\b(perhaps|maybe|possibly),?\s*', re.I), ''),
        (re.compile(r'\b(kind|sort) of\b', re.I), ''),
        
        # Replace weak verbs
        (re.compile(r'\bseems to be\b', re.I), 'is'),
        (re.compile(r'\bappears to be\b', re.I), 'is'),
        (re.compile(r'\btends to be\b', re.I), 'is'),
        
        # Question marks that add uncertainty
        (re.compile(r'\?\s*$', re.MULTILINE), '.'),
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
    
    def highlight_chaos(self, text):
        """Highlight chaos words in the text"""
        if not text:
            return ""
        
        result = text
        
        # Find all chaos words with their positions
        chaos_words = []
        for match in self.HEDGING.finditer(text):
            chaos_words.append((match.start(), match.end(), match.group()))
        for match in self.UNCERTAINTY.finditer(text):
            chaos_words.append((match.start(), match.end(), match.group()))
        
        # Sort by position (reverse so we can replace from end to start)
        chaos_words.sort(key=lambda x: x[0], reverse=True)
        
        # Wrap chaos words in HTML
        for start, end, word in chaos_words:
            result = result[:start] + f'<span style="background-color: #ff6b6b; color: white; padding: 2px 6px; border-radius: 4px; font-weight: 500;">{word}</span>' + result[end:]
        
        return result
    
    def process(self, text):
        if not text or not text.strip():
            return text, CoherenceMetrics(0.0, 0.0, 1.0, ProcessingState.OMEGA)
        
        psi_score = self.detect_chaos(text)
        result = text
        
        # Apply transformations
        for pattern, replacement in self.TRANSFORMS:
            result = pattern.sub(replacement, result)
        
        # Clean up whitespace and punctuation
        result = re.sub(r'\s+', ' ', result).strip()
        result = re.sub(r'\s+([.,!?])', r'\1', result)  # Fix spacing before punctuation
        result = re.sub(r'([.,!?])([A-Z])', r'\1 \2', result)  # Add space after punctuation
        
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
st.set_page_config(page_title="Luna Coherence", page_icon="🌙", layout="centered")

if 'framework' not in st.session_state:
    st.session_state.framework = LunaFramework()

st.title("🌙 Luna Coherence")
st.caption("Ψ² + Δ² = Ω² | Transform chaos into clarity")
st.markdown("---")

text_input = st.text_area(
    "Paste your text:",
    height=150,
    placeholder="I think maybe this could be interesting...",
    key="main_input"
)

# Real-time chaos highlighting
if text_input and text_input.strip():
    highlighted = st.session_state.framework.highlight_chaos(text_input)
    chaos_count = len(st.session_state.framework.HEDGING.findall(text_input))
    chaos_count += len(st.session_state.framework.UNCERTAINTY.findall(text_input))
    
    if chaos_count > 0:
        with st.expander(f"🔍 Found {chaos_count} chaos word(s) - Click to see", expanded=False):
            st.markdown(highlighted, unsafe_allow_html=True)
            st.caption("Red highlights show uncertainty and hedging language")

if st.button("✨ Transform", type="primary", use_container_width=True):
    if text_input and text_input.strip():
        with st.spinner("Transforming..."):
            result, metrics = st.session_state.framework.process(text_input)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📥 Before")
            st.text_area("before_label", value=text_input, height=120, disabled=True, key="before", label_visibility="collapsed")
            st.metric("Chaos (Ψ)", f"{metrics.psi_score:.2f}")
        
        with col2:
            st.subheader("📤 After")
            st.text_area("after_label", value=result, height=120, disabled=True, key="after", label_visibility="collapsed")
            improvement = metrics.omega_score - metrics.psi_score
            st.metric("Coherence (Ω)", f"{metrics.omega_score:.2f}", 
                     delta=f"{improvement:+.2f}")
        
        st.markdown("---")
        col3, col4, col5 = st.columns(3)
        
        with col3:
            st.metric("Transform Power (Δ)", f"{metrics.delta_score:.2f}")
        
        with col4:
            st.metric("State", metrics.state.value.upper())
        
        with col5:
            words_removed = len(text_input.split()) - len(result.split())
            st.metric("Words Removed", max(0, words_removed))
        
        # Success message based on improvement
        if metrics.delta_score > 0.5:
            st.success("✨ Excellent transformation! Your text is now much more confident.")
        elif metrics.delta_score > 0.2:
            st.info("👍 Good improvement! Removed hedging language.")
        else:
            st.info("✅ Your text was already fairly confident!")
        
    else:
        st.warning("⚠️ Enter some text first!")

# Sidebar
with st.sidebar:
    st.header("📚 Quick Examples")
    st.caption("Click to try:")
    
    examples = {
        "Business Email": "I think we might be able to get in the door quicker with the sales team. What do you think? Should we go that way?",
        "Report Writing": "The results are kind of unclear and somewhat ambiguous in their implications, perhaps requiring further analysis.",
        "Presentation": "I believe this proposal could possibly be worth considering for the next quarter, probably.",
        "LinkedIn Post": "Maybe this approach seems like it could be interesting for other founders. I guess it's worth sharing?"
    }
    
    for name, text in examples.items():
        if st.button(name, use_container_width=True):
            st.session_state.example_selected = text
            st.rerun()
    
    if 'example_selected' in st.session_state:
        st.info("👆 Example loaded! Scroll up to transform it.")
        if st.button("Clear Example", use_container_width=True):
            del st.session_state.example_selected
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("""
    **Luna removes:**
    - Hedging words (maybe, perhaps)
    - Uncertainty phrases (I think, kind of)
    - Weak language patterns
    
    **Perfect for:**
    - 📧 Professional emails
    - 📝 Reports & proposals
    - 💼 LinkedIn posts
    - 🎯 Sales copy
    """)

st.markdown("---")
st.caption("Created by **Briana Luna** | [Get Pro Version](#) for API access")

# Handle example loading
if 'example_selected' in st.session_state:
    st.session_state.main_input = st.session_state.example_selected
    del st.session_state.example_selected
    st.rerun()
