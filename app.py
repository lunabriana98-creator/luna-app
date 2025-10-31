"""
LUNA COHERENCE COACH
The confidence writing coach that shows its work
Created by Briana Luna
"""
import streamlit as st
import re
from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum

class ChangeType(Enum):
    HEDGING_REMOVED = "Hedging Removed"
    UNCERTAINTY_REMOVED = "Uncertainty Removed"
    WEAK_VERB_STRENGTHENED = "Weak Verb Strengthened"
    PASSIVE_TO_ACTIVE = "Passive → Active"
    QUESTION_REMOVED = "Question Removed"
    QUALIFIER_REMOVED = "Qualifier Removed"
    GRAMMAR_FIXED = "Grammar Fixed"

@dataclass
class Transformation:
    before: str
    after: str
    change_type: ChangeType
    explanation: str
    confidence_impact: int

@dataclass
class TransformationReport:
    original: str
    transformed: str
    changes: List[Transformation]
    confidence_before: float
    confidence_after: float
    total_words_removed: int
    total_changes: int

class LunaCoach:
    """The confidence writing coach"""
    
    # Comprehensive pattern detection
    PATTERNS = {
        'hedging': [
            (r'\bI think that\b', '', "Removes unnecessary thinking phrases", 15),
            (r'\bI believe that\b', '', "Removes belief qualifiers", 15),
            (r'\bI guess that\b', '', "Eliminates guessing language", 15),
            (r'\bI feel like\b', '', "Replaces feelings with facts", 15),
            (r'\bmaybe\s*,?\s*', '', "Removes hedging", 10),
            (r'\bperhaps\s*,?\s*', '', "Removes hedging", 10),
            (r'\bpossibly\s*,?\s*', '', "Removes hedging", 10),
            (r'\bprobably\s*,?\s*', '', "Removes hedging", 10),
            (r'\b(kind|sort) of\b', '', "Eliminates weak qualifiers", 12),
            (r'\bbasically\b', '', "Removes filler", 8),
            (r'\bactually\b', '', "Removes unnecessary emphasis", 8),
        ],
        'uncertainty': [
            (r'\bI don\'t know if\b', '', "Removes uncertainty admission", 20),
            (r'\bI\'m not sure if\b', '', "Removes doubt", 20),
            (r'\bI don\'t know\b', '', "Removes uncertainty", 18),
            (r'\bnot sure\b', 'unclear', "Converts uncertainty to fact", 15),
            (r'\bmixed up\b', 'unclear', "Clarifies confusion", 15),
        ],
        'weak_verbs': [
            (r'\bmight be able to\b', 'can', "Strengthens capability", 18),
            (r'\bcould be able to\b', 'can', "Shows definite ability", 18),
            (r'\bwould be able to\b', 'can', "Demonstrates capability", 18),
            (r'\bmight be\b', 'is', "Strengthens statement", 15),
            (r'\bcould be\b', 'is', "Makes definitive claim", 15),
            (r'\bseems to be\b', 'is', "Converts appearance to fact", 15),
            (r'\bappears to be\b', 'is', "States facts directly", 15),
            (r'\btends to be\b', 'is', "Makes direct statement", 15),
        ],
        'questions': [
            (r'\?\s*$', '.', "Converts question to statement", 12),
            (r'What do you think\?', '', "Removes validation seeking", 15),
            (r'Should we\?', '.', "Makes decisive statement", 15),
        ],
        'grammar': [
            (r'\bill be able to\b', "I'll be able to", "Fixes contraction", 5),
            (r'\bits all been\b', "it's all been", "Fixes contraction", 5),
            (r'\bI dont\b', "I don't", "Fixes grammar", 5),
            (r'\bdont\b', "don't", "Fixes grammar", 5),
        ],
        'apologetic': [
            (r'\bI need your help\b', '', "Removes dependency language", 12),
            (r'\bsorry to bother\b', '', "Eliminates apologetic tone", 18),
            (r'\bjust wanted to\b', 'wanted to', "Removes minimizing", 10),
            (r'\bjust a\b', 'a', "Removes minimizing", 8),
        ]
    }
    
    def detect_confidence(self, text):
        """Calculate confidence score 0-100"""
        if not text or not text.strip():
            return 100
        
        words = len(text.split())
        if words == 0:
            return 100
        
        penalty = 0
        
        # Count all weak patterns
        for category, patterns in self.PATTERNS.items():
            for pattern, _, _, impact in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                penalty += matches * impact
        
        # Normalize to 0-100 scale
        confidence = max(0, 100 - (penalty / words * 100))
        return min(100, confidence)
    
    def transform_with_tracking(self, text):
        """Transform text and track every change"""
        if not text or not text.strip():
            return TransformationReport(text, text, [], 100, 100, 0, 0)
        
        original = text
        result = text
        changes = []
        
        # Track initial confidence
        confidence_before = self.detect_confidence(original)
        
        # Apply transformations and track each change
        for category, patterns in self.PATTERNS.items():
            for pattern, replacement, explanation, impact in patterns:
                matches = list(re.finditer(pattern, result, re.IGNORECASE))
                
                for match in matches:
                    before_text = match.group(0)
                    after_text = replacement if replacement else '[removed]'
                    
                    # Determine change type
                    if category == 'hedging':
                        change_type = ChangeType.HEDGING_REMOVED
                    elif category == 'uncertainty':
                        change_type = ChangeType.UNCERTAINTY_REMOVED
                    elif category == 'weak_verbs':
                        change_type = ChangeType.WEAK_VERB_STRENGTHENED
                    elif category == 'questions':
                        change_type = ChangeType.QUESTION_REMOVED
                    elif category == 'grammar':
                        change_type = ChangeType.GRAMMAR_FIXED
                    elif category == 'apologetic':
                        change_type = ChangeType.QUALIFIER_REMOVED
                    else:
                        change_type = ChangeType.QUALIFIER_REMOVED
                    
                    # Record the change
                    changes.append(Transformation(
                        before=before_text,
                        after=after_text,
                        change_type=change_type,
                        explanation=explanation,
                        confidence_impact=impact
                    ))
                
                # Apply the transformation
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Clean up text
        result = re.sub(r'\s+', ' ', result).strip()
        result = re.sub(r'\s+([.,!?;:])', r'\1', result)
        result = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', result)
        
        # Capitalize
        if result:
            result = result[0].upper() + result[1:] if len(result) > 1 else result.upper()
        
        # Calculate final confidence
        confidence_after = self.detect_confidence(result)
        
        # Calculate stats
        words_removed = len(original.split()) - len(result.split())
        
        return TransformationReport(
            original=original,
            transformed=result,
            changes=changes,
            confidence_before=confidence_before,
            confidence_after=confidence_after,
            total_words_removed=max(0, words_removed),
            total_changes=len(changes)
        )
        
