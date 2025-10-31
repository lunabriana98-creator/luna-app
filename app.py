"""
LUNA COHERENCE COACH — Modern, transparent confidence writing app
Created by Briana Luna
"""
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional

import streamlit as st

# Optional share-card PNG generation
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


# =========================
# Domain model
# =========================
class ChangeType(Enum):
    HEDGING_REMOVED = "Hedging removed"
    UNCERTAINTY_REMOVED = "Uncertainty removed"
    WEAK_VERB_STRENGTHENED = "Weak verb strengthened"
    PASSIVE_TO_ACTIVE = "Passive → active"
    QUESTION_TO_STATEMENT = "Question → statement"
    QUALIFIER_REMOVED = "Qualifier removed"
    FILLER_REMOVED = "Filler removed"
    NEGATIVE_SELF_TALK_REFRAMED = "Negative self-talk reframed"
    INTENSIFIER_TONED_DOWN = "Intensifier toned down"
    GRAMMAR_FIXED = "Grammar fixed"


@dataclass
class Transformation:
    start: int
    end: int
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


# =========================
# Coach logic
# =========================
class LunaCoach:
    """The confidence writing coach — transparent & educational"""

    # Enhanced pattern library: broader "chaos detection"
    PATTERNS = {
        # Hedging
        "hedging": [
            (r"\bI think\b", "", "States sound stronger without hedging.", 14),
            (r"\bI think that\b", "", "Removes unnecessary thinking phrase.", 15),
            (r"\bI believe\b", "", "Belief ≠ evidence; say it directly.", 14),
            (r"\bI feel like\b", "", "Replace feelings with facts and actions.", 14),
            (r"\bmaybe\b", "", "Removes hedging to clarify intent.", 10),
            (r"\bperhaps\b", "", "Removes hedging to clarify intent.", 10),
            (r"\bpossibly\b", "", "Removes hedging to clarify intent.", 10),
            (r"\bprobably\b", "", "Removes hedging to clarify intent.", 10),
            (r"\b(kind|sort) of\b", "", "Eliminates vague qualifiers.", 12),
            (r"\bbasically\b", "", "Filler that weakens tone.", 8),
            (r"\bactually\b", "", "Often unnecessary emphasis.", 8),
        ],
        # Uncertainty
        "uncertainty": [
            (r"\bI don't know if\b", "", "State what you can do next.", 20),
            (r"\bI'm not sure\b", "", "Replace doubt with a decision or plan.", 18),
            (r"\bnot sure\b", "unclear", "Clarifies uncertainty to a clear term.", 15),
            (r"\bmixed up\b", "unclear", "Clarifies confusion.", 12),
        ],
        # Weak verbs
        "weak_verbs": [
            (r"\bmight be able to\b", "can", "Choose decisive capability.", 18),
            (r"\bcould be able to\b", "can", "Choose decisive capability.", 18),
            (r"\bwould be able to\b", "can", "Choose decisive capability.", 18),
            (r"\bmight be\b", "is", "Strengthens the claim.", 15),
            (r"\bcould be\b", "is", "Makes a definitive statement.", 15),
            (r"\bseems to be\b", "is", "Converts appearance to fact.", 15),
            (r"\bappears to be\b", "is", "States facts directly.", 15),
            (r"\btends to be\b", "is", "Smoother assertive phrasing.", 12),
        ],
        # Passive voice
        "passive": [
            (r"\b(is|are|was|were|be|been|being)\s+\w+(ed|en)\s+by\b", "", "Prefer active voice; name the actor.", 16),
        ],
        # Questions → statements (validation seeking / tentativeness)
        "questions": [
            (r"\?\s*$", ".", "Convert question to a decision-oriented statement.", 12),
            (r"\bWhat do you think\?\b", "", "Avoid validation-seeking; propose an action.", 15),
            (r"\bShould we\?\b", ".", "Decide and state the plan.", 15),
        ],
        # Filler / clutter
        "filler": [
            (r"\bjust\b", "", "Common minimizer; remove to strengthen tone.", 8),
            (r"\breally\b", "", "Intensifier that rarely adds precision.", 6),
            (r"\bvery\b", "", "Vague intensifier; replace with specifics.", 6),
            (r"\bkind of\b", "", "Vague—tighten phrasing.", 8),
        ],
        # Negative self-talk
        "neg_self": [
            (r"\bI need your help\b", "", "Shift from dependency to initiative.", 12),
            (r"\bI'm bad at\b", "I'm improving at", "Reframe into growth.", 14),
            (r"\bI can't\b", "I can", "Assert capability or next step.", 16),
            (r"\bI always mess up\b", "I’m learning from errors", "Replace global negative with growth.", 16),
            (r"\bsorry to bother\b", "", "Remove apology when not needed.", 18),
        ],
        # Grammar/small fixes
        "grammar": [
            (r"\bill\b", "I'll", "Fixes contraction.", 5),
            (r"\bits\b", "it's", "Adds missing apostrophe where needed.", 5),
            (r"\bdont\b", "don't", "Fix grammar.", 5),
            (r"\bdoesnt\b", "doesn't", "Fix grammar.", 5),
            (r"\bim\b", "I'm", "Fix grammar.", 5),
            (r"\s{2,}", " ", "Collapse repeated spaces.", 2),
        ],
        # Intensifiers (tone-down without losing meaning)
        "intensifiers": [
            (r"\balways\b", "", "Absolutes can sound reactive; remove or qualify.", 6),
            (r"\bnever\b", "", "Absolutes can sound reactive; remove or qualify.", 6),
            (r"\bextremely\b", "", "Over-intense; prefer specifics.", 6),
            (r"\bhighly\b", "", "Vague intensifier; prefer specifics.", 4),
        ],
    }

    CATEGORY_TO_TYPE = {
        "hedging": ChangeType.HEDGING_REMOVED,
        "uncertainty": ChangeType.UNCERTAINTY_REMOVED,
        "weak_verbs": ChangeType.WEAK_VERB_STRENGTHENED,
        "passive": ChangeType.PASSIVE_TO_ACTIVE,
        "questions": ChangeType.QUESTION_TO_STATEMENT,
        "grammar": ChangeType.GRAMMAR_FIXED,
        "filler": ChangeType.FILLER_REMOVED,
        "neg_self": ChangeType.NEGATIVE_SELF_TALK_REFRAMED,
        "intensifiers": ChangeType.INTENSIFIER_TONED_DOWN,
    }

    def detect_confidence(self, text: str) -> float:
        """Heuristic ‘confidence score’ 0–100 based on pattern density per word."""
        if not text or not text.strip():
            return 100.0
        words = max(1, len(text.split()))
        penalty = 0
        for category, patterns in self.PATTERNS.items():
            for pattern, _, _, impact in patterns:
                penalty += len(re.findall(pattern, text, re.IGNORECASE)) * impact
        # Normalize: more words dilute a single issue; scale by word count
        score = max(0.0, 100.0 - (penalty / words * 100.0))
        return min(100.0, score)

    def _iter_matches(self, text: str):
        """Yield (category, match, replacement, explanation, impact)."""
        for category, patterns in self.PATTERNS.items():
            for pattern, replacement, explanation, impact in patterns:
                for m in re.finditer(pattern, text, flags=re.IGNORECASE):
                    yield category, m, replacement, explanation, impact

    def transform_with_tracking(self, text: str) -> TransformationReport:
        """Apply all transformations while recording transparent, exact changes."""
        if not text or not text.strip():
            return TransformationReport(text, text, [], 100.0, 100.0, 0, 0)

        original = text
        confidence_before = self.detect_confidence(original)

        # We’ll apply changes left→right by character index to preserve offsets
        # Gather all matches first
        matches = []
        for category, m, replacement, explanation, impact in self._iter_matches(original):
            matches.append((m.start(), m.end(), category, m.group(0), replacement, explanation, impact))
        # Sort to apply deterministically
        matches.sort(key=lambda x: (x[0], x[1]))

        # Build transformed string with splice operations
        out = []
        last_idx = 0
        changes: List[Transformation] = []
        shift = 0  # net char shift so far (for display positions only)

        for start, end, category, before_text, replacement, explanation, impact in matches:
            # Append untouched span
            out.append(original[last_idx:start])
            after_text = replacement if replacement is not None else ""
            out.append(after_text)

            change_type = self.CATEGORY_TO_TYPE.get(category, ChangeType.QUALIFIER_REMOVED)
            changes.append(Transformation(
                start=start + shift,
                end=end + shift,
                before=before_text,
                after=after_text if after_text else "[removed]",
                change_type=change_type,
                explanation=explanation,
                confidence_impact=impact,
            ))

            # Update indices
            last_idx = end
            shift += len(after_text) - (end - start)

        out.append(original[last_idx:])
        transformed = "".join(out)

        # Cleanup spacing and punctuation
        transformed = re.sub(r"\s+", " ", transformed).strip()
        transformed = re.sub(r"\s+([.,!?;:])", r"\1", transformed)

        # Capitalize first letter
        if transformed:
            transformed = transformed[0].upper() + transformed[1:]

        confidence_after = self.detect_confidence(transformed)
        words_removed = max(0, len(original.split()) - len(transformed.split()))

        return TransformationReport(
            original=original,
            transformed=transformed,
            changes=changes,
            confidence_before=confidence_before,
            confidence_after=confidence_after,
            total_words_removed=words_removed,
            total_changes=len(changes),
        )


