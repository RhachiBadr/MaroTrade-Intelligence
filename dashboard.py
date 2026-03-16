"""
dashboard.py — Dashboard C03 Moteur de Scoring Avancé
Lancer avec : streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scoring_engine import MarketScoringEngine, MarketResult

# ═══════════════════════════════════════════════════════════════
# CONFIG PAGE
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Moteur de Scoring Export — Maroc",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.score-big { font-size: 2.8rem; font-weight: 700; line-height: 1; }
.score-label { font-size: 0.85rem; color: #888; margin-top: 2px; }
.dim-row { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.atout { background: #e8f5e9; color: #1b5e20; padding: 5px 10px; border-radius: 6px; font-size: 0.85rem; margin-bottom: 5px; }
.risque { background: #fff3e0; color: #e65100; padding: 5px 10px; border-radius: 6px; font-size: 0.85rem; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# SIDEBAR — PARAMÈTRES
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.title("🌍 Scoring Export")
    st.caption("Moteur C03 · Plateforme Commerce Maroc")
    st.divider()

    # Catalogue produits
    HS_CATALOGUE = {
        "🫒 Huile d'argan (151590)":        "151590",
        "🐟 Sardines en conserve (160413)": "160413",
        "🌴 Dattes fraîches (080410)":      "080410",
        "📦 Autre produit":                 "custom",
    }

    product_name = st.text_input("Nom du produit", value="Huile d'argan bio")
    selected_cat = st.selectbox("Catégorie HS", list(HS_CATALOGUE.keys()))
    hs_code = HS_CATALOGUE[selected_cat]
    if hs_code == "custom":
        hs_code = st.text_input("Code HS (6 chiffres)", "151590")

    top_n = st.slider("Nombre de marchés à analyser", 3, 10, 5)

    st.divider()
    st.caption("Poids des dimensions")
    w_marche    = st.slider("Potentiel de marché",     0, 50, 28)
    w_accord    = st.slider("Accord commercial",       0, 50, 22)
    w_business  = st.slider("Facilité des affaires",   0, 40, 18)
    w_stabilite = st.slider("Stabilité & risque",      0, 30, 12)
    w_diaspora  = st.slider("Diaspora MRE",            0, 30, 10)
    w_logist    = st.slider("Logistique",              0, 30, 10)

    run_btn = st.button("🔍 Lancer l'analyse", type="primary", use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# HELPERS GRAPHIQUES
# ═══════════════════════════════════════════════════════════════

DIMENSIONS = [
    "Potentiel de marché",
    "Accord commercial",
    "Facilité des affaires",
    "Stabilité & risque pays",
    "Diaspora marocaine (MRE)",
    "Logistique & transport",
]

COLORS = ["#1D9E75", "#378ADD", "#BA7517", "#534AB7", "#D85A30", "#D4537E"]

def radar_chart(results: list) -> go.Figure:
    """Radar chart comparant les top marchés sur 6 dimensions."""
    fig = go.Figure()
    cats = DIMENSIONS + [DIMENSIONS[0]]

    for i, r in enumerate(results[:5]):
        vals = [d.score for d in r.dimensions] + [r.dimensions[0].score]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=cats,
            fill="toself", opacity=0.25,
            name=r.country_name,
            line=dict(color=COLORS[i % len(COLORS)], width=2),
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        height=420,
        margin=dict(l=40, r=40, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
    )
    return fig


def bar_scores(results: list) -> go.Figure:
    """Bar chart des scores finaux."""
    countries = [r.country_name for r in results]
    scores    = [r.score_final  for r in results]
    colors    = COLORS[:len(results)]

    fig = go.Figure(go.Bar(
        x=scores, y=countries,
        orientation="h",
        marker_color=colors,
        text=[f"{s:.1f}" for s in scores],
        textposition="outside",
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 115], title="Score /100"),
        yaxis=dict(autorange="reversed"),
        height=300,
        margin=dict(l=10, r=60, t=10, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def shap_waterfall(shap_dict: dict, country: str) -> go.Figure:
    """Waterfall SHAP — contribution de chaque feature au score."""
    items = list(shap_dict.items())[:12]
    labels = [i[0] for i in items]
    values = [i[1] for i in items]
    colors = ["#1D9E75" if v > 0 else "#E24B4A" for v in values]

    fig = go.Figure(go.Bar(
        x=values, y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{v:+.2f}" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        title=f"Contribution SHAP — {country}",
        xaxis_title="Impact sur le score",
        height=400,
        margin=dict(l=10, r=80, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange="reversed"),
    )
    return fig


def dimension_heatmap(results: list) -> go.Figure:
    """Heatmap des scores par dimension et par pays."""
    countries = [r.country_name for r in results]
    matrix = [[d.score for d in r.dimensions] for r in results]
    df_heat = pd.DataFrame(matrix, index=countries, columns=DIMENSIONS)

    fig = px.imshow(
        df_heat,
        color_continuous_scale="RdYlGn",
        zmin=0, zmax=100,
        text_auto=".0f",
        aspect="auto",
        height=280,
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
    )
    return fig


# ═══════════════════════════════════════════════════════════════
# CONTENU PRINCIPAL
# ═══════════════════════════════════════════════════════════════

st.title("🌍 Moteur de Scoring des Marchés d'Export")
st.caption(f"Scoring pondéré × XGBoost × SHAP — 6 dimensions, 15 indicateurs")

if not run_btn:
    st.info("👈 Configurez votre produit dans la barre latérale et lancez l'analyse.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Dimensions analysées", "6")
        st.caption("Marché · Accord · Business · Stabilité · Diaspora · Logistique")
    with col2:
        st.metric("Indicateurs intégrés", "15")
        st.caption("UN Comtrade · World Bank · ADII · MRE · LPI")
    with col3:
        st.metric("Modèles combinés", "2")
        st.caption("Scoring pondéré (60%) + XGBoost (40%)")
    st.stop()


# ═══════════════════════════════════════════════════════════════
# LANCEMENT DE L'ANALYSE
# ═══════════════════════════════════════════════════════════════

with st.spinner("Analyse en cours — chargement des données, entraînement XGBoost, calcul SHAP..."):
    # Appliquer les poids personnalisés
    from scoring_engine import WEIGHTS
    total = w_marche + w_accord + w_business + w_stabilite + w_diaspora + w_logist
    if total > 0:
        WEIGHTS["marche"]     = w_marche    / total
        WEIGHTS["accord"]     = w_accord    / total
        WEIGHTS["business"]   = w_business  / total
        WEIGHTS["stabilite"]  = w_stabilite / total
        WEIGHTS["diaspora"]   = w_diaspora  / total
        WEIGHTS["logistique"] = w_logist    / total

    engine = MarketScoringEngine()
    results = engine.run(product_name, hs_code, top_n)

st.success(f"✅ {len(results)} marchés analysés pour **{product_name}** (HS {hs_code})")
st.divider()


# ─────────────────────────────────────────
# VUE GLOBALE — métriques + graphiques
# ─────────────────────────────────────────

st.subheader("Vue d'ensemble")

col_metrics = st.columns(min(len(results), 5))
for i, r in enumerate(results[:5]):
    with col_metrics[i]:
        color = "#1D9E75" if r.score_final >= 70 else "#BA7517" if r.score_final >= 50 else "#E24B4A"
        st.markdown(
            f"<div style='text-align:center'>"
            f"<div style='font-size:1rem;color:#888'>#{r.rank}</div>"
            f"<div style='font-size:1.4rem;font-weight:600'>{r.country_name}</div>"
            f"<div class='score-big' style='color:{color}'>{r.score_final:.0f}</div>"
            f"<div class='score-label'>/ 100</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.divider()

col_radar, col_bar = st.columns([3, 2])
with col_radar:
    st.plotly_chart(radar_chart(results), use_container_width=True)
with col_bar:
    st.plotly_chart(bar_scores(results), use_container_width=True)
    st.plotly_chart(dimension_heatmap(results), use_container_width=True)


# ─────────────────────────────────────────
# FICHES DÉTAILLÉES PAR MARCHÉ
# ─────────────────────────────────────────

st.divider()
st.subheader("Fiches détaillées par marché")

tabs = st.tabs([f"#{r.rank} {r.country_name}" for r in results])

for tab, r in zip(tabs, results):
    with tab:
        col_left, col_right = st.columns([1, 1])

        with col_left:
            # Score final
            color = "#1D9E75" if r.score_final >= 70 else "#BA7517" if r.score_final >= 50 else "#E24B4A"
            st.markdown(
                f"<div style='display:flex;align-items:baseline;gap:8px;margin-bottom:16px'>"
                f"<span class='score-big' style='color:{color}'>{r.score_final:.1f}</span>"
                f"<span style='font-size:1.1rem;color:#888'>/ 100</span>"
                f"<span style='font-size:0.85rem;color:#aaa;margin-left:8px'>"
                f"Pondéré: {r.score_weighted:.1f} · XGBoost: {r.score_xgboost:.1f}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # Scores par dimension
            for d in r.dimensions:
                pct = int(d.score)
                bar_color = "#1D9E75" if pct >= 70 else "#BA7517" if pct >= 50 else "#E24B4A"
                st.markdown(f"**{d.nom}** — {pct}/100")
                st.progress(pct / 100)
                with st.expander(f"Détail {d.nom}"):
                    for k, v in d.detail.items():
                        st.markdown(f"- **{k}** : {v}")
                    st.caption(d.interpretation)

        with col_right:
            # Atouts
            st.markdown("**Atouts principaux**")
            for a in r.top_atouts:
                st.markdown(f'<div class="atout">✓ {a}</div>', unsafe_allow_html=True)

            # Risques
            if r.top_risques:
                st.markdown("**Points de vigilance**")
                for ri in r.top_risques:
                    st.markdown(f'<div class="risque">⚠ {ri}</div>', unsafe_allow_html=True)

            st.divider()

            # Accord commercial
            acc = r.accord_info
            st.markdown("**Accord commercial Maroc**")
            st.info(f"{acc['accord']} — Droits: {acc['droits']}%")

            # Logistique
            log = r.logistique_info
            st.markdown("**Logistique depuis Casablanca**")
            st.markdown(
                f"Distance : **{log['distance_km']:,} km** · "
                f"LPI : **{log['lpi']}/5** · "
                f"Coût conteneur : **{log['cout_conteneur_usd']:,} USD**"
            )

        # SHAP waterfall
        st.plotly_chart(shap_waterfall(r.shap_values, r.country_name), use_container_width=True)


# ─────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────

st.divider()
st.subheader("Export des résultats")

export_rows = []
for r in results:
    row = {
        "Rang": r.rank,
        "Pays": r.country_name,
        "Score final /100": r.score_final,
        "Score pondéré": r.score_weighted,
        "Score XGBoost": r.score_xgboost,
        "Accord": r.accord_info["accord"],
        "Droits (%)": r.accord_info["droits"],
    }
    for d in r.dimensions:
        row[f"Score — {d.nom}"] = d.score
    export_rows.append(row)

df_export = pd.DataFrame(export_rows)
st.dataframe(df_export, use_container_width=True)

csv = df_export.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Télécharger CSV",
    data=csv,
    file_name=f"scoring_{product_name.replace(' ', '_')}.csv",
    mime="text/csv",
)