# Initialize - MUST BE FIRST!
st.set_page_config(
    page_title="Luna Confidence Coach",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    }
    
    h1 {
        background: linear-gradient(135deg, #10b981, #059669);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        letter-spacing: -1px;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.3s !important;
    }
    
    .stButton button:hover {
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    .change-item {
        background: white;
        padding: 16px;
        border-radius: 12px;
        margin: 8px 0;
        border-left: 4px solid #10b981;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .before-text {
        color: #ef4444;
        font-weight: 600;
        text-decoration: line-through;
    }
    
    .after-text {
        color: #10b981;
        font-weight: 600;
    }
    
    .impact-badge {
        display: inline-block;
        background: #dcfce7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 8px;
    }
    
    .stats-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
    }
    
    .share-card {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 30px;
        border-radius: 16px;
        margin: 20px 0;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.3);
    }
    
    .progress-bar {
        height: 8px;
        background: #e5e7eb;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #10b981, #059669);
        transition: width 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
st.set_page_config(
    page_title="Luna Confidence Coach",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'coach' not in st.session_state:
    st.session_state.coach = LunaCoach()
if 'history' not in st.session_state:
    st.session_state.history = []

# Header
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("Luna Confidence Coach")
    st.caption("The only writing tool that shows you exactly how it makes you confident")

# Main Input
text_input = st.text_area(
    "Paste your text here:",
    height=150,
    placeholder="Type or paste any text with uncertain language...",
    key="main_input",
    value=st.session_state.get('load_example', '')
)

# Transform button
if st.button("🚀 Transform & Learn", type="primary", use_container_width=True):
    if text_input and text_input.strip():
        with st.spinner("Analyzing your confidence..."):
            report = st.session_state.coach.transform_with_tracking(text_input)
            st.session_state.current_report = report
            st.session_state.history.append(report)
        
        # Results Section
        st.markdown("---")
        st.markdown("## 📊 Your Transformation Report")
        
        # Top Stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            improvement = report.confidence_after - report.confidence_before
            st.metric(
                "Confidence Score",
                f"{report.confidence_after:.0f}/100",
                f"+{improvement:.0f}",
                delta_color="normal"
            )
        
        with col2:
            st.metric("Changes Made", report.total_changes)
        
        with col3:
            st.metric("Words Removed", report.total_words_removed)
        
        with col4:
            improvement_pct = (improvement / max(report.confidence_before, 1)) * 100
            st.metric("Improvement", f"{improvement_pct:.0f}%")
        
        # Before/After
        st.markdown("### ✨ Your Transformed Text")
        col_before, col_after = st.columns(2)
        
        with col_before:
            st.markdown("**Before:**")
            st.text_area("", value=report.original, height=150, disabled=True, key="show_before", label_visibility="collapsed")
        
        with col_after:
            st.markdown("**After:**")
            st.text_area("", value=report.transformed, height=150, key="show_after", label_visibility="collapsed")
            if st.button("📋 Copy Transformed Text", use_container_width=True):
                st.code(report.transformed, language=None)
                st.success("✅ Text ready to copy!")
        
        # Transformation Feed
        st.markdown("---")
        st.markdown("### 🎯 Every Change We Made (And Why)")
        
        if report.changes:
            for i, change in enumerate(report.changes, 1):
                st.markdown(f"""
                <div class="change-item">
                    <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">
                        <strong>Change #{i}</strong> • {change.change_type.value}
                    </div>
                    <div style="font-size: 16px; margin: 12px 0;">
                        <span class="before-text">{change.before}</span>
                        <span style="margin: 0 8px;">→</span>
                        <span class="after-text">{change.after}</span>
                        <span class="impact-badge">+{change.confidence_impact} confidence</span>
                    </div>
                    <div style="font-size: 14px; color: #4b5563; margin-top: 8px;">
                        💡 {change.explanation}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Your text was already confident! No changes needed.")
        
        # Shareable Card
        if report.changes:
            st.markdown("---")
            st.markdown("### 📸 Share Your Progress")
            
            st.markdown(f"""
            <div class="share-card">
                <h2 style="color: white; margin: 0 0 20px 0;">My Luna Transformation</h2>
                <div style="display: flex; justify-content: space-around; margin: 20px 0;">
                    <div>
                        <div style="font-size: 14px; opacity: 0.9;">Confidence Before</div>
                        <div style="font-size: 32px; font-weight: bold;">{report.confidence_before:.0f}</div>
                    </div>
                    <div style="font-size: 32px; align-self: center;">→</div>
                    <div>
                        <div style="font-size: 14px; opacity: 0.9;">Confidence After</div>
                        <div style="font-size: 32px; font-weight: bold;">{report.confidence_after:.0f}</div>
                    </div>
                </div>
                <div style="text-align: center; margin-top: 20px; opacity: 0.9;">
                    {report.total_changes} changes made • {report.total_words_removed} words removed
                </div>
                <div style="text-align: center; margin-top: 16px; font-size: 14px; opacity: 0.8;">
                    Transformed with Luna 🌙
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.caption("📸 Screenshot this card to share your improvement!")
    else:
        st.warning("Please enter some text first!")

# Sidebar
with st.sidebar:
    st.markdown("### 🎯 Quick Examples")
    
    examples = {
        "😰 Uncertain Email": "their team is doing better than us I don't know if ill be able to pull this off I need your help I don't if we should hire them or fire them its all been a mix up in my head",
        "🤔 Wishy-Washy": "I think maybe we could possibly try this approach, perhaps next quarter if that seems like it might work?",
        "💼 Over-Qualified": "Sorry to bother you, but I was just wondering if maybe you might be able to help with this small request?",
        "📊 Weak Report": "The results seem to kind of suggest that we might be able to see some sort of improvement, probably.",
    }
    
    for name, text in examples.items():
        if st.button(name, use_container_width=True, key=f"ex_{name}"):
            st.session_state.load_example = text
            st.rerun()
    
    if st.button("Clear", use_container_width=True):
        st.session_state.load_example = ''
        st.rerun()
    
    st.markdown("---")
    
    # Progress tracking
    if st.session_state.history:
        st.markdown("### 📈 Your Progress")
        total_transformations = len(st.session_state.history)
        avg_improvement = sum(r.confidence_after - r.confidence_before for r in st.session_state.history) / total_transformations
        
        st.metric("Transformations", total_transformations)
        st.metric("Avg Improvement", f"+{avg_improvement:.0f}")
        
        if total_transformations >= 5:
            st.success("🎉 You're building confidence!")
    
    st.markdown("---")
    st.markdown("### 💡 How Luna Works")
    st.markdown("""
    Luna analyzes your writing for:
    - 🎯 Hedging language
    - 😰 Uncertainty phrases
    - 💪 Weak verbs
    - ❓ Tentative questions
    - 📝 Grammar issues
    
    Then shows you **every change** and **why it matters**.
    """)
    
    st.markdown("---")
    st.caption("**Created by Briana Luna**")
    st.caption("Ψ² + Δ² = Ω²")
