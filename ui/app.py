"""Streamlit app — ReadyIQ (single native page: glass hero + live tribunal).

An Advocate and an Examiner debate a candidate's certification readiness; each
claim shows its source citation; the Judge renders a readiness verdict; a Curator
pulls live Microsoft Learn content; a human approves. All in one place.
Run: streamlit run ui/app.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from app.orchestration.graph import run_pipeline

CERTS = ["AZ-204", "AZ-400", "DP-203"]
_VERDICT_STYLE = {
    "READY":   ("✅", "#86efac", "rgba(34,197,94,.16)"),
    "ALMOST":  ("🟡", "#fcd34d", "rgba(245,158,11,.16)"),
    "NOT_YET": ("⛔", "#fca5a5", "rgba(239,68,68,.16)"),
}

st.set_page_config(page_title="ReadyIQ", page_icon="🎓", layout="wide")

# ------------------------------------------------------------------ theme + hero
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"], .stMarkdown, .stSelectbox, .stRadio { font-family:'Inter',sans-serif; }

.stApp{
  background:
    radial-gradient(900px 600px at 15% 6%, rgba(139,92,246,.30), transparent 60%),
    radial-gradient(800px 600px at 85% 10%, rgba(217,70,239,.24), transparent 60%),
    radial-gradient(900px 700px at 50% 112%, rgba(99,102,241,.26), transparent 60%),
    linear-gradient(160deg,#0d0a1f 0%, #140e2e 50%, #0d0a1f 100%);
  background-attachment: fixed;
}
[data-testid="stHeader"]{ background:transparent; }
.block-container{ position:relative; z-index:2; padding-top:2rem; max-width:1180px; }

/* floating product objects + drifting blobs (decorative, behind content) */
.riq-obj{ position:fixed; font-size:60px; z-index:0; pointer-events:none;
  filter:drop-shadow(0 12px 24px rgba(0,0,0,.45)); animation:riq-float 9s ease-in-out infinite; }
.riq-o1{ top:16%; left:3%;  font-size:72px; }
.riq-o2{ top:24%; right:4%; animation-delay:-2s; }
.riq-o3{ bottom:12%; left:5%; animation-delay:-4s; }
.riq-o4{ bottom:18%; right:4%; font-size:66px; animation-delay:-6s; }
@keyframes riq-float{ 0%,100%{transform:translateY(0) rotate(-6deg);} 50%{transform:translateY(-20px) rotate(6deg);} }
.riq-blob{ position:fixed; border-radius:50%; filter:blur(80px); opacity:.45; z-index:0; pointer-events:none; }
.riq-b1{ width:360px;height:360px;background:#8b5cf6;top:-90px;left:-60px; }
.riq-b2{ width:320px;height:320px;background:#d946ef;bottom:-90px;right:-50px; }

/* hero */
.riq-brand{ display:inline-flex;align-items:center;gap:.55rem;font-weight:800;letter-spacing:.06em;
  color:#cdc6ec;font-size:1.15rem;text-transform:uppercase; }
.riq-dot{ width:12px;height:12px;border-radius:50%;background:linear-gradient(135deg,#8b5cf6,#d946ef);box-shadow:0 0 14px #8b5cf6; }
.riq-title{ font-size:3.4rem;font-weight:900;letter-spacing:-.035em;line-height:1.04;margin:.3rem 0 0;color:#f5f3ff; }
.riq-title .g{ background:linear-gradient(90deg,#a78bfa,#e879f9);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent; }
.riq-sub{ color:#b9b3d6;font-size:1.08rem;margin:.5rem 0 0;max-width:720px;line-height:1.6; }

/* debate columns -> dark frosted glass */
[data-testid="column"]{
  background:rgba(255,255,255,0.05); backdrop-filter:blur(18px) saturate(140%);
  border:1px solid rgba(255,255,255,0.12); border-radius:22px; padding:22px 24px;
  box-shadow:0 16px 44px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.10);
}
[data-testid="column"] h3{ margin-top:.1rem;font-weight:700;color:#f5f3ff; }

/* expanders */
[data-testid="stExpander"]{ border:none !important;box-shadow:none !important; }
[data-testid="stExpander"] details{ background:rgba(168,85,247,.10);border:1px solid rgba(168,85,247,.22);border-radius:12px; }
[data-testid="stExpander"] summary{ font-size:.82rem;color:#c4b5fd; }

/* button */
.stButton > button{
  background:linear-gradient(90deg,#8b5cf6,#d946ef);color:#fff;border:none;border-radius:13px;
  padding:.7rem 1.8rem;font-weight:800;font-size:1.02rem;letter-spacing:.01em;
  box-shadow:0 14px 32px rgba(139,92,246,.42);transition:transform .12s ease, filter .12s ease;
}
.stButton > button:hover{ filter:brightness(1.08);transform:translateY(-2px);color:#fff; }

/* verdict pill + glass cards */
.riq-verdict{ display:inline-flex;align-items:center;gap:.5rem;padding:.6rem 1.3rem;border-radius:999px;
  font-weight:800;font-size:1.2rem;border:1px solid rgba(255,255,255,.18);box-shadow:0 10px 26px rgba(0,0,0,.35); }
.riq-card{ background:rgba(255,255,255,.05);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.12);
  border-radius:14px;padding:14px 16px;margin:.45rem 0;box-shadow:0 10px 26px rgba(0,0,0,.30); }
.riq-card a{ color:#c4b5fd;font-weight:600;text-decoration:none; }
.riq-card a:hover{ text-decoration:underline; }
.riq-card .ex{ color:#b9b3d6;font-size:.86rem;margin-top:.2rem; }
.riq-chip{ display:inline-block;background:rgba(255,255,255,.06);color:#c4b5fd;border:1px solid rgba(168,85,247,.30);
  border-radius:999px;padding:.22rem .8rem;font-size:.8rem;font-weight:600;backdrop-filter:blur(6px); }
</style>

<div class="riq-blob riq-b1"></div><div class="riq-blob riq-b2"></div>
<div class="riq-obj riq-o1">🎓</div><div class="riq-obj riq-o2">⚖️</div>
<div class="riq-obj riq-o3">📚</div><div class="riq-obj riq-o4">🧠</div>

<div>
  <span class="riq-brand"><span class="riq-dot"></span> ReadyIQ · Microsoft Agents League</span>
  <div class="riq-title">Test before <span class="g">the test</span></div>
  <div class="riq-sub">An Advocate and an Examiner debate a candidate's certification readiness.
  A Judge decides — every claim cited to the exam objectives or the candidate's record, refusing to guess.
  Grounded in Microsoft Foundry IQ, with live study content from the Microsoft Learn MCP.</div>
</div>
""", unsafe_allow_html=True)

