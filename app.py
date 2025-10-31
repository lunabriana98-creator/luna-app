"""
LUNA CONFIDENCE COACH — Pro Edition (Minimal & Elegant)
Author: Briana Luna
Notes:
- No emojis.
- Sidebar replaced with AI Dashboard (trend, streak, growth meter, quick exports).
- Accessibility: all widgets have non-empty labels (hidden when needed).
- Fixes Streamlit session_state mutation and label warnings.
"""

import re
import json
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from datetime import datetime, timezone

import streamlit as st

# Optional PNG share card
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
    created_at_iso: str


# =========================
# Coach logic
# =========================
class LunaCoach:
    """Confidence writing coach — transparent & educational."""

    PATTERNS = {
        "hedging": [
            (r"\bI think that\b", "", "Removes unnecessary thinking phrase.", 15),
            (r"\bI think\b", "", "States sound stronger without hedging.", 14),
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
        "uncertainty": [
            (r"\bI don't know if\b", "", "State what you can do next.", 20),
            (r"\bI'm not sure\b", "", "Replace doubt with a decision or plan.", 18),
            (r"\bnot sure\b", "unclear", "Clarifies uncertainty to a clear term.", 15),
            (r"\bmixed up\b", "unclear", "Clarifies confusion.", 12),
        ],
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
        "passive": [
            (r"\b(is|are|was|were|be|been|being)\s+\w+(ed|en)\s+by\b", "", "Prefer active voice; name the actor.", 16),
        ],
        "questions": [
            (r"\bWhat do you think\?\b", "", "Avoid validation-seeking; propose an action.", 15),
            (r"\bShould we\?\b", ".", "Decide and state the plan.", 15),
            (r"\?\s*$", ".", "Convert question to a decision-oriented statement.", 12),
        ],
        "filler": [
            (r"\bjust\b", "", "Common minimizer; remove to strengthen tone.", 8),
            (r"\breally\b", "", "Intensifier that rarely adds precision.", 6),
            (r"\bvery\b", "", "Vague intensifier; replace with specifics.", 6),
            (r"\bkind of\b", "", "Vague—tighten phrasing.", 8),
        ],
        "neg_self": [
            (r"\bI need your help\b", "", "Shift from dependency to initiative.", 12),
            (r"\bI'm bad at\b", "I'm improving at", "Reframe into growth.", 14),
            (r"\bI can't\b", "I can", "Assert capability or next step.", 16),
            (r"\bI always mess up\b", "I’m learning from errors", "Replace global negative with growth.", 16),
            (r"\bsorry to bother\b", "", "Remove apology when not needed.", 18),
        ],
        "grammar": [
            (r"\bill\b", "I'll", "Fixes contraction.", 5),
            (r"\bits\b", "it's", "Adds missing apostrophe where needed.", 5),
            (r"\bdont\b", "don't", "Fix grammar.", 5),
            (r"\bdoesnt\b", "doesn't", "Fix grammar.", 5),
            (r"\bim\b", "I'm", "Fix grammar.", 5),
            (r"\s{2,}", " ", "Collapse repeated spaces.", 2),
        ],
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
        if not text or not text.strip():
            return 100.0
        words = max(1, len(text.split()))
        penalty = 0
        for patterns in self.PATTERNS.values():
            for pattern, _, _, impact in patterns:
                penalty += len(re.findall(pattern, text, re.IGNORECASE)) * impact
        score = max(0.0, 100.0 - (penalty / words * 100.0))
        return min(100.0, score)

    def _iter_matches(self, text: str):
        for category, patterns in self.PATTERNS.items():
            for pattern, replacement, explanation, impact in patterns:
                for m in re.finditer(pattern, text, flags=re.IGNORECASE):
                    yield category, m, replacement, explanation, impact

    def transform_with_tracking(self, text: str) -> TransformationReport:
        if not text or not text.strip():
            now_iso = datetime.now(timezone.utc).isoformat()
            return TransformationReport(text, text, [], 100.0, 100.0, 0, 0, now_iso)

        original = text
        confidence_before = self.detect_confidence(original)

        matches = []
        for category, m, replacement, explanation, impact in self._iter_matches(original):
            matches.append((m.start(), m.end(), category, m.group(0), replacement, explanation, impact))
        matches.sort(key=lambda x: (x[0], x[1]))

        out = []
        last_idx = 0
        changes: List[Transformation] = []
        shift = 0

        for start, end, category, before_text, replacement, explanation, impact in matches:
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

            last_idx = end
            shift += len(after_text) - (end - start)

        out.append(original[last_idx:])
        transformed = "".join(out)

        transformed = re.sub(r"\s+", " ", transformed).strip()
        transformed = re.sub(r"\s+([.,!?;:])", r"\1", transformed)
        if transformed:
            transformed = transformed[0].upper() + transformed[1:]

        confidence_after = self.detect_confidence(transformed)
        words_removed = max(0, len(original.split()) - len(transformed.split()))
        now_iso = datetime.now(timezone.utc).isoformat()

        return TransformationReport(
            original=original,
            transformed=transformed,
            changes=changes,
            confidence_before=confidence_before,
            confidence_after=confidence_after,
            total_words_removed=words_removed,
            total_changes=len(changes),
            created_at_iso=now_iso,
        )


# =========================
# UI — Streamlit
# =========================
st.set_page_config(page_title="Luna Confidence Coach", layout="wide", initial_sidebar_state="expanded")

# ---------- State ----------
if "coach" not in st.session_state:
    st.session_state.coach = LunaCoach()
if "history" not in st.session_state:
    st.session_state.history: List[TransformationReport] = []
if "report" not in st.session_state:
    st.session_state.report: Optional[TransformationReport] = None
if "theme_dark" not in st.session_state:
    st.session_state.theme_dark = False

# ---------- Styles ----------
# Minimal & Elegant theme (light by default)
base_css = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --bg: #fbfbfd;
  --panel: #ffffff;
  --ink: #0b1220;
  --muted: #667085;
  --border: rgba(2,8,23,0.08);
  --shadow: 0 8px 24px rgba(2,8,23,0.06);
  --brand: #0ea5e9;
  --brand-600:#0284c7;
  --success:#10b981;
  --danger:#ef4444;
  --ring: rgba(14,165,233,.25);
}

.dark :root{
  --bg: #0b0e14;
  --panel: #0f131a;
  --ink: #e5ecf6;
  --muted: #9aa5b1;
  --border: rgba(229,236,246,0.08);
  --shadow: 0 12px 30px rgba(0,0,0,0.35);
  --brand: #38bdf8;
  --brand-600:#0ea5e9;
  --success:#34d399;
  --danger:#f87171;
  --ring: rgba(56,189,248,.2);
}

.stApp{
  font-family: 'Inter', sans-serif;
  background: var(--bg);
}
h1,h2,h3 { letter-spacing: -0.02em; color: var(--ink); }
.caption, .stCaption, .stMarkdown p { color: var(--ink); }
.card{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 18px 20px;
  box-shadow: var(--shadow);
}
.card.glass{
  backdrop-filter: saturate(140%) blur(8px);
  background: linear-gradient(180deg, rgba(255,255,255,0.72), rgba(255,255,255,0.68));
  border: 1px solid rgba(255,255,255,0.55);
}
.dark .card.glass{
  background: linear-gradient(180deg, rgba(17,21,29,0.55), rgba(17,21,29,0.5));
  border: 1px solid rgba(255,255,255,0.06);
}
.stat .value{ font-size: 28px; font-weight: 800; color: var(--ink); }
.stat .label{ color: var(--muted); font-size: 12px; }
.feed-item{
  border-left: 4px solid var(--brand);
  border-radius: 14px;
  padding: 14px 16px;
  background: var(--panel);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  opacity: 0;
  transform: translateY(10px);
  animation: fadeInUp .35s ease forwards;
}
@keyframes fadeInUp { to{ opacity:1; transform:none; } }
.before{ color: var(--danger); text-decoration: line-through; font-weight: 600; }
.after{ color: var(--success); font-weight: 700; }
.badge{
  display:inline-block; background: rgba(14,165,233,.12); color: var(--brand-600);
  padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; margin-left: 8px;
}
.progress{ height: 8px; background: rgba(2,8,23,0.08); border-radius: 6px; overflow: hidden; }
.progress > div{ height: 8px; background: linear-gradient(90deg, var(--brand), var(--success)); }
.topbar{
  display:flex; align-items:center; justify-content:space-between;
  padding: 8px 12px; border-bottom: 1px solid var(--border); margin-bottom: 8px;
}
.brand{ font-weight: 800; letter-spacing:-0.02em; }
.switch-row{ display:flex; align-items:center; gap:10px; color: var(--muted); font-size: 13px; }
a.button-like{
  display:inline-block; padding:10px 14px; border-radius:10px;
  background: var(--brand); color:#fff; text-decoration:none; font-weight:700;
}
.small{ font-size: 12px; color: var(--muted); }
</style>
"""
st.markdown(base_css, unsafe_allow_html=True)

# ----- Top bar with theme toggle -----
top_l, top_r = st.columns([3, 1])
with top_l:
    st.markdown('<div class="topbar"><div class="brand">Luna Confidence Coach</div><div></div></div>', unsafe_allow_html=True)
with top_r:
    theme_choice = st.toggle("Dark mode", value=st.session_state.theme_dark)
    st.session_state.theme_dark = theme_choice
    # Apply a CSS class to body based on theme (simulate by injecting a small script)
    st.markdown("""
    <script>
      const root = window.parent.document.querySelector('html');
      if (%s){ root.classList.add('dark'); } else { root.classList.remove('dark'); }
    </script>
    """ % ("true" if st.session_state.theme_dark else "false"), unsafe_allow_html=True)

# ---------- Main layout ----------
main_left, main_right = st.columns([7, 5])

# ===== Left: Editor & Transformation =====
with main_left:
    st.markdown('<div class="card glass">', unsafe_allow_html=True)
    st.markdown("### Compose")
    text = st.text_area(
        "Write or paste your draft",
        height=190,
        placeholder="Write something that feels tentative, wordy, or passive…",
        key="main_input",
        label_visibility="visible",
    )
    run_col = st.columns([1])[0]
    with run_col:
        if st.button("Transform & explain", type="primary", use_container_width=True):
            if text and text.strip():
                report = st.session_state.coach.transform_with_tracking(text)
                st.session_state.report = report
                st.session_state.history.append(report)
            else:
                st.warning("Please enter some text first.")
    st.markdown('</div>', unsafe_allow_html=True)

    report: Optional[TransformationReport] = st.session_state.report
    if report:
        st.markdown('<div class="card" style="margin-top:12px;">', unsafe_allow_html=True)
        st.markdown("### Before / After")

        bcol, acol = st.columns(2)
        with bcol:
            st.text_area(
                "Before text",
                value=report.original,
                height=170,
                disabled=True,
                label_visibility="collapsed",
                key="before_text_view",
            )
        with acol:
            st.text_area(
                "After text",
                value=report.transformed,
                height=170,
                label_visibility="collapsed",
                key="after_text_view",
            )
            # one-click copy (no empty labels)
            st.markdown("""
            <script>
            function copyAfter(){
                const el = window.parent.document.querySelector('textarea[aria-label="after_text_view"]');
                if(el){
                    navigator.clipboard.writeText(el.value);
                    const notice = window.parent.document.createElement('div');
                    notice.textContent = 'Copied';
                    notice.style.position='fixed'; notice.style.right='16px'; notice.style.bottom='16px';
                    notice.style.background='var(--brand)'; notice.style.color='#fff'; notice.style.padding='8px 12px';
                    notice.style.borderRadius='8px'; notice.style.fontWeight='700'; notice.style.zIndex='9999';
                    window.parent.document.body.appendChild(notice);
                    setTimeout(()=>notice.remove(),1000);
                }
            }
            </script>
            <a class="button-like" href="javascript:copyAfter()">Copy transformed text</a>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Stats
        st.markdown('<div class="card" style="margin-top:12px;">', unsafe_allow_html=True)
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown(f'<div class="stat"><div class="value">{report.confidence_after:.0f}/100</div><div class="label">Confidence</div></div>', unsafe_allow_html=True)
        with s2:
            delta = report.confidence_after - report.confidence_before
            st.markdown(f'<div class="stat"><div class="value">+{delta:.0f}</div><div class="label">Improvement</div></div>', unsafe_allow_html=True)
        with s3:
            st.markdown(f'<div class="stat"><div class="value">{report.total_changes}</div><div class="label">Changes</div></div>', unsafe_allow_html=True)
        with s4:
            st.markdown(f'<div class="stat"><div class="value">{report.total_words_removed}</div><div class="label">Words removed</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Transparent transformation feed
        st.markdown('<div class="card" style="margin-top:12px;">', unsafe_allow_html=True)
        st.markdown("### Transformation feed (what changed & why)")
        if report.changes:
            for i, ch in enumerate(report.changes, 1):
                st.markdown(f"""
                <div class="feed-item">
                  <div style="font-size:13px;color:var(--muted);margin-bottom:6px;">
                    <strong>Change #{i}</strong> • {ch.change_type.value}
                    <span class="badge">+{ch.confidence_impact} confidence</span>
                  </div>
                  <div style="font-size:16px;margin:8px 0;">
                    <span class="before">{ch.before}</span>
                    <span style="margin:0 8px;">→</span>
                    <span class="after">{ch.after}</span>
                  </div>
                  <div class="small">{ch.explanation}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Your text was already confident—no edits needed.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Learning insights
        st.markdown('<div class="card" style="margin-top:12px;">', unsafe_allow_html=True)
        st.markdown("### Learning insights")
        insights = []
        tl = report.original.lower()
        def saw(pat: str) -> bool: return re.search(pat, tl) is not None
        if any(saw(p) for p in [r"\bi think\b", r"\bmaybe\b", r"\bperhaps\b", r"\bkind of\b"]):
            insights.append("Hedging makes readers do extra inference. Replace with concrete decisions and evidence.")
        if re.search(r"\b(is|are|was|were|be|been|being)\s+\w+(ed|en)\s+by\b", report.original, re.IGNORECASE):
            insights.append("Passive voice hides ownership. Name the actor and action to increase clarity.")
        if any(saw(p) for p in [r"\bjust\b", r"\breally\b", r"\bvery\b"]):
            insights.append("Filler and intensifiers rarely add meaning. Prefer precise verbs and nouns.")
        if any(saw(p) for p in [r"\bi'm not sure\b", r"\bi don't know\b"]):
            insights.append("Pair uncertainty with a next step so your message still moves forward.")
        if any(saw(p) for p in [r"\bsorry\b", r"\bi need your help\b"]):
            insights.append("Drop unneeded apologies; state the ask clearly with context.")
        if insights:
            for tip in insights: st.markdown(f"- {tip}")
        else:
            st.markdown("- Your writing is already assertive and clear. Keep going.")
        st.markdown('</div>', unsafe_allow_html=True)

# ===== Right: AI Dashboard (pro vibe) =====
with main_right:
    st.markdown('<div class="card glass">', unsafe_allow_html=True)
    st.markdown("### AI Dashboard")

    # Confidence trend & usage metrics
    total = len(st.session_state.history)
    if total:
        avg_delta = sum(r.confidence_after - r.confidence_before for r in st.session_state.history) / total
        best_after = max(r.confidence_after for r in st.session_state.history)
    else:
        avg_delta, best_after = 0.0, 0.0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat"><div class="value">{total}</div><div class="label">Transformations</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat"><div class="value">+{avg_delta:.0f}</div><div class="label">Avg improvement</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat"><div class="value">{best_after:.0f}</div><div class="label">Best confidence</div></div>', unsafe_allow_html=True)

    # Growth meter (based on last delta)
    if total:
        delta_last = st.session_state.history[-1].confidence_after - st.session_state.history[-1].confidence_before
        pct = int(max(0, min(100, delta_last)))
    else:
        pct = 0
    st.markdown("#### Confidence Growth Meter")
    st.markdown(f'<div class="progress"><div style="width:{pct}%"></div></div>', unsafe_allow_html=True)
    st.caption("Measures improvement from your most recent transformation.")

    # Confidence trend chart (simple)
    st.markdown("#### Confidence trend")
    import pandas as pd
    if total:
        df = pd.DataFrame({
            "Run": list(range(1, total+1)),
            "Confidence (after)": [r.confidence_after for r in st.session_state.history]
        })
        st.line_chart(df, x="Run", y="Confidence (after)", height=180)
    else:
        st.caption("Run a few transformations to see the trend.")

    # Session streak (days in a row used — session-scoped approximation)
    # Track days used in this session; persist in session_state only.
    if "days_used" not in st.session_state:
        st.session_state.days_used = set()
    # Record today (UTC) if a transformation happened
    if total:
        last_day = st.session_state.history[-1].created_at_iso[:10]
        st.session_state.days_used.add(last_day)

    streak = len(st.session_state.days_used)
    st.markdown("#### Session streak")
    st.markdown(f'<div class="stat"><div class="value">{streak}</div><div class="label">Days active (this session)</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Share / export card
    st.markdown('<div class="card" style="margin-top:12px;">', unsafe_allow_html=True)
    st.markdown("### Share & Export")
    report = st.session_state.report
    if report:
        # Share card HTML
        card_html = f"""
        <div style="background:linear-gradient(180deg,rgba(14,165,233,.12),rgba(16,185,129,.10));border:1px solid var(--border);border-radius:16px;padding:16px;">
            <div style="display:flex;gap:24px;flex-wrap:wrap;align-items:center;">
                <div>
                    <div class="small">Before</div>
                    <div style="font-weight:800;font-size:24px;color:var(--ink);">{report.confidence_before:.0f}</div>
                </div>
                <div style="opacity:.7;font-size:24px;">→</div>
                <div>
                    <div class="small">After</div>
                    <div style="font-weight:800;font-size:24px;color:var(--ink);">{report.confidence_after:.0f}</div>
                </div>
                <div style="margin-left:auto;">
                    <div class="small" style="text-align:right;">Changes • Words removed</div>
                    <div style="font-weight:800;font-size:18px;color:var(--ink);text-align:right;">{report.total_changes} • {report.total_words_removed}</div>
                </div>
            </div>
            <div class="small" style="margin-top:8px;">Made with Luna Confidence Coach</div>
        </div>
        """

        # PNG maker
        def make_png_card(rep: TransformationReport) -> Optional[bytes]:
            if not PIL_AVAILABLE:
                return None
            W, H = 900, 280
            im = Image.new("RGB", (W, H), (245, 247, 250))
            draw = ImageDraw.Draw(im)
            # Subtle gradient
            for y in range(H):
                tone = 245 - int(10 * y / H)
                draw.line([(0, y), (W, y)], fill=(tone, tone, 250))
            def t(x,y,s,sz=26):
                try:
                    f = ImageFont.truetype("DejaVuSans.ttf", sz)
                except:
                    f = ImageFont.load_default()
                draw.text((x,y), s, fill=(20, 25, 33), font=f)
            t(24, 18, "Luna Transformation", 28)
            t(24, 80, f"Before: {rep.confidence_before:.0f}")
            t(24, 118, f"After:  {rep.confidence_after:.0f}")
            t(24, 166, f"Changes: {rep.total_changes}")
            t(24, 204, f"Words removed: {rep.total_words_removed}")
            import io
            buf = io.BytesIO()
            im.save(buf, format="PNG")
            return buf.getvalue()

        col_dl1, col_dl2, col_dl3 = st.columns(3)
        with col_dl1:
            png_bytes = make_png_card(report)
            if png_bytes:
                st.download_button("Download share card (PNG)", png_bytes, file_name="luna_share_card.png")
            else:
                st.download_button("Download share card (HTML)", card_html.encode("utf-8"), file_name="luna_share_card.html")
        with col_dl2:
            payload = {
                "confidence_before": report.confidence_before,
                "confidence_after": report.confidence_after,
                "total_changes": report.total_changes,
                "total_words_removed": report.total_words_removed,
                "created_at": report.created_at_iso,
                "changes": [
                    {
                        "change_type": ch.change_type.value,
                        "before": ch.before,
                        "after": ch.after,
                        "explanation": ch.explanation,
                        "impact": ch.confidence_impact,
                        "start": ch.start, "end": ch.end
                    } for ch in report.changes
                ],
                "original": report.original,
                "transformed": report.transformed,
            }
            st.download_button("Download report (JSON)", json.dumps(payload, indent=2).encode("utf-8"), file_name="luna_report.json")
        with col_dl3:
            txt_card = f"""Luna Transformation
Before: {report.confidence_before:.0f}
After:  {report.confidence_after:.0f}
Changes: {report.total_changes}
Words removed: {report.total_words_removed}
———
{report.transformed}
"""
            st.download_button("Download report (TXT)", txt_card.encode("utf-8"), file_name="luna_report.txt")
    else:
        st.caption("Run a transformation to enable sharing & export.")
    st.markdown('</div>', unsafe_allow_html=True)
