"""
dashboard_c02.py — Dashboard Veille Réglementaire C02
MaroTrade Intelligence · Version LLM (Claude 3.5 Haiku)
Lancer avec : streamlit run dashboard_c02.py
"""

import os
import streamlit as st
import pandas as pd
from datetime import datetime
from services.watch import RegulatoryWatchEngine, LEVEL_CRITICAL, LEVEL_WARNING, LEVEL_INFO
from services.nlp import NLPAnalyzer

st.set_page_config(
    page_title="Veille Réglementaire — MaroTrade",
    page_icon="📡",
    layout="wide",
)

st.markdown("""
<style>
.alert-critical { background:#FCEBEB; border-left:4px solid #E24B4A; padding:12px 16px; border-radius:0 8px 8px 0; margin-bottom:10px; }
.alert-warning  { background:#FAEEDA; border-left:4px solid #BA7517; padding:12px 16px; border-radius:0 8px 8px 0; margin-bottom:10px; }
.alert-info     { background:#E1F5EE; border-left:4px solid #1D9E75; padding:12px 16px; border-radius:0 8px 8px 0; margin-bottom:10px; }
.alert-title    { font-size:14px; font-weight:600; margin-bottom:4px; }
.alert-meta     { font-size:12px; color:#888; margin-bottom:6px; }
.alert-text     { font-size:13px; line-height:1.5; }
.action-box     { background:rgba(0,0,0,0.04); border-radius:6px; padding:8px 12px; font-size:12px; margin-top:8px; }
.llm-badge      { display:inline-block; font-size:10px; padding:1px 6px; border-radius:4px; background:#EEEDFE; color:#3C3489; font-weight:500; margin-left:6px; }
@media (prefers-color-scheme: dark) {
  .alert-critical { background:#501313; }
  .alert-warning  { background:#412402; }
  .alert-info     { background:#04342C; }
  .alert-meta  { color:#aaa; }
  .action-box  { background:rgba(255,255,255,0.08); }
  .llm-badge   { background:#26215C; color:#CECBF6; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.title("📡 Veille Réglementaire")
    st.caption("Module C02 · MaroTrade Intelligence")
    st.divider()

    HS_CATALOGUE = {
        "🫒 Huile d'argan (151590)":        "151590",
        "🐟 Sardines en conserve (160413)": "160413",
        "🌴 Dattes fraîches (080410)":      "080410",
        "🌺 Safran (09102010)":             "09102010",
        "🌿 Cumin (090920)":                "090920",
        "🪆 Tapis berbère (570110)":        "570110",
        "🏺 Zellige (691010)":              "691010",
        "📦 Autre produit":                 "custom",
    }

    product_name = st.text_input("Votre produit", value="Huile d'argan bio")
    selected = st.selectbox("Catégorie HS", list(HS_CATALOGUE.keys()))
    hs_code = HS_CATALOGUE[selected]
    if hs_code == "custom":
        hs_code = st.text_input("Code HS (6 chiffres)", "151590")

    st.divider()
    st.caption("Marchés à surveiller")
    PAYS_OPTIONS = {
        "France":          "FRA", "États-Unis":      "USA",
        "Allemagne":       "DEU", "Japon":           "JPN",
        "Canada":          "CAN", "Arabie Saoudite": "SAU",
        "Émirats Arabes":  "ARE", "Espagne":         "ESP",
        "Royaume-Uni":     "GBR", "Qatar":           "QAT",
    }
    selected_pays = st.multiselect(
        "Pays cibles",
        list(PAYS_OPTIONS.keys()),
        default=["France", "États-Unis", "Arabie Saoudite"],
    )
    target_countries = [PAYS_OPTIONS[p] for p in selected_pays]

    st.divider()

    # ── Option IA locale ───────────────────────────────────────
    st.caption("Intelligence artificielle locale")
    use_llm = st.checkbox(
        "Activer l'analyse IA locale",
        value=True,
        help="Utilise le service NLP open-source pour enrichir les alertes sans API externe.",
    )

    st.divider()
    niveau_filter = st.multiselect(
        "Filtrer par niveau",
        [LEVEL_CRITICAL, LEVEL_WARNING, LEVEL_INFO],
        default=[LEVEL_CRITICAL, LEVEL_WARNING, LEVEL_INFO],
    )

    run_btn = st.button("🔍 Lancer la veille", type="primary", use_container_width=True)


# ─────────────────────────────────────────
# PAGE PRINCIPALE
# ─────────────────────────────────────────
st.title("📡 Veille Réglementaire Export")
st.caption(f"Surveillance réglementaire intelligente · {datetime.now().strftime('%d/%m/%Y')}")

if not run_btn:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sources surveillées", "4", help="EUR-Lex · RASFF · WTO · FDA")
    col2.metric("Réglementations indexées", "8+")
    col3.metric("Pays couverts", "20+")
    col4.metric(
        "Mode IA",
        "Claude 3.5 Haiku" if use_llm else "Basique",
        delta="Actif" if use_llm else None,
    )
    st.info("👈 Configurez votre produit et vos marchés, puis lancez la veille.")
    st.stop()


# ─────────────────────────────────────────
# ANALYSE
# ─────────────────────────────────────────
with st.spinner("Collecte des sources réglementaires..."):
    engine = RegulatoryWatchEngine()
    alerts = engine.run(hs_code, product_name, target_countries)

# Enrichissement IA locale si activé
brief_text = None
if use_llm:
    with st.spinner("Analyse IA locale en cours..."):
        analyzer = NLPAnalyzer(use_models=False)
        enriched_alerts = []
        for alert in alerts:
            source_text = alert.get("resume") or alert.get("titre") or ""
            analysis = analyzer.analyze(source_text, hs_code, target_countries)
            alert = {
                **alert,
                "titre": f"{analysis.titre} — {alert.get('titre', '')}" if alert.get('titre') else analysis.titre,
                "resume": analysis.resume,
                "action": analysis.action_requise,
                "score_impact": analysis.impact_score,
                "llm_enhanced": True,
                "llm_analysis": analysis,
            }
            enriched_alerts.append(alert)
        alerts = enriched_alerts
        brief_text = "Analyse IA locale appliquée aux alertes réglementaires."

# Filtrer par niveau
engine_obj = engine
summary_data = engine_obj.get_summary(alerts)
alerts = [a for a in alerts if a.get("niveau") in niveau_filter]


# ─────────────────────────────────────────
# MÉTRIQUES
# ─────────────────────────────────────────
st.divider()
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total alertes", summary_data["total"])
col2.metric("🔴 Critiques", summary_data["critique"],
            delta="Urgent" if summary_data["critique"] > 0 else None,
            delta_color="inverse")
col3.metric("🟡 Attention", summary_data["attention"])
col4.metric("🟢 Infos", summary_data["info"])
if llm_stats:
    col5.metric("🤖 Tokens LLM", f"{llm_stats['tokens_totaux']:,}",
                help=f"Coût estimé : ${llm_stats['cout_estime_usd']:.4f} USD")

# Brief exécutif LLM
if brief_text:
    st.divider()
    st.subheader("🤖 Brief exécutif — Claude 3.5 Haiku")
    st.info(brief_text)

st.divider()


# ─────────────────────────────────────────
# AFFICHAGE DES ALERTES
# ─────────────────────────────────────────
def render_alert(alert: dict):
    niveau = alert.get("niveau", LEVEL_INFO)
    css_class = {
        LEVEL_CRITICAL: "alert-critical",
        LEVEL_WARNING:  "alert-warning",
        LEVEL_INFO:     "alert-info",
    }.get(niveau, "alert-info")

    icon  = {LEVEL_CRITICAL: "🔴", LEVEL_WARNING: "🟡", LEVEL_INFO: "🟢"}.get(niveau, "⚪")
    llm_enhanced = alert.get("llm_enhanced", False)
    llm_badge = '<span class="llm-badge">Claude 3.5 Haiku</span>' if llm_enhanced else ""

    titre   = alert.get("titre", "")[:120]
    source  = alert.get("source", "")
    date    = str(alert.get("date", ""))[:10]
    score   = alert.get("score_impact", alert.get("relevance", 0))
    resume  = alert.get("resume", "")[:300]
    action  = alert.get("action", "")
    url     = alert.get("url", "")
    delai   = alert.get("delai_jours")
    delai_str = f" · ⏱ {delai} jours" if delai else ""

    # Afficher confiance si LLM
    llm_a = alert.get("llm_analysis")
    confiance_str = ""
    if llm_a and hasattr(llm_a, "confiance"):
        confiance_str = f" · Confiance {llm_a.confiance:.0%}"

    action_html = f'<div class="action-box">✅ {action}</div>' if action else ""
    url_html    = f'<a href="{url}" target="_blank" style="font-size:11px;color:#378ADD">→ Source officielle</a>' if url else ""

    st.markdown(
        f'<div class="{css_class}">'
        f'<div class="alert-title">{icon} {titre}{llm_badge}</div>'
        f'<div class="alert-meta">{source} · {date} · Impact {score:.0f}/100{delai_str}{confiance_str}</div>'
        f'<div class="alert-text">{resume}</div>'
        f'{action_html}'
        f'<div style="margin-top:6px">{url_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


critiques  = [a for a in alerts if a.get("niveau") == LEVEL_CRITICAL]
attentions = [a for a in alerts if a.get("niveau") == LEVEL_WARNING]
infos      = [a for a in alerts if a.get("niveau") == LEVEL_INFO]

if not alerts:
    st.success("✅ Aucune alerte pour ce produit sur ces marchés.")
else:
    if critiques:
        st.subheader("🔴 Critiques — Action urgente")
        for a in critiques:
            render_alert(a)

    if attentions:
        st.subheader("🟡 Attention — À surveiller")
        for a in attentions:
            render_alert(a)

    if infos:
        with st.expander(f"🟢 Informations ({len(infos)})"):
            for a in infos:
                render_alert(a)


# ─────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────
st.divider()
st.subheader("Export")

rows = []
for a in alerts:
    row = {
        "Niveau":  a.get("niveau", ""),
        "Titre":   a.get("titre", ""),
        "Source":  a.get("source", ""),
        "Date":    str(a.get("date", ""))[:10],
        "Impact":  a.get("score_impact", 0),
        "Action":  a.get("action", ""),
        "LLM":     "Oui" if a.get("llm_enhanced") else "Non",
    }
    rows.append(row)

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True, hide_index=True)
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Télécharger CSV",
    data=csv,
    file_name=f"veille_{product_name.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
)