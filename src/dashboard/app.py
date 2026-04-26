import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime

# ── Configuration de la page ──────────────────────────────────────────────────
st.set_page_config(
    page_title="PLBD – Supervision Batterie",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS personnalisé ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif;
    background-color: #0a0e1a;
    color: #e0e8ff;
}

.main { background-color: #0a0e1a; }

h1, h2, h3 { color: #e0e8ff; }

/* Titre principal */
.title-block {
    text-align: center;
    padding: 1.5rem 0 1rem;
    border-bottom: 1px solid #1e2d50;
    margin-bottom: 1.5rem;
}
.title-block h1 {
    font-family: 'Exo 2', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #7eb8f7;
    margin: 0;
}
.title-block p {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: #4a6fa5;
    margin: 4px 0 0;
    letter-spacing: 0.2em;
}

/* Carte métrique principale */
.metric-card {
    background: linear-gradient(135deg, #0d1730 0%, #111d38 100%);
    border: 1px solid #1e3060;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
}
.metric-card.green::before  { background: #22c55e; }
.metric-card.orange::before { background: #f97316; }
.metric-card.red::before    { background: #ef4444; }

.metric-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.18em;
    color: #4a6fa5;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.metric-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.4rem;
    font-weight: 400;
    color: #e0e8ff;
    line-height: 1;
}
.metric-unit {
    font-size: 1rem;
    color: #4a6fa5;
    margin-left: 4px;
}
.metric-sub {
    font-size: 0.78rem;
    color: #4a6fa5;
    margin-top: 6px;
}

/* Barre SOC */
.soc-bar-bg {
    background: #0d1730;
    border: 1px solid #1e3060;
    border-radius: 8px;
    height: 28px;
    overflow: hidden;
    margin-top: 8px;
}
.soc-bar-fill {
    height: 100%;
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 10px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: #0a0e1a;
    font-weight: 600;
    transition: width 0.5s ease;
}

/* Badge état */
.status-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    font-weight: 600;
    text-transform: uppercase;
}
.badge-green  { background: #052e16; color: #22c55e; border: 1px solid #166534; }
.badge-orange { background: #2a1300; color: #f97316; border: 1px solid #9a3412; }
.badge-red    { background: #2a0000; color: #ef4444; border: 1px solid #991b1b; }

/* Alerte */
.alert-box {
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 0.82rem;
    margin: 6px 0;
    border-left: 3px solid;
}
.alert-green  { background: #052e16; border-color: #22c55e; color: #86efac; }
.alert-orange { background: #2a1300; border-color: #f97316; color: #fdba74; }
.alert-red    { background: #2a0000; border-color: #ef4444; color: #fca5a5; }

/* Séparateur */
.section-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.25em;
    color: #2e4a7a;
    text-transform: uppercase;
    border-bottom: 1px solid #1e2d50;
    padding-bottom: 6px;
    margin: 1.2rem 0 0.8rem;
}

/* Streamlit overrides */
div[data-testid="stMetric"] { display: none; }
.stButton > button {
    background: #0d1730;
    border: 1px solid #1e3060;
    color: #7eb8f7;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    border-radius: 6px;
    padding: 6px 16px;
}
.stButton > button:hover {
    background: #1e3060;
    border-color: #7eb8f7;
    color: #e0e8ff;
}
</style>
""", unsafe_allow_html=True)

# ── Initialisation session ────────────────────────────────────────────────────
if "historique" not in st.session_state:
    st.session_state.historique = pd.DataFrame(columns=["temps", "tension", "courant", "soc", "temperature"])
if "actif" not in st.session_state:
    st.session_state.actif = True

# ── Simulation données (remplacer par ADS1115 plus tard) ─────────────────────
def lire_donnees_simulees():
    tension = round(random.uniform(11.5, 14.4), 3)
    courant = round(random.uniform(-5.0, 8.0), 3)
    temperature = round(random.uniform(22.0, 45.0), 1)
    # SOC estimé depuis tension (batterie plomb-acide 12V)
    soc = round(max(0, min(100, (tension - 10.5) / (14.4 - 10.5) * 100)), 1)
    return tension, courant, temperature, soc

def etat_batterie(soc):
    if soc >= 80:
        return "OPTIMAL", "green"
    elif soc >= 40:
        return "NORMAL", "green"
    elif soc >= 20:
        return "ATTENTION", "orange"
    else:
        return "CRITIQUE", "red"

def etat_temperature(temp):
    if temp < 35:
        return "green"
    elif temp < 42:
        return "orange"
    else:
        return "red"

def etat_courant(courant):
    if courant > 0:
        return "CHARGE", "green"
    elif courant > -2:
        return "VEILLE", "orange"
    else:
        return "DÉCHARGE", "red"

def recommandations(soc, tension, temperature, courant):
    recs = []
    if soc < 20:
        recs.append(("red", "⚠ SOC critique — réduire immédiatement la consommation nocturne"))
    if soc > 95:
        recs.append(("orange", "↑ Batterie quasi pleine — risque de surcharge"))
    if temperature > 42:
        recs.append(("red", "🌡 Température élevée — améliorer la ventilation"))
    elif temperature > 35:
        recs.append(("orange", "🌡 Température en hausse — surveiller le refroidissement"))
    if tension < 11.8:
        recs.append(("red", "⚡ Tension basse — vérifier le câblage et le régulateur"))
    if courant < -4:
        recs.append(("orange", "↓ Décharge rapide — vérifier la consommation des appareils"))
    if not recs:
        recs.append(("green", "✓ Système opérationnel — aucune anomalie détectée"))
    return recs

# ── En-tête ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="title-block">
    <h1>⚡ PLBD — SUPERVISION BATTERIE</h1>
    <p>SYSTÈME PHOTOVOLTAÏQUE AUTONOME · TEMPS RÉEL</p>
</div>
""", unsafe_allow_html=True)

# ── Contrôles ─────────────────────────────────────────────────────────────────
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1, 1, 4])
with col_ctrl1:
    if st.button("▶ START" if not st.session_state.actif else "⏸ PAUSE"):
        st.session_state.actif = not st.session_state.actif
with col_ctrl2:
    if st.button("🗑 RESET"):
        st.session_state.historique = pd.DataFrame(columns=["temps", "tension", "courant", "soc", "temperature"])

# ── Lecture données ───────────────────────────────────────────────────────────
tension, courant, temperature, soc = lire_donnees_simulees()
etat_label, etat_couleur = etat_batterie(soc)
courant_label, courant_couleur = etat_courant(courant)
temp_couleur = etat_temperature(temperature)

# Ajout à l'historique
if st.session_state.actif:
    nouvelle_ligne = pd.DataFrame([{
        "temps": datetime.now().strftime("%H:%M:%S"),
        "tension": tension,
        "courant": courant,
        "soc": soc,
        "temperature": temperature
    }])
    st.session_state.historique = pd.concat(
        [st.session_state.historique, nouvelle_ligne], ignore_index=True
    ).tail(60)

# ── Métriques principales ─────────────────────────────────────────────────────
st.markdown('<div class="section-title">PARAMÈTRES EN TEMPS RÉEL</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    soc_color = "green" if soc >= 40 else ("orange" if soc >= 20 else "red")
    st.markdown(f"""
    <div class="metric-card {soc_color}">
        <div class="metric-label">ÉTAT DE CHARGE (SOC)</div>
        <div class="metric-value">{soc}<span class="metric-unit">%</span></div>
        <div class="soc-bar-bg">
            <div class="soc-bar-fill" style="width:{soc}%; background:{'#22c55e' if soc>=40 else ('#f97316' if soc>=20 else '#ef4444')}">
                {soc}%
            </div>
        </div>
        <div class="metric-sub" style="margin-top:8px">
            <span class="status-badge badge-{etat_couleur}">{etat_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    v_color = "green" if tension >= 12.4 else ("orange" if tension >= 11.8 else "red")
    st.markdown(f"""
    <div class="metric-card {v_color}">
        <div class="metric-label">TENSION BATTERIE</div>
        <div class="metric-value">{tension}<span class="metric-unit">V</span></div>
        <div class="metric-sub">Nominale : 12 V · Max : 14.4 V</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card {courant_couleur}">
        <div class="metric-label">COURANT</div>
        <div class="metric-value">{abs(courant)}<span class="metric-unit">A</span></div>
        <div class="metric-sub">
            <span class="status-badge badge-{courant_couleur}">{courant_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card {temp_couleur}">
        <div class="metric-label">TEMPÉRATURE</div>
        <div class="metric-value">{temperature}<span class="metric-unit">°C</span></div>
        <div class="metric-sub">Limite : 45 °C</div>
    </div>
    """, unsafe_allow_html=True)

# ── Graphiques ────────────────────────────────────────────────────────────────
if len(st.session_state.historique) > 1:
    st.markdown('<div class="section-title">HISTORIQUE SESSION</div>', unsafe_allow_html=True)
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("**SOC Batterie (%)**")
        st.line_chart(
            st.session_state.historique.set_index("temps")["soc"],
            color="#22c55e"
        )
    with col_g2:
        st.markdown("**Tension (V)**")
        st.line_chart(
            st.session_state.historique.set_index("temps")["tension"],
            color="#7eb8f7"
        )

# ── Recommandations ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">DIAGNOSTIC &amp; RECOMMANDATIONS</div>', unsafe_allow_html=True)
for couleur, message in recommandations(soc, tension, temperature, courant):
    st.markdown(f'<div class="alert-box alert-{couleur}">{message}</div>', unsafe_allow_html=True)

# ── Horodatage ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:right; font-family:'Share Tech Mono',monospace; font-size:0.65rem;
color:#2e4a7a; margin-top:1.5rem; border-top:1px solid #1e2d50; padding-top:8px;">
DERNIÈRE MISE À JOUR : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} · MODE SIMULATION
</div>
""", unsafe_allow_html=True)

# ── Rafraîchissement automatique ──────────────────────────────────────────────
if st.session_state.actif:
    time.sleep(2)
    st.rerun()