"""
dashboard.py — Dashboard C03 · Moteur de Scoring des Marchés d'Export
MaroTrade Intelligence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Lancer avec : streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scoring_engine import MarketScoringEngine, WEIGHTS_DEFAULT as WEIGHTS

# ═══════════════════════════════════════════════════════════════
# CONFIG PAGE
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="MaroTrade Intelligence — Scoring Export",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.score-big  { font-size:2.8rem; font-weight:700; line-height:1; }
.score-sub  { font-size:0.85rem; color:#888; margin-top:2px; }
.atout  { background:#e8f5e9; color:#1b5e20; padding:6px 12px; border-radius:6px; font-size:0.85rem; margin-bottom:5px; }
.risque { background:#fff3e0; color:#e65100; padding:6px 12px; border-radius:6px; font-size:0.85rem; margin-bottom:5px; }
.brand  { font-size:0.75rem; color:#1D9E75; font-weight:600; letter-spacing:.1em; text-transform:uppercase; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# CATALOGUE PRODUITS MAROCAINS
# Code HS → données disponibles dans data_sources.py
# ═══════════════════════════════════════════════════════════════

HS_CATALOGUE = {
    "🫒 Huile d'argan (151590)":           "151590",
    "🐟 Sardines en conserve (160413)":    "160413",
    "🌴 Dattes fraîches (080410)":         "080410",
    "🌺 Safran (09102010)":                "09102010",
    "📦 Autre produit — code HS manuel":   "custom",
}

DIMENSIONS = [
    "Potentiel de marché",
    "Accord commercial",
    "Facilité des affaires",
    "Stabilité & risque pays",
    "Diaspora marocaine (MRE)",
    "Logistique & transport",
]

COLORS = ["#1D9E75", "#378ADD", "#BA7517", "#534AB7", "#D85A30", "#D4537E"]


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown('<div class="brand">MaroTrade Intelligence</div>', unsafe_allow_html=True)
    st.title("Scoring Export")
    st.caption("Module C03 · Marchés prioritaires")
    st.divider()

    # ── Produit ──────────────────────────────────────────────
    st.caption("Votre produit")
    product_name = st.text_input("Nom commercial", value="Huile d'argan bio",
                                  placeholder="Ex: Safran premium, Sardines AOC...")

    selected_cat = st.selectbox("Catégorie HS douanier", list(HS_CATALOGUE.keys()))
    hs_code = HS_CATALOGUE[selected_cat]
    if hs_code == "custom":
        hs_code = st.text_input("Code HS (6 chiffres)", "151590",
                                 help="Trouvez votre code HS sur douane.gov.ma")

    top_n = st.slider("Nombre de marchés à analyser", min_value=3, max_value=10, value=5)

    st.divider()

    # ── Poids personnalisables ────────────────────────────────
    st.caption("Personnaliser les poids")
    with st.expander("Ajuster les dimensions", expanded=False):
        w_marche    = st.slider("Potentiel de marché",    0, 50, 28)
        w_accord    = st.slider("Accord commercial",      0, 50, 22)
        w_business  = st.slider("Facilité des affaires",  0, 40, 18)
        w_stabilite = st.slider("Stabilité & risque",     0, 30, 12)
        w_diaspora  = st.slider("Diaspora MRE",           0, 30, 10)
        w_logist    = st.slider("Logistique",             0, 30, 10)
    if "w_marche" not in dir():
        w_marche, w_accord, w_business = 28, 22, 18
        w_stabilite, w_diaspora, w_logist = 12, 10, 10

    st.divider()
    run_btn = st.button("Lancer l'analyse", type="primary", width='stretch')


# ═══════════════════════════════════════════════════════════════
# FONCTIONS GRAPHIQUES
# ═══════════════════════════════════════════════════════════════

def radar_chart(results: list) -> go.Figure:
    fig = go.Figure()
    cats = DIMENSIONS + [DIMENSIONS[0]]
    for i, r in enumerate(results[:5]):
        vals = [d.score for d in r.dimensions] + [r.dimensions[0].score]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=cats, fill="toself", opacity=0.2,
            name=r.country_name,
            line=dict(color=COLORS[i % len(COLORS)], width=2),
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True, height=400,
        margin=dict(l=30, r=30, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(size=11)),
    )
    return fig

def bar_scores(results: list) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=[r.score_final  for r in results],
        y=[r.country_name for r in results],
        orientation="h",
        marker_color=COLORS[:len(results)],
        text=[f"{r.score_final:.1f}" for r in results],
        textposition="outside",
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 115], title="Score /100"),
        yaxis=dict(autorange="reversed"),
        height=280,
        margin=dict(l=10, r=50, t=10, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig

def heatmap_dims(results: list) -> go.Figure:
    countries = [r.country_name for r in results]
    matrix    = [[d.score for d in r.dimensions] for r in results]
    df_h = pd.DataFrame(matrix, index=countries, columns=DIMENSIONS)
    fig = px.imshow(
        df_h, color_continuous_scale="RdYlGn",
        zmin=0, zmax=100, text_auto=".0f", aspect="auto", height=240,
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        xaxis=dict(tickfont=dict(size=10)),
    )
    return fig

def shap_chart(shap_dict: dict, country: str) -> go.Figure:
    items  = list(shap_dict.items())[:10]
    labels = [i[0] for i in items]
    values = [i[1] for i in items]
    colors = ["#1D9E75" if v > 0 else "#E24B4A" for v in values]
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker_color=colors,
        text=[f"{v:+.2f}" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        title=dict(text=f"Contribution SHAP — {country}", font=dict(size=13)),
        xaxis_title="Impact sur le score",
        height=360,
        margin=dict(l=10, r=70, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange="reversed"),
    )
    return fig

def score_color(s: float) -> str:
    return "#1D9E75" if s >= 70 else "#BA7517" if s >= 50 else "#E24B4A"


# ═══════════════════════════════════════════════════════════════
# PAGE PRINCIPALE — ÉTAT INITIAL
# ═══════════════════════════════════════════════════════════════

st.markdown('<div class="brand">MaroTrade Intelligence</div>', unsafe_allow_html=True)
st.title("Marchés prioritaires à l'export")
st.caption("Scoring pondéré × XGBoost × SHAP — 6 dimensions · 15 indicateurs · 20+ pays")

if not run_btn:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Dimensions", "6", help="Marché · Accord · Business · Stabilité · Diaspora · Logistique")
    col2.metric("Indicateurs", "15", help="UN Comtrade · World Bank WGI · OCDE · MRE · LPI")
    col3.metric("Modèles", "2", help="Scoring pondéré (60%) + XGBoost (40%)")
    col4.metric("Pays couverts", "20+")

    st.divider()
    st.info("Configurez votre produit dans la barre latérale et cliquez sur **Lancer l'analyse**.")

    st.subheader("Produits marocains disponibles")
    cols = st.columns(4)
    exemples = [
        ("Huile d'argan bio", "151590", "#1 France · #2 USA · #3 Japon"),
        ("Sardines en conserve", "160413", "#1 Espagne · #2 France · #3 Italie"),
        ("Dattes fraîches", "080410", "#1 France · #2 Allemagne · #3 USA"),
        ("Safran marocain", "09102010", "#1 France · #2 Espagne · #3 Émirats"),
    ]
    for col, (prod, hs, top) in zip(cols, exemples):
        with col:
            st.markdown(f"**{prod}**")
            st.caption(f"HS {hs}")
            st.caption(top)
    st.stop()


# ═══════════════════════════════════════════════════════════════
# LANCEMENT ANALYSE
# ═══════════════════════════════════════════════════════════════

with st.spinner(f"Analyse de {product_name} (HS {hs_code}) — XGBoost + SHAP en cours..."):
    # Appliquer poids personnalisés
    total = w_marche + w_accord + w_business + w_stabilite + w_diaspora + w_logist
    if total > 0:
        WEIGHTS["marche"]     = w_marche    / total
        WEIGHTS["accord"]     = w_accord    / total
        WEIGHTS["business"]   = w_business  / total
        WEIGHTS["stabilite"]  = w_stabilite / total
        WEIGHTS["diaspora"]   = w_diaspora  / total
        WEIGHTS["logistique"] = w_logist    / total

    engine  = MarketScoringEngine()
    results = engine.run(product_name, hs_code, top_n)

st.success(f"{len(results)} marchés analysés pour **{product_name}** · HS {hs_code}")
st.divider()


# ═══════════════════════════════════════════════════════════════
# SECTION 1 — SCORES RÉSUMÉ
# ═══════════════════════════════════════════════════════════════

st.subheader("Classement des marchés")

cols = st.columns(min(len(results), 5))
for i, r in enumerate(results[:5]):
    with cols[i]:
        c = score_color(r.score_final)
        st.markdown(
            f"<div style='text-align:center;padding:8px 0'>"
            f"<div style='font-size:.9rem;color:#888'>#{r.rank}</div>"
            f"<div style='font-size:1.1rem;font-weight:600;margin:4px 0'>{r.country_name}</div>"
            f"<div class='score-big' style='color:{c}'>{r.score_final:.0f}</div>"
            f"<div class='score-sub'>/ 100</div>"
            f"<div style='font-size:.75rem;color:#aaa;margin-top:4px'>"
            f"W:{r.score_weighted:.0f} · XGB:{r.score_xgboost:.0f}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.divider()


# ═══════════════════════════════════════════════════════════════
# SECTION 2 — GRAPHIQUES COMPARATIFS
# ═══════════════════════════════════════════════════════════════

st.subheader("Analyse comparative")

col_r, col_b = st.columns([3, 2])
with col_r:
    st.caption("Radar — profil par dimension")
    st.plotly_chart(radar_chart(results), width='stretch', key="chart_radar")
with col_b:
    st.caption("Scores finaux")
    st.plotly_chart(bar_scores(results), width='stretch', key="chart_bar")
    st.caption("Heatmap dimensions")
    st.plotly_chart(heatmap_dims(results), width='stretch', key="chart_heatmap")

st.divider()


# ═══════════════════════════════════════════════════════════════
# SECTION 3 — FICHES DÉTAILLÉES
# ═══════════════════════════════════════════════════════════════

st.subheader("Fiches détaillées par marché")
tabs = st.tabs([f"#{r.rank}  {r.country_name}" for r in results])

for tab, r in zip(tabs, results):
    with tab:
        col_l, col_r = st.columns(2)

        # ── Colonne gauche : scores par dimension ─────────────
        with col_l:
            c = score_color(r.score_final)
            st.markdown(
                f"<div style='display:flex;align-items:baseline;gap:10px;margin-bottom:16px'>"
                f"<span class='score-big' style='color:{c}'>{r.score_final:.1f}</span>"
                f"<span style='color:#888'>/100</span>"
                f"<span style='font-size:.8rem;color:#aaa;margin-left:6px'>"
                f"Pondéré {r.score_weighted:.1f} · XGBoost {r.score_xgboost:.1f}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

            for d in r.dimensions:
                pct = int(d.score)
                bc  = score_color(d.score)
                st.markdown(f"**{d.nom}** — {pct}/100")
                st.progress(pct / 100)
                with st.expander(f"Voir le détail"):
                    for k, v in d.detail.items():
                        st.markdown(f"- **{k}** : {v}")
                    st.caption(d.interpretation)

        # ── Colonne droite : atouts, risques, info ────────────
        with col_r:
            if r.top_atouts:
                st.markdown("**Atouts**")
                for a in r.top_atouts:
                    st.markdown(f'<div class="atout">✓ {a}</div>', unsafe_allow_html=True)

            if r.top_risques:
                st.markdown("**Points de vigilance**")
                for ri in r.top_risques:
                    st.markdown(f'<div class="risque">⚠ {ri}</div>', unsafe_allow_html=True)

            st.divider()

            acc = r.accord_info
            log = r.logistique_info

            st.markdown("**Accord commercial Maroc**")
            if acc["droits"] == 0:
                st.success(f"{acc['accord']} — Droits 0%")
            else:
                st.warning(f"{acc['accord']} — Droits {acc['droits']}%")

            st.markdown("**Logistique depuis Casablanca**")
            lc1, lc2, lc3 = st.columns(3)
            lc1.metric("Distance", f"{log['distance_km']:,} km")
            lc2.metric("LPI", f"{log['lpi']}/5")
            lc3.metric("Conteneur", f"{log['cout_conteneur_usd']:,} $")

            if log.get("risk_label"):
                st.markdown("**Risque pays (OCDE)**")
                rcat = log.get("risk_category", 4)
                if rcat <= 1:
                    st.success(f"Catégorie {rcat} — {log['risk_label']}")
                elif rcat <= 3:
                    st.info(f"Catégorie {rcat} — {log['risk_label']}")
                else:
                    st.warning(f"Catégorie {rcat} — {log['risk_label']}")

        # ── SHAP waterfall ────────────────────────────────────
        st.plotly_chart(shap_chart(r.shap_values, r.country_name), width='stretch', key=f"shap_{r.country_code}")


# ═══════════════════════════════════════════════════════════════
# SECTION 4 — EXPORT
# ═══════════════════════════════════════════════════════════════

st.divider()
st.subheader("Export des résultats")

rows = []
for r in results:
    row = {
        "Rang":             r.rank,
        "Pays":             r.country_name,
        "Score final /100": r.score_final,
        "Score pondéré":    r.score_weighted,
        "Score XGBoost":    r.score_xgboost,
        "Accord":           r.accord_info["accord"],
        "Droits (%)":       r.accord_info["droits"],
        "Distance (km)":    r.logistique_info["distance_km"],
        "LPI":              r.logistique_info["lpi"],
        "Risque OCDE":      r.logistique_info.get("risk_category", "-"),
    }
    for d in r.dimensions:
        row[f"Score — {d.nom}"] = round(d.score, 1)
    rows.append(row)

df_export = pd.DataFrame(rows)
st.dataframe(df_export, width='stretch', hide_index=True)

col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    csv = df_export.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Télécharger CSV",
        data=csv,
        file_name=f"marotrade_{product_name.replace(' ', '_')}_{hs_code}.csv",
        mime="text/csv",
        width='stretch',
    )
with col_dl2:
    json_str = df_export.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8")
    st.download_button(
        "Télécharger JSON",
        data=json_str,
        file_name=f"marotrade_{product_name.replace(' ', '_')}_{hs_code}.json",
        mime="application/json",
        width='stretch',
    )

st.caption("MaroTrade Intelligence · Module C03 · Hackathon Facilitation du Commerce 2026")