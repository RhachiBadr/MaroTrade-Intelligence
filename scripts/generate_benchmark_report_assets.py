from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
FIGURES = ROOT / "notebooks" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "figure.dpi": 140,
        "savefig.dpi": 220,
        "font.family": "DejaVu Sans",
        "axes.edgecolor": "#D5DAE3",
        "axes.grid": False,
        "grid.color": "#E8ECF3",
    }
)

COLORS = {
    "blue": "#3758F9",
    "green": "#12A594",
    "orange": "#F59E0B",
    "red": "#EF4444",
    "purple": "#7C3AED",
    "ink": "#111827",
    "muted": "#6B7280",
}


def read_json(name: str) -> dict:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


def metric(d: dict, *names: str, default=np.nan):
    for name in names:
        if name in d:
            return d[name]
    return default


def norm_v4(d: dict) -> pd.DataFrame:
    rows = []
    for model, item in d.get("ranking_metrics", {}).items():
        val = item.get("val", {})
        test = item.get("test", {})
        rows.append(
            {
                "benchmark": "v4",
                "model": model,
                "feature_set": "stable_v4",
                "val_top3": metric(val, "top3_hit_rate"),
                "val_ndcg3": metric(val, "ndcg@3"),
                "test_top3": metric(test, "top3_hit_rate"),
                "test_ndcg3": metric(test, "ndcg@3"),
                "test_regret": metric(test, "mean_regret"),
                "test_rmse": np.nan,
                "test_mae": np.nan,
                "test_spearman": np.nan,
                "test_r2": np.nan,
            }
        )
    opt = d.get("optuna_results")
    if opt:
        val = opt.get("ranking", {}).get("val", {})
        test = opt.get("ranking", {}).get("test", {})
        rows.append(
            {
                "benchmark": "v4",
                "model": f"{opt.get('model', 'Model')}_Optuna",
                "feature_set": "stable_v4",
                "val_top3": metric(val, "top3_hit_rate"),
                "val_ndcg3": metric(val, "ndcg@3"),
                "test_top3": metric(test, "top3_hit_rate"),
                "test_ndcg3": metric(test, "ndcg@3"),
                "test_regret": metric(test, "mean_regret"),
                "test_rmse": opt.get("test_rmse", np.nan),
                "test_mae": np.nan,
                "test_spearman": opt.get("test_spearman", np.nan),
                "test_r2": opt.get("test_r2", np.nan),
            }
        )
    return pd.DataFrame(rows)


def norm_v5(d: dict) -> pd.DataFrame:
    rows = []
    for model, item in d.get("results", {}).items():
        val = item.get("val", {})
        test = item.get("test", {})
        rows.append(
            {
                "benchmark": "v5",
                "model": model,
                "feature_set": "advanced_v5",
                "val_top3": metric(val, "top3_hit_rate"),
                "val_ndcg3": metric(val, "ndcg@3"),
                "test_top3": metric(test, "top3_hit_rate"),
                "test_ndcg3": metric(test, "ndcg@3"),
                "test_regret": metric(test, "mean_regret"),
                "test_rmse": metric(test, "rmse"),
                "test_mae": metric(test, "mae"),
                "test_spearman": metric(test, "spearman"),
                "test_r2": metric(test, "r2"),
            }
        )
    return pd.DataFrame(rows)


def norm_v51(d: dict) -> pd.DataFrame:
    cols = [
        "model",
        "feature_set",
        "business_score",
        "val_top3",
        "val_ndcg3",
        "test_top3",
        "test_ndcg3",
        "test_regret",
        "test_rmse",
        "test_mae",
        "test_spearman",
        "test_r2",
    ]
    return pd.DataFrame(d.get("summary", []))[cols].assign(benchmark="v5.1")


def to_report_numbers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.select_dtypes(include=[float]).columns:
        out[col] = out[col].map(lambda x: "" if pd.isna(x) else f"{x:.3f}")
    return out


