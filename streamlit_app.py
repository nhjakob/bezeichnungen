#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Streamlit Slot Selector (3 Raeder) mit:
- Up/Down-Buttons pro Rad
- "Spin" mit weichem Auslaufen (Slot-Feeling)
- Ergebniszeile als Berufsbezeichnung (Level [+], Leistung + Rolle aus Disziplin)
- Regelwerk:
    * 'Mid-Level' wird im Ergebnis nicht gezeigt (neutraler Senioritaetsgrad)
    * 'Wissenschaft' + 'Text' -> 'Wissenschaftstexter:in'
    * 'Wissenschaft' + andere Disziplinen -> 'Wissenschafts' + <rollenstamm> + ':in'
    * 'Kommunikation' + Disziplin -> 'Kommunikations' + <rollenstamm> + ':in'
    * sonst: <Leistung-mit-Bindestrich>-<Rolle>
- THEME fuer Farben/Typo/Flächen (an Website-Style angelehnt)
"""

import streamlit as st
import time
import random
st.set_page_config(
    page_title="Slot-Selector (Streamlit)",
    page_icon="🎰",
    layout="wide",
)

THEME = {
    "bg": "#FFFFFF",
    "surface": "#F5F7FA",
    "text": "#0F172A",
    "muted": "#374151",
    "border": "#D1D5DB",
    "accent": "#00A886",
    "accent_surface": "#E6FFFA",
    "result_bg": "#0F766E",
}

st.markdown(
    f"""
    <style>
    .result-bar {{
        background: {THEME["result_bg"]};
        color: #fff;
        padding: 12px 16px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 1.08rem;
        margin-top: 12px;
        letter-spacing: .1px;
    }}
    .value-box {{
        background: #fff;
        border: 1px solid {THEME["border"]};
        border-radius: 12px;
        padding: 12px 14px;
        text-align: center;
        font-weight: 700;
        color: {THEME["text"]};
        box-shadow: 0 0 0 4px {THEME["accent_surface"]};
    }}
    .title {{
        font-weight: 800;
        color: {THEME["text"]};
        margin-bottom: 8px;
        font-size: 1.05rem;
        letter-spacing: .2px;
    }}
    .stButton > button {{
        background-color: {THEME["accent"]} !important;
        color: #ffffff !important;
        border: 0;
        border-radius: 10px;
        padding: 8px 12px;
        font-weight: 700;
        letter-spacing: .2px;
    }}
    .btn-secondary > button {{
        background-color: #F3F4F6 !important;
        color: {THEME["text"]} !important;
        border: 1px solid {THEME["border"]} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

CATEGORIES = [
    ("Level", ["Junior", "Mid-Level", "Senior"]),
    ("Leistung", [
        "Event",
        "Content",
        "Video",
        "Audio",
        "Social Media",
        "Dialog",
        "Kommunikation",
        "Wissenschaft",
        "Print",
    ]),
    ("Disziplin", ["Beratung", "Design", "Konzept", "Text"]),
]

ROLE_TITLE = {
    "Beratung": "Berater:in",
    "Design": "Designer:in",
    "Konzept": "Konzeptioner:in",
    "Text": "Texter:in",
}
ROLE_STEM = {
    "Beratung": "berater",
    "Design": "designer",
    "Konzept": "konzeptioner",
    "Text": "texter",
}
DEFAULT_ROLE_TITLE = "Spezialist:in"
DEFAULT_ROLE_STEM = "spezialist"

def clamp_mod(i: int, n: int) -> int:
    return 0 if n == 0 else (i % n)

def hyphenize(term: str) -> str:
    return "-".join(term.split())

def compose_title(level: str, leistung: str, disziplin: str) -> str:
    role_title = ROLE_TITLE.get(disziplin, DEFAULT_ROLE_TITLE)
    role_stem  = ROLE_STEM.get(disziplin, DEFAULT_ROLE_STEM)

    # Level-Praefix: Mid-Level unterdruecken
    level_prefix = "" if level == "Mid-Level" else (level + " ")

    # Wissenschaft / Kommunikation -> Zusammensetzungen mit -s
    if leistung == "Wissenschaft":
        return f"{level_prefix}Wissenschafts{role_stem}:in"
    if leistung == "Kommunikation":
        return f"{level_prefix}Kommunikations{role_stem}:in"

    # Standard: Leistung-Rolle
    leistung_h = hyphenize(leistung)  # z. B. Social-Media
    return f"{level_prefix}{leistung_h}-{role_title}"

if "indices" not in st.session_state:
    st.session_state.indices = [0 for _ in CATEGORIES]

def value_html(text: str) -> str:
    return f'<div class="value-box">{text}</div>'

def render_wheels() -> list:
    cols = st.columns(len(CATEGORIES), gap="large")
    value_placeholders = []
    for i, (title, options) in enumerate(CATEGORIES):
        with cols[i]:
            st.markdown(f'<div class="title">{title}</div>', unsafe_allow_html=True)

            # Up
            st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
            up_clicked = st.button("^", key=f"up_{i}")
            st.markdown('</div>', unsafe_allow_html=True)

            # Value
            value_ph = st.empty()
            idx = clamp_mod(st.session_state.indices[i], len(options))
            st.session_state.indices[i] = idx
            value_ph.markdown(value_html(options[idx]), unsafe_allow_html=True)

            # Down
            st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
            down_clicked = st.button("v", key=f"down_{i}")
            st.markdown('</div>', unsafe_allow_html=True)

            # Interaktion
            if up_clicked:
                st.session_state.indices[i] = clamp_mod(st.session_state.indices[i] - 1, len(options))
                value_ph.markdown(value_html(options[st.session_state.indices[i]]), unsafe_allow_html=True)
            if down_clicked:
                st.session_state.indices[i] = clamp_mod(st.session_state.indices[i] + 1, len(options))
                value_ph.markdown(value_html(options[st.session_state.indices[i]]), unsafe_allow_html=True)

            value_placeholders.append(value_ph)
    return value_placeholders

def current_values():
    vals = []
    for i, (_, options) in enumerate(CATEGORIES):
        vals.append(options[st.session_state.indices[i]])
    return vals

def render_result(result_ph=None):
    level, leistung, disziplin = current_values()
    title = compose_title(level, leistung, disziplin)
    html = f'<div class="result-bar">{title}</div>'
    if result_ph is None:
        st.markdown(html, unsafe_allow_html=True)
    else:
        result_ph.markdown(html, unsafe_allow_html=True)

def spin_animation(value_placeholders, result_placeholder):
    for i, (_, options) in enumerate(CATEGORIES):
        n = len(options)
        if n == 0:
            continue
        current_idx = st.session_state.indices[i]
        target_idx = random.randrange(n)
        loops = 1 + i
        steps = loops * n + ((target_idx - current_idx) % n)
        if steps == 0:
            steps = n

        base_s = 0.04
        extra_s = 0.09

        for k in range(steps):
            st.session_state.indices[i] = clamp_mod(st.session_state.indices[i] + 1, n)
            val = options[st.session_state.indices[i]]
            value_placeholders[i].markdown(value_html(val), unsafe_allow_html=True)
            render_result(result_placeholder)

            frac = 0 if steps == 1 else k / (steps - 1)
            time.sleep(base_s + frac * extra_s)

# Header
st.markdown(
    f"""
    <div style="background:{THEME['bg']};padding:8px 0 4px 0;">
      <h1 style="margin:0;color:{THEME['text']};font-weight:800;letter-spacing:.2px;">
        Auswahlräder &nbsp;<span style="color:{THEME['accent']}">Slot</span>
      </h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Wheels + Ergebnis
value_placeholders = render_wheels()
result_placeholder = st.empty()
render_result(result_placeholder)

# Actions
c1, c2, _ = st.columns([1, 1, 6])
with c1:
    spin = st.button("Spin", type="primary")
with c2:
    reset = st.button("Reset")

if reset:
    st.session_state.indices = [0 for _ in CATEGORIES]
    value_placeholders = render_wheels()
    render_result(result_placeholder)

if spin:
    spin_animation(value_placeholders, result_placeholder)