# =========================
# UI — Streamlit
# =========================
st.set_page_config(
    page_title="Luna Confidence Coach",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styles (no emojis) ----------
st.markdown("""
<style>
:root{
  --bg:#ffffff;
  --ink:#0f172a;
  --muted:#6b7280;
  --brand:#0ea5e9;
  --brand-600:#0284c7;
  --success:#10b981;
  --danger:#ef4444;
  --card:#ffffff;
  --ring:rgba(14,165,233,.25);
}
.stApp{background:linear-gradient(135deg,#ffffff 0%,#f6f7fb 100%);}
h1,h2,h3{letter-spacing:-0.02em;}
h1{font-weight:800;}
.gradient-text{
  background:linear-gradient(135deg,var(--brand),var(--success));
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
}
.card{
  background:var(--card);
  border-radius:14px;
  padding:18px 20px;
  box-shadow:0 4px 18px rgba(2,8,23,.06);
  border:1px solid rgba(2,8,23,.05);
}
.stat{
  text-align:center;
}
.stat .value{
  font-size:28px;
  font-weight:800;
}
.stat .label{
  color:var(--muted);
  font-size:12px;
}
.feed-item{
  background:#fff;
  border-left:4px solid var(--brand);
  border-radius:12px;
  padding:14px 16px;
  margin:8px 0;
  box-shadow:0 2px 10px rgba(2,8,23,.05);
}
.before{color:var(--danger);text-decoration:line-through;font-weight:600;}
.after{color:var(--success);font-weight:700;}
.badge{
  display:inline-block;background:#e0f2fe;color:#075985;
  padding:2px 10px;border-radius:999px;font-size:12px;font-weight:700;margin-left:8px;
}
.progress{height:8px;background:#e5e7eb;border-radius:6px;overflow:hidden;}
.progress > div{height:8px;background:linear-gradient(90deg,var(--brand),var(--success));}
.share{
  background:linear-gradient(135deg,var(--brand),var(--success));
  color:white;border-radius:16px;padding:24px 28px;box-shadow:0 8px 24px var(--ring);
}
.copy-btn button{width:100%;}
a.button-like{
  display:inline-block;padding:10px 14px;border-radius:10px;background:#0ea5e9;color:#fff;text-decoration:none;font-weight:700;
}
</style>
""", unsafe_allow_html=True)

# ---------- State ----------
if "coach" not in st.session_state:
    st.session_state.coach = LunaCoach()
if "history" not in st.session_state:
    st.session_state.history = []
if "report" not in st.session_state:
    st.session_state.report: Optional[TransformationReport] = None

# ---------- Header ----------
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<h1 class="gradient-text">Luna Confidence Coach</h1>', unsafe_allow_html=True)
    st.caption("Coaching that shows its work. Transparent, educational, and designed to be shared.")
with c2:
    st.markdown("")

# ---------- Input ----------
text = st.text_area(
    "Paste your text:",
    height=170,
    placeholder="Drop in a draft that feels uncertain, wordy, or passive...",
    key="main_input",
)

col_btn, = st.columns([1])
with col_btn:
    if st.button("Transform & explain", type="primary", use_container_width=True):
        if text and text.strip():
            report = st.session_state.coach.transform_with_tracking(text)
            st.session_state.report = report
            st.session_state.history.append(report)
        else:
            st.warning("Please enter some text first.")

# ---------- Results ----------
report: Optional[TransformationReport] = st.session_state.report

if report:
    st.markdown("---")
    st.subheader("Your transformation report")

    # Top stats
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown('<div class="card stat"><div class="value">{:.0f}/100</div><div class="label">Confidence score</div></div>'.format(report.confidence_after), unsafe_allow_html=True)
    with s2:
        delta = report.confidence_after - report.confidence_before
        st.markdown('<div class="card stat"><div class="value">+{:.0f}</div><div class="label">Improvement</div></div>'.format(delta), unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div class="card stat"><div class="value">{report.total_changes}</div><div class="label">Changes made</div></div>', unsafe_allow_html=True)
    with s4:
        st.markdown(f'<div class="card stat"><div class="value">{report.total_words_removed}</div><div class="label">Words removed</div></div>', unsafe_allow_html=True)

    # Before/After with one-click copy
    st.markdown("### Before / After")
    bcol, acol = st.columns(2)
    with bcol:
        st.markdown('<div class="card"><strong>Before</strong></div>', unsafe_allow_html=True)
        st.text_area("", value=report.original, height=160, disabled=True, label_visibility="collapsed", key="before_text")
    with acol:
        st.markdown('<div class="card"><strong>After</strong></div>', unsafe_allow_html=True)
        st.text_area("", value=report.transformed, height=160, label_visibility="collapsed", key="after_text")
        st.markdown("""
        <script>
        function copyAfter(){
            const el = window.parent.document.querySelector('textarea[data-testid="stTextArea-input"][aria-label="after_text"]');
            if(el){
                navigator.clipboard.writeText(el.value);
                const notice = window.parent.document.createElement('div');
                notice.textContent = 'Copied to clipboard';
                notice.style.position='fixed'; notice.style.right='16px'; notice.style.bottom='16px';
                notice.style.background='#0ea5e9'; notice.style.color='#fff'; notice.style.padding='8px 12px';
                notice.style.borderRadius='8px'; notice.style.fontWeight='700';
                window.parent.document.body.appendChild(notice);
                setTimeout(()=>notice.remove(),1200);
            }
        }
        </script>
        <a class="button-like" href="javascript:copyAfter()">Copy transformed text</a>
        """, unsafe_allow_html=True)

    # Transparent Transformation Feed
    st.markdown("### Visual transformation feed (what changed & why)")
    if report.changes:
        for i, ch in enumerate(report.changes, 1):
            st.markdown(f"""
            <div class="feed-item">
              <div style="font-size:13px;color:#64748b;margin-bottom:6px;">
                <strong>Change #{i}</strong> • {ch.change_type.value}
                <span class="badge">+{ch.confidence_impact} confidence</span>
              </div>
              <div style="font-size:16px;margin:8px 0;">
                <span class="before">{ch.before}</span>
                <span style="margin:0 8px;">→</span>
                <span class="after">{ch.after}</span>
              </div>
              <div style="font-size:13px;color:#475569;">{ch.explanation}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Your text was already confident—no edits needed.")

    # Learning Insights (coaching-focused)
    st.markdown("### Learning insights")
    insights = []
    text_lower = report.original.lower()

    def saw(pat: str) -> bool:
        return re.search(pat, text_lower) is not None

    if any(saw(p) for p in [r"\bi think\b", r"\bmaybe\b", r"\bperhaps\b", r"\bkind of\b"]):
        insights.append("Hedging makes readers do extra inference. Replace with concrete decisions and evidence.")
    if re.search(r"\b(is|are|was|were|be|been|being)\s+\w+(ed|en)\s+by\b", report.original, re.IGNORECASE):
        insights.append("Passive voice hides ownership. Name the actor and the action to increase clarity.")
    if any(saw(p) for p in [r"\bjust\b", r"\breally\b", r"\bvery\b"]):
        insights.append("Filler and intensifiers rarely add meaning. Prefer precise verbs and nouns.")
    if any(saw(p) for p in [r"\bi'm not sure\b", r"\bi don't know\b"]):
        insights.append("Uncertainty is okay—pair it with a next step so your message still moves forward.")
    if any(saw(p) for p in [r"\bsorry\b", r"\bi need your help\b"]):
        insights.append("Drop unneeded apologies and dependency language; state the ask clearly with context.")

    if insights:
        for tip in insights:
            st.markdown(f"- {tip}")
    else:
        st.markdown("- Your writing is already assertive and clear. Keep going.")

    # Shareable Results Card (+ download)
    st.markdown("### Share your results")
    card_html = f"""
    <div class="share">
        <h3 style="margin:0 0 12px 0;">Luna Transformation</h3>
        <div style="display:flex;gap:24px;flex-wrap:wrap;">
            <div><div style="opacity:.85;font-size:12px;">Before</div>
                 <div style="font-size:28px;font-weight:800;">{report.confidence_before:.0f}</div></div>
            <div style="align-self:center;font-size:28px;">→</div>
            <div><div style="opacity:.85;font-size:12px;">After</div>
                 <div style="font-size:28px;font-weight:800;">{report.confidence_after:.0f}</div></div>
            <div style="align-self:center;margin-left:auto;">
                <div style="opacity:.85;font-size:12px;text-align:right;">Changes • Words removed</div>
                <div style="font-size:20px;font-weight:800;text-align:right;">{report.total_changes} • {report.total_words_removed}</div>
            </div>
        </div>
        <div style="margin-top:12px;opacity:.9;font-size:12px;">Made with Luna Confidence Coach</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    # Downloads
    col_dl1, col_dl2, col_dl3 = st.columns(3)

    # PNG share card (Pillow)
    def make_png_card() -> Optional[bytes]:
        if not PIL_AVAILABLE:
            return None
        W, H = 860, 300
        im = Image.new("RGB", (W, H), (14, 165, 233))
        draw = ImageDraw.Draw(im)
        # Gradient-ish overlay block
        for x in range(W):
            c = int(185 + 70*(x/W))
            draw.line([(x,0),(x,H)], fill=(c, 250 - (x*40)//W, 210))
        # Text
        def t(x,y,s,sz=28,weight="bold"):
            try:
                f = ImageFont.truetype("DejaVuSans.ttf", sz)
            except:
                f = ImageFont.load_default()
            draw.text((x,y), s, fill=(255,255,255), font=f)
        t(24, 18, "Luna Transformation", 28)
        t(24, 80, f"Before: {report.confidence_before:.0f}", 24)
        t(24, 118, f"After:  {report.confidence_after:.0f}", 24)
        t(24, 168, f"Changes: {report.total_changes}", 22)
        t(24, 202, f"Words removed: {report.total_words_removed}", 22)
        t(24, 250, "Made with Luna Confidence Coach", 18)
        import io
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        return buf.getvalue()

    with col_dl1:
        png_bytes = make_png_card()
        if png_bytes:
            st.download_button("Download share card (PNG)", png_bytes, file_name="luna_share_card.png")
        else:
            st.download_button("Download share card (HTML)", card_html.encode("utf-8"), file_name="luna_share_card.html")

    # JSON export of changes
    import json
    export_payload = {
        "confidence_before": report.confidence_before,
        "confidence_after": report.confidence_after,
        "total_changes": report.total_changes,
        "total_words_removed": report.total_words_removed,
        "changes": [
            {
                "change_type": ch.change_type.value,
                "before": ch.before,
                "after": ch.after,
                "explanation": ch.explanation,
                "impact": ch.confidence_impact,
                "start": ch.start,
                "end": ch.end,
            } for ch in report.changes
        ],
        "original": report.original,
        "transformed": report.transformed,
    }

    with col_dl2:
        st.download_button("Download report (JSON)", json.dumps(export_payload, indent=2).encode("utf-8"), file_name="luna_report.json")

    with col_dl3:
        # Lightweight text “report card” for sharing
        txt_card = f"""Luna Transformation
Before: {report.confidence_before:.0f}
After:  {report.confidence_after:.0f}
Changes: {report.total_changes}
Words removed: {report.total_words_removed}
———
{report.transformed}
"""
        st.download_button("Download report (TXT)", txt_card.encode("utf-8"), file_name="luna_report.txt")

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### Quick examples")
    examples = {
        "Uncertain email": "their team is doing better than us I don't know if ill be able to pull this off i need your help i dont know if we should hire them or fire them its all been a mix up in my head",
        "Wishy-washy": "I think maybe we could possibly try this approach, perhaps next quarter if that seems like it might work?",
        "Over-qualified": "Sorry to bother you, but I was just wondering if maybe you might be able to help with this small request?",
        "Weak report": "The results seem to kind of suggest that we might be able to see some sort of improvement, probably.",
    }
    for name, text_ex in examples.items():
        if st.button(name, use_container_width=True, key=f"ex_{name}"):
            st.session_state.main_input = text_ex
            st.experimental_rerun()

    st.markdown("---")
    st.markdown("### Your progress")
    if st.session_state.history:
        total = len(st.session_state.history)
        avg_delta = sum(r.confidence_after - r.confidence_before for r in st.session_state.history) / total
        st.markdown(f'<div class="card stat"><div class="value">{total}</div><div class="label">Transformations</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card stat"><div class="value">+{avg_delta:.0f}</div><div class="label">Avg improvement</div></div>', unsafe_allow_html=True)
        # Visual bar of avg improvement
        pct = max(0, min(100, int(avg_delta)))
        st.markdown('<div class="progress"><div style="width:{}%"></div></div>'.format(pct), unsafe_allow_html=True)
    else:
        st.caption("Run a few transformations to see your improvement trend.")

    st.markdown("---")
    st.markdown("### How it coaches you")
    st.markdown("""
- Detects hedging, uncertainty, weak verbs, passive voice, filler, negative self-talk, and grammar noise.
- Shows every single change and explains why it matters.
- Teaches patterns to avoid, so you become naturally confident over time.
""")
    st.caption("Created by Briana Luna")