def write_markdown(df: pd.DataFrame, path: Path) -> None:
    lines = [
        "| " + " | ".join(df.columns) + " |",
        "| " + " | ".join(["---"] * len(df.columns)) + " |",
    ]
    for row in df.astype(str).values:
        lines.append("| " + " | ".join(row) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_table(df: pd.DataFrame, stem: str, caption: str) -> None:
    shown = to_report_numbers(df)
    shown.to_csv(FIGURES / f"{stem}.csv", index=False, encoding="utf-8")
    write_markdown(shown, FIGURES / f"{stem}.md")
    shown.to_latex(index=False, escape=True, caption=caption, label=f"tab:{stem}").replace(
        "\\toprule", "\\hline"
    ).replace("\\midrule", "\\hline").replace("\\bottomrule", "\\hline")
    (FIGURES / f"{stem}.tex").write_text(
        shown.to_latex(index=False, escape=True, caption=caption, label=f"tab:{stem}"),
        encoding="utf-8",
    )

    fig_w = max(10, min(18, 1.08 * len(shown.columns)))
    fig_h = max(2.2, min(9, 0.45 * len(shown) + 1.4))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis("off")
    table = ax.table(cellText=shown.values, colLabels=shown.columns, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1, 1.35)
    for (row, _), cell in table.get_celld().items():
        cell.set_edgecolor("#D8DEE9")
        if row == 0:
            cell.set_facecolor(COLORS["ink"])
            cell.get_text().set_color("white")
            cell.get_text().set_weight("bold")
        elif row % 2 == 0:
            cell.set_facecolor("#F8FAFC")
    ax.set_title(caption, fontsize=12, pad=16, color=COLORS["ink"])
    fig.tight_layout()
    fig.savefig(FIGURES / f"{stem}.png", bbox_inches="tight")
    plt.close(fig)


def add_bar_labels(ax, values, fmt="{:.2f}") -> None:
    max_value = max([v for v in values if pd.notna(v)] or [1])
    for patch, value in zip(ax.patches, values):
        if pd.isna(value):
            continue
        ax.text(
            patch.get_x() + patch.get_width() / 2,
            patch.get_height() + max_value * 0.015,
            fmt.format(value),
            ha="center",
            va="bottom",
            fontsize=8,
            color=COLORS["ink"],
        )


def main() -> None:
    v4 = read_json("benchmark_phase1_results.json")
    v5 = read_json("benchmark_phase1_v5_results.json")
    v51 = read_json("benchmark_phase1_v5_1_results.json")

    df4 = norm_v4(v4)
    df5 = norm_v5(v5)
    df51 = norm_v51(v51)

    best_v4 = df4.sort_values(["test_top3", "test_ndcg3", "test_regret"], ascending=[False, False, True]).iloc[0]
    best_v5 = df5.sort_values(["val_top3", "val_ndcg3", "test_regret"], ascending=[False, False, True]).iloc[0]
    best_v51 = df51.sort_values(["business_score", "val_top3", "test_regret"], ascending=[False, False, True]).iloc[0]
    final = pd.DataFrame([best_v4, best_v5, best_v51]).reset_index(drop=True)
    final.insert(0, "selection_role", ["Best previous baseline", "Best v5 candidate", "Final selected model"])

    final_cols = [
        "selection_role",
        "benchmark",
        "model",
        "feature_set",
        "val_top3",
        "test_top3",
        "test_ndcg3",
        "test_regret",
        "test_rmse",
        "test_spearman",
    ]
    save_table(final[final_cols], "report_table_ieee_final_comparison", "Final benchmark comparison for market recommendation.")

    v51_cols = [
        "model",
        "feature_set",
        "business_score",
        "val_top3",
        "test_top3",
        "test_ndcg3",
        "test_regret",
        "test_rmse",
        "test_mae",
        "test_spearman",
        "test_r2",
    ]
    save_table(
        df51.sort_values("business_score", ascending=False)[v51_cols].head(12),
        "report_table_v5_1_all_models",
        "Detailed v5.1 model comparison.",
    )

    # Benchmark evolution.
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    x = np.arange(len(final))
    labels = final["benchmark"] + "\n" + final["model"]
    panels = [
        ("test_top3", "Test Top-3 hit rate", COLORS["blue"], "{:.2f}"),
        ("test_ndcg3", "Test NDCG@3", COLORS["green"], "{:.2f}"),
        ("test_regret", "Mean regret", COLORS["orange"], "{:.1f}"),
    ]
    for ax, (col, title, color, fmt) in zip(axes, panels):
        values = final[col].astype(float).values
        ax.bar(x, values, color=color, alpha=0.92, width=0.62)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.grid(axis="y")
        add_bar_labels(ax, values, fmt=fmt)
    fig.suptitle("Benchmark evolution: baseline, v5 and final v5.1", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "report_01_benchmark_evolution.png", bbox_inches="tight")
    plt.close(fig)

    # V5.1 dashboard.
    top = df51.sort_values("business_score", ascending=False).head(8)
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    panels = [
        ("val_top3", "Validation Top-3", COLORS["blue"], False),
        ("test_top3", "Test Top-3", COLORS["green"], False),
        ("test_ndcg3", "Test NDCG@3", COLORS["purple"], False),
        ("test_regret", "Mean regret", COLORS["red"], True),
    ]
    for ax, (col, title, color, asc) in zip(axes.ravel(), panels):
        ordered = top.sort_values(col, ascending=asc)
        names = ordered["model"] + " / " + ordered["feature_set"].str.replace("_", " ")
        ax.barh(names, ordered[col], color=color, alpha=0.9)
        ax.set_title(title)
        ax.grid(axis="x")
        ax.invert_yaxis()
    fig.suptitle("V5.1 business metrics by model", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "report_02_v5_1_metric_dashboard.png", bbox_inches="tight")
    plt.close(fig)

    # Feature strategy ablation.
    grouped = (
        df51.groupby("feature_set")
        .agg(
            best_val_top3=("val_top3", "max"),
            best_test_top3=("test_top3", "max"),
            mean_regret=("test_regret", "mean"),
        )
        .reset_index()
    )
    fig, ax1 = plt.subplots(figsize=(10, 4.6))
    idx = np.arange(len(grouped))
    width = 0.32
    ax1.bar(idx - width / 2, grouped["best_val_top3"], width, label="Best val Top-3", color=COLORS["blue"])
    ax1.bar(idx + width / 2, grouped["best_test_top3"], width, label="Best test Top-3", color=COLORS["green"])
    ax1.set_xticks(idx)
    ax1.set_xticklabels(grouped["feature_set"].str.replace("_", " "))
    ax1.set_ylabel("Top-3 hit rate")
    ax1.grid(axis="y")
    ax1.legend(loc="upper left")
    ax2 = ax1.twinx()
    ax2.plot(idx, grouped["mean_regret"], color=COLORS["red"], marker="o", linewidth=2.5, label="Mean regret")
    ax2.set_ylabel("Mean regret")
    ax2.legend(loc="upper right")
    ax1.set_title("Feature ablation: stable core vs advanced features")
    fig.tight_layout()
    fig.savefig(FIGURES / "report_03_feature_strategy_ablation.png", bbox_inches="tight")
    plt.close(fig)

    # Best model highlight.
    best = df51.loc[df51["model"].eq(v51["best_model"]) & df51["feature_set"].eq(v51["feature_set"])].iloc[0]
    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.set_facecolor("#F8FAFC")
    ax.axis("off")
    ax.text(0.04, 0.88, "Final selected model", fontsize=13, color=COLORS["muted"], weight="bold")
    ax.text(0.04, 0.74, f"{best['model']} ({best['feature_set']})", fontsize=24, color=COLORS["ink"], weight="bold")
    ax.text(
        0.04,
        0.62,
        "Selected using the validation business score: Top-3, NDCG@3 and regret.",
        fontsize=11,
        color=COLORS["muted"],
    )
    cards = [
        ("Val Top-3", best["val_top3"], COLORS["blue"], "{:.1%}"),
        ("Test Top-3", best["test_top3"], COLORS["green"], "{:.1%}"),
        ("Test NDCG@3", best["test_ndcg3"], COLORS["purple"], "{:.3f}"),
        ("Test regret", best["test_regret"], COLORS["red"], "{:.1f}"),
    ]
    for i, (name, value, color, fmt) in enumerate(cards):
        left = 0.04 + i * 0.235
        rect = plt.Rectangle((left, 0.24), 0.205, 0.25, transform=ax.transAxes, color="white", ec="#E5E7EB", lw=1.2)
        ax.add_patch(rect)
        ax.text(left + 0.025, 0.40, name, transform=ax.transAxes, fontsize=10, color=COLORS["muted"], weight="bold")
        ax.text(left + 0.025, 0.29, fmt.format(value), transform=ax.transAxes, fontsize=19, color=color, weight="bold")
    ax.text(
        0.04,
        0.10,
        "Interpretation: v5.1 prioritizes a robust and explainable Top-3 market recommendation.",
        fontsize=10.5,
        color=COLORS["ink"],
    )
    fig.savefig(FIGURES / "report_04_best_model_highlight.png", bbox_inches="tight")
    plt.close(fig)

    # Ranking quality tradeoff.
    fig, ax = plt.subplots(figsize=(10, 6))
    for feature_set, group in df51.groupby("feature_set"):
        ax.scatter(
            group["test_regret"],
            group["test_ndcg3"],
            s=80 + 500 * group["val_top3"],
            alpha=0.76,
            label=feature_set,
            edgecolor="white",
            linewidth=1.0,
        )
        for _, row in group.iterrows():
            if row["model"] in {"RandomForest", "CatBoost", "XGBoost", "LightGBM"}:
                ax.text(row["test_regret"] + 0.6, row["test_ndcg3"], row["model"], fontsize=8)
    ax.scatter(best["test_regret"], best["test_ndcg3"], s=300, marker="*", color=COLORS["red"], label="Final selected")
    ax.set_xlabel("Mean regret on test set (lower is better)")
    ax.set_ylabel("NDCG@3 on test set (higher is better)")
    ax.set_title("Ranking quality vs regret tradeoff - v5.1")
    ax.grid(True)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / "report_05_ranking_quality_tradeoff.png", bbox_inches="tight")
    plt.close(fig)

    conclusion = (
        "# Conclusion benchmark Phase 1 v5.1\n\n"
        "Le benchmark v5.1 finalise la s\u00e9lection du mod\u00e8le de scoring des march\u00e9s "
        "en privil\u00e9giant les m\u00e9triques directement align\u00e9es avec l'usage PME: "
        "recommander un Top 3 exploitable, limiter le regret m\u00e9tier et conserver une logique explicable.\n\n"
        f"Le mod\u00e8le retenu est **{v51['best_model']}** avec le jeu de variables **{v51['feature_set']}**. "
        f"Il obtient un Top-3 validation de **{best['val_top3']:.3f}**, un NDCG@3 validation de "
        f"**{best['val_ndcg3']:.3f}**, un Top-3 test de **{best['test_top3']:.3f}** et un regret test "
        f"moyen de **{best['test_regret']:.2f}**.\n\n"
        "La principale am\u00e9lioration de v5.1 n'est pas seulement l'ajout de mod\u00e8les plus complexes: "
        "c'est la stabilisation de la d\u00e9cision. Les features avanc\u00e9es de v5 ont \u00e9t\u00e9 test\u00e9es, "
        "mais elles n'apportent pas un gain m\u00e9tier suffisamment stable. La version finale retient donc "
        "le noyau v4 stable, plus robuste et plus facile \u00e0 int\u00e9grer dans le backend.\n\n"
        "Pour le rapport, il faut pr\u00e9senter v5.1 comme la version finale orient\u00e9e d\u00e9cision: "
        "elle transforme un probl\u00e8me de pr\u00e9diction de valeur export en probl\u00e8me de ranking de march\u00e9s, "
        "ce qui correspond mieux au besoin r\u00e9el d'une PME marocaine qui doit choisir un march\u00e9 prioritaire "
        "parmi plusieurs destinations possibles.\n"
    )
    (FIGURES / "report_06_conclusion_v5_1.md").write_text(conclusion, encoding="utf-8")

    manifest = {
        "tables": [
            "report_table_ieee_final_comparison.csv",
            "report_table_ieee_final_comparison.tex",
            "report_table_ieee_final_comparison.md",
            "report_table_v5_1_all_models.csv",
            "report_table_v5_1_all_models.tex",
            "report_table_v5_1_all_models.md",
        ],
        "figures": [
            "report_table_ieee_final_comparison.png",
            "report_table_v5_1_all_models.png",
            "report_01_benchmark_evolution.png",
            "report_02_v5_1_metric_dashboard.png",
            "report_03_feature_strategy_ablation.png",
            "report_04_best_model_highlight.png",
            "report_05_ranking_quality_tradeoff.png",
            "report_06_conclusion_v5_1.md",
        ],
        "selected_model": {
            "model": v51["best_model"],
            "feature_set": v51["feature_set"],
            "val_top3": float(best["val_top3"]),
            "test_top3": float(best["test_top3"]),
            "test_ndcg3": float(best["test_ndcg3"]),
            "test_regret": float(best["test_regret"]),
        },
    }
    (FIGURES / "report_manifest_v5_1.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