st.write("")
cert = st.selectbox("Choose a certification to assess", CERTS)
st.markdown('<span class="riq-chip">Synthetic candidates · AZ-204 · AZ-400 · DP-203 · no real learner data</span>',
            unsafe_allow_html=True)
st.write("")

if st.button("⚖️  Check Readiness", type="primary"):
    try:
        with st.spinner("The Advocate and Examiner are building their cases…"):
            result = run_pipeline(cert)
    except ValueError:
        st.warning(f"No content is loaded for **{cert}**. "
                   f"This demo is pre-loaded with **AZ-204, AZ-400, DP-203**.")
        st.stop()

    evidence_by_id = {p.id: p for p in result.evidence}

    def render_claims(claims, color):
        for c in claims:
            src = evidence_by_id.get(c.citation_id)
            st.markdown(f":{color}[●] {c.text}")
            if src:
                with st.expander(f"source · {c.citation_id} ({src.filing} — {src.section})"):
                    st.write(src.text)

    adv_col, exm_col = st.columns(2, gap="large")
    with adv_col:
        st.subheader("🟢 Advocate — ready to sit")
        st.markdown("**Opening**")
        st.write(result.advocate.summary)
        render_claims(result.advocate.claims, "green")
        if result.advocate.rebuttal_summary:
            st.markdown("**Rebuttal**")
            st.write(result.advocate.rebuttal_summary)
            render_claims(result.advocate.rebuttal_claims, "green")
    with exm_col:
        st.subheader("🔴 Examiner — not yet ready")
        st.markdown("**Opening**")
        st.write(result.examiner.summary)
        render_claims(result.examiner.claims, "red")
        if result.examiner.rebuttal_summary:
            st.markdown("**Rebuttal**")
            st.write(result.examiner.rebuttal_summary)
            render_claims(result.examiner.rebuttal_claims, "red")

    st.divider()
    v = result.verdict
    icon, fg, bg = _VERDICT_STYLE.get(v.decision, ("⚖️", "#c7d2fe", "rgba(99,102,241,.16)"))
    st.markdown(
        f'<div class="riq-verdict" style="background:{bg};color:{fg}">'
        f'{icon}&nbsp; Verdict: {v.decision.replace("_", " ")} · {v.confidence:.0%} confidence</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.write(v.rationale)
    if v.next_step:
        st.markdown(f"**Recommended next step:** {v.next_step}")

    # Curator: live, official Microsoft Learn content via the Learn MCP (public docs, no PII).
    if v.decision != "READY":
        st.markdown("#### 📚 Study these next — live from Microsoft Learn")
        st.caption("Fetched in real time via the Microsoft Learn MCP server.")
        from app.tools.learn_mcp import search_learn
        query = f"{cert} {v.next_step or 'exam preparation study guide'}"
        with st.spinner("Fetching official Microsoft Learn content…"):
            modules = search_learn(query, k=3)
        if modules:
            for m in modules:
                title = m.get("title", "Microsoft Learn")
                url = m.get("url", "")
                ex = (m.get("excerpt", "") or "").replace("#", "").replace("\n", " ").strip()[:170]
                head = f'<a href="{url}" target="_blank">{title}</a>' if url else f"<b>{title}</b>"
                st.markdown(f'<div class="riq-card">{head}<div class="ex">{ex}…</div></div>',
                            unsafe_allow_html=True)
        else:
            st.caption("Live Microsoft Learn content is unavailable right now.")

    # Human-in-the-loop: advisory until a manager approves.
    st.divider()
    st.markdown("**👤 Manager review** &nbsp;·&nbsp; _human-in-the-loop gate_", unsafe_allow_html=True)
    decision = st.radio("This readiness verdict is:", ["Pending", "Approved", "Overridden"],
                        horizontal=True, index=0)
    if decision == "Approved":
        st.success("Verdict approved — the study plan / exam booking can proceed.")
    elif decision == "Overridden":
        st.info("Verdict overridden by manager — agents have no authority to act without approval.")

    with st.expander("🔍 Reasoning trace (audit log)"):
        st.json(result.trace)
