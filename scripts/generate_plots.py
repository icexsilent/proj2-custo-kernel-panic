#!/usr/bin/env python3
"""
generate_plots.py
Gera todos os 8 gráficos exigidos no roteiro de experimentos distcc (Seção 6)
a partir dos arquivos CSV em results/ e salva em plots/ com alta resolução (300 DPI),
com margens e posicionamento de rótulos ajustados para evitar qualquer sobreposição de texto.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "font.size": 10.5,
    "axes.titlesize": 12.5,
    "axes.titleweight": "bold",
    "axes.labelsize": 10.5,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

PALETTE = ["#2563eb", "#059669", "#d97706", "#dc2626", "#7c3aed", "#0891b2"]


def plot_01_individual_vs_coletivo(df_tempos: pd.DataFrame, out_dir: str):
    sub = df_tempos[df_tempos["experimento"] == "exp1_individual_coletivo"]
    if sub.empty:
        return
    stats = (
        sub.groupby("rotulo", sort=False)["tempo_s"]
        .agg(["mean", "std"])
        .reset_index()
    )
    stats["std"] = stats["std"].fillna(0.0)

    labels_map = {
        "Maquina_1_Individual": "Máquina 1\n(Individual)",
        "Maquina_2_Individual": "Máquina 2\n(Individual)",
        "Coletivo_M1_M2": "Coletivo\n(Máq. 1 + Máq. 2)",
    }
    x_labels = [labels_map.get(r, r) for r in stats["rotulo"]]
    colors = ["#3b82f6", "#60a5fa", "#10b981"][: len(stats)]

    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    bars = ax.bar(
        x_labels,
        stats["mean"],
        yerr=stats["std"],
        capsize=6,
        color=colors,
        edgecolor="#1e293b",
        width=0.5,
    )
    ax.set_title("Pergunta 1: Tempo de Compilação Individual vs. Coletivo", pad=12)
    ax.set_ylabel("Tempo Médio de Compilação (s)")
    top_y = (stats["mean"] + stats["std"]).max()
    ax.set_ylim(0, top_y * 1.28)

    for bar, (_, row) in zip(bars, stats.iterrows()):
        h = bar.get_height()
        ax.annotate(
            f"{row['mean']:.2f}s ± {row['std']:.2f}s",
            xy=(bar.get_x() + bar.get_width() / 2, h + row["std"]),
            xytext=(0, 7),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=10,
        )

    if len(stats) >= 3:
        t_ind = stats.iloc[0]["mean"]
        t_col = stats.iloc[-1]["mean"]
        if t_col > 0:
            reducao = ((t_ind - t_col) / t_ind) * 100.0
            speedup = t_ind / t_col
            ax.text(
                0.97,
                0.93,
                f"Redução Coletiva: {reducao:.1f}%\nSpeedup: {speedup:.2f}x",
                transform=ax.transAxes,
                ha="right",
                va="top",
                bbox=dict(boxstyle="round,pad=0.45", facecolor="#ecfdf5", edgecolor="#059669"),
                fontsize=10,
            )

    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "01_individual_vs_coletivo.png"))
    plt.close(fig)


def plot_02_percentual_por_maquina(df_hosts: pd.DataFrame, out_dir: str):
    if df_hosts.empty:
        return
    sub = df_hosts[
        (df_hosts["experimento"] == "exp1_individual_coletivo")
        & (df_hosts["rotulo"] == "Coletivo_M1_M2")
        & (~df_hosts["host"].isin(["local_make", "localhost"]))
    ]
    if sub.empty:
        sub = df_hosts[~df_hosts["host"].isin(["local_make", "localhost"])]
    if sub.empty:
        return

    grouped = (
        sub.groupby("host")["arquivos_compilados"]
        .mean()
        .reset_index()
    )
    total = grouped["arquivos_compilados"].sum()
    if total <= 0:
        return

    host_labels = []
    for idx, h in enumerate(grouped["host"], start=1):
        if ":3632" in h:
            host_labels.append(f"Máquina 1\n({h})")
        elif ":3633" in h:
            host_labels.append(f"Máquina 2\n({h})")
        else:
            host_labels.append(f"Nó {idx}\n({h})")

    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    wedges, texts, autotexts = ax.pie(
        grouped["arquivos_compilados"],
        labels=host_labels,
        autopct=lambda pct: f"{pct:.1f}%\n({round(pct*total/100):.0f} arqs)",
        startangle=90,
        radius=0.82,
        pctdistance=0.62,
        labeldistance=1.15,
        colors=PALETTE[: len(grouped)],
        wedgeprops=dict(width=0.52, edgecolor="white", linewidth=2.5),
        textprops=dict(fontsize=10.5, fontweight="bold"),
    )
    for at in autotexts:
        at.set_fontweight("bold")
        at.set_color("white")
        at.set_fontsize(10.5)

    ax.set_title("Pergunta 2: Contribuição de Compilação por Máquina (Arquivos .c)", pad=14)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "02_percentual_por_maquina.png"))
    plt.close(fig)


def plot_03_kernel_vs_sqlite(df_tempos: pd.DataFrame, out_dir: str):
    sub = df_tempos[df_tempos["experimento"] == "exp3_projetos"]
    if sub.empty:
        return

    stats = (
        sub.groupby(["projeto", "rotulo"], sort=False)["tempo_s"]
        .agg(["mean", "std"])
        .reset_index()
    )
    stats["std"] = stats["std"].fillna(0.0)

    projetos = list(dict.fromkeys(stats["projeto"]))
    x = np.arange(len(projetos))
    width = 0.34

    solo_means, solo_stds = [], []
    dist_means, dist_stds = [], []

    for p in projetos:
        s_row = stats[(stats["projeto"] == p) & (stats["rotulo"] == "Solo")]
        d_row = stats[(stats["projeto"] == p) & (stats["rotulo"] == "Distribuido")]
        solo_means.append(s_row["mean"].values[0] if not s_row.empty else 0)
        solo_stds.append(s_row["std"].values[0] if not s_row.empty else 0)
        dist_means.append(d_row["mean"].values[0] if not d_row.empty else 0)
        dist_stds.append(d_row["std"].values[0] if not d_row.empty else 0)

    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    b1 = ax.bar(
        x - width / 2,
        solo_means,
        width,
        yerr=solo_stds,
        capsize=5,
        label="Solo (make local)",
        color="#64748b",
        edgecolor="#1e293b",
    )
    b2 = ax.bar(
        x + width / 2,
        dist_means,
        width,
        yerr=dist_stds,
        capsize=5,
        label="Distribuído (distcc)",
        color="#2563eb",
        edgecolor="#1e293b",
    )

    max_y = max(
        max([m + s for m, s in zip(solo_means, solo_stds)], default=1),
        max([m + s for m, s in zip(dist_means, dist_stds)], default=1),
    )
    ax.set_title("Pergunta 3: Comparação de Projetos — SQLite vs. Kernel Linux", pad=12)
    ax.set_ylabel("Tempo Médio de Compilação (s)")
    ax.set_xticks(x)
    ax.set_xticklabels([p.replace("_", " ") for p in projetos], fontweight="bold", fontsize=11)
    ax.set_ylim(0, max_y * 1.30)
    ax.legend(loc="upper left")

    for i in range(len(projetos)):
        if solo_means[i] > 0 and dist_means[i] > 0:
            sp = solo_means[i] / dist_means[i]
            red = ((solo_means[i] - dist_means[i]) / solo_means[i]) * 100.0
            y_top = max(solo_means[i] + solo_stds[i], dist_means[i] + dist_stds[i])
            ax.annotate(
                f"Speedup: {sp:.2f}x (-{red:.1f}%)",
                xy=(x[i], y_top),
                xytext=(0, 18),
                textcoords="offset points",
                ha="center",
                fontweight="bold",
                fontsize=10,
                bbox=dict(boxstyle="round,pad=0.35", facecolor="#eff6ff", edgecolor="#2563eb"),
            )

    for bars in (b1, b2):
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                if h >= max_y * 0.14:
                    ax.annotate(
                        f"{h:.2f}s",
                        xy=(bar.get_x() + bar.get_width() / 2, h * 0.5),
                        ha="center",
                        va="center",
                        color="white",
                        fontweight="bold",
                        fontsize=9.5,
                    )
                else:
                    ax.annotate(
                        f"{h:.2f}s",
                        xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center",
                        va="bottom",
                        color="#0f172a",
                        fontweight="bold",
                        fontsize=9,
                    )

    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "03_kernel_vs_sqlite.png"))
    plt.close(fig)


def plot_04_velocidade_rede(df_tempos: pd.DataFrame, out_dir: str):
    sub = df_tempos[df_tempos["experimento"] == "exp4_rede"].copy()
    if sub.empty:
        return
    sub["bw_mbps"] = sub["extra"].astype(float)
    stats = (
        sub.groupby("bw_mbps")["tempo_s"]
        .agg(["mean", "std"])
        .reset_index()
        .sort_values("bw_mbps")
    )
    stats["std"] = stats["std"].fillna(0.0)

    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    ax.errorbar(
        stats["bw_mbps"],
        stats["mean"],
        yerr=stats["std"],
        fmt="-o",
        color="#2563eb",
        linewidth=2.2,
        markersize=7,
        capsize=5,
        label="Tempo de Build Distribuído (±1 DP)",
    )
    ax.set_xscale("log")
    ax.set_xticks(stats["bw_mbps"])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_xlabel("Velocidade da Rede Limitada via tc tbf (Mbit/s — escala log)")
    ax.set_ylabel("Tempo de Compilação (s)")
    ax.set_title("Pergunta 4: Impacto da Velocidade de Rede no Tempo de Compilação", pad=12)

    min_t = stats["mean"].min()
    max_t = stats["mean"].max()
    ax.set_ylim(-0.5, max_t * 1.12)

    knee_rows = stats[stats["mean"] <= min_t + (max_t - min_t) * 0.05]
    if not knee_rows.empty:
        knee = knee_rows.iloc[0]
        ax.axvline(knee["bw_mbps"], color="#dc2626", linestyle=":", linewidth=1.8)
        ax.annotate(
            f"Joelho da curva (~{int(knee['bw_mbps'])} Mbit/s)\nRede deixa de ser gargalo\n({knee['mean']:.2f}s)",
            xy=(knee["bw_mbps"], knee["mean"]),
            xytext=(knee["bw_mbps"] * 0.65, knee["mean"] + (max_t - min_t) * 0.34),
            ha="center",
            arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.5),
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#fef2f2", edgecolor="#dc2626"),
            fontsize=9.5,
            fontweight="bold",
        )

    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "04_velocidade_rede.png"))
    plt.close(fig)


def plot_05a_escala_maquinas(df_tempos: pd.DataFrame, out_dir: str):
    sub = df_tempos[df_tempos["experimento"] == "exp5a_escala"].copy()
    if sub.empty:
        return
    sub["n_maq"] = sub["extra"].astype(int)
    stats = (
        sub.groupby("n_maq")["tempo_s"]
        .agg(["mean", "std"])
        .reset_index()
        .sort_values("n_maq")
    )
    stats["std"] = stats["std"].fillna(0.0)

    t1 = stats.iloc[0]["mean"]
    stats["speedup"] = t1 / stats["mean"]
    stats["eficiencia"] = (stats["speedup"] / stats["n_maq"]) * 100.0
    p_frac = 0.88
    stats["amdahl"] = 1.0 / ((1.0 - p_frac) + (p_frac / stats["n_maq"]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 5.4))

    ax1.errorbar(
        stats["n_maq"],
        stats["mean"],
        yerr=stats["std"],
        fmt="-o",
        color="#2563eb",
        linewidth=2.2,
        markersize=7,
        capsize=5,
    )
    ax1.set_xticks(stats["n_maq"])
    ax1.set_xlim(0.7, stats["n_maq"].max() + 0.3)
    ax1.set_ylim(stats["mean"].min() * 0.72, stats["mean"].max() * 1.16)
    ax1.set_xlabel("Número de Servidores distccd")
    ax1.set_ylabel("Tempo Médio de Compilação (s)")
    ax1.set_title("Escala: Nº de Máquinas × Tempo", pad=10)
    for _, r in stats.iterrows():
        ax1.annotate(
            f"{r['mean']:.2f}s",
            xy=(r["n_maq"], r["mean"]),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            fontweight="bold",
            fontsize=9.5,
        )

    ax2.plot(stats["n_maq"], stats["n_maq"], "--", color="#94a3b8", label="Speedup Linear Ideal (S = N)")
    ax2.plot(stats["n_maq"], stats["amdahl"], "-.", color="#d97706", linewidth=2, label="Lei de Amdahl (P = 88%)")
    ax2.plot(stats["n_maq"], stats["speedup"], "-s", color="#059669", linewidth=2.2, markersize=7, label="Speedup Medido (T₁/Tₙ)")
    ax2.set_xticks(stats["n_maq"])
    ax2.set_xlim(0.7, stats["n_maq"].max() + 0.35)
    ax2.set_ylim(0.55, stats["n_maq"].max() * 1.12)
    ax2.set_xlabel("Número de Servidores distccd")
    ax2.set_ylabel("Speedup (x)")
    ax2.set_title("Speedup Real vs. Lei de Amdahl & Eficiência", pad=10)
    for _, r in stats.iterrows():
        ax2.annotate(
            f"{r['speedup']:.2f}x\n(Efic: {r['eficiencia']:.0f}%)",
            xy=(r["n_maq"], r["speedup"]),
            xytext=(0, -26),
            textcoords="offset points",
            ha="center",
            fontsize=8.5,
            fontweight="bold",
            color="#065f46",
        )
    ax2.legend(loc="upper left")

    fig.suptitle("Pergunta 5A: Escalabilidade Horizontal com distcc", fontsize=13.5, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(os.path.join(out_dir, "05a_escala_maquinas.png"))
    plt.close(fig)


def plot_05b_processos_fundo(df_tempos: pd.DataFrame, out_dir: str):
    sub = df_tempos[df_tempos["experimento"] == "exp5b_stress"].copy()
    if sub.empty:
        return
    sub["carga_pct"] = sub["extra"].astype(int)
    stats = (
        sub.groupby("carga_pct")["tempo_s"]
        .agg(["mean", "std"])
        .reset_index()
        .sort_values("carga_pct")
    )
    stats["std"] = stats["std"].fillna(0.0)

    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    x_labels = [f"{c}%" for c in stats["carga_pct"]]
    bars = ax.bar(
        x_labels,
        stats["mean"],
        yerr=stats["std"],
        capsize=6,
        color=["#10b981", "#f59e0b", "#f97316", "#ef4444"][: len(stats)],
        edgecolor="#1e293b",
        width=0.48,
    )
    ax.plot(range(len(stats)), stats["mean"], "-o", color="#1e293b", linewidth=1.8, label="Tendência de degradação")
    ax.set_xlabel("Carga de CPU Concorrente nos Servidores (stress-ng)")
    ax.set_ylabel("Tempo de Compilação (s)")
    ax.set_title("Pergunta 5B: Impacto de Processos de Fundo Competindo por CPU", pad=14)

    # Garante margem generosa acima da maior barra + barra de erro para nunca encostar no título
    max_top = (stats["mean"] + stats["std"]).max()
    ax.set_ylim(0, max_top * 1.24)

    t0 = stats.iloc[0]["mean"]
    for idx, (bar, (_, r)) in enumerate(zip(bars, stats.iterrows())):
        delta = ((r["mean"] - t0) / t0) * 100.0 if t0 > 0 else 0.0
        # Desloca ligeiramente à esquerda no ponto de 50% para não cruzar a linha de tendência
        x_offset = -18 if idx == 2 else 0
        ax.annotate(
            f"{r['mean']:.2f}s\n({delta:+.0f}%)",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height() + r["std"]),
            xytext=(x_offset, 7),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.8),
        )

    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "05b_processos_fundo.png"))
    plt.close(fig)


def plot_05c_arquivos_vs_speedup(df_tempos: pd.DataFrame, out_dir: str):
    sub = df_tempos[df_tempos["experimento"] == "exp5c_num_arquivos"].copy()
    if sub.empty:
        return
    sub["n_arq"] = sub["extra"].astype(int)
    piv = (
        sub.groupby(["n_arq", "modo"])["tempo_s"]
        .mean()
        .unstack("modo")
        .dropna()
        .reset_index()
        .sort_values("n_arq")
    )
    if "solo" not in piv.columns or "distcc" not in piv.columns:
        return

    piv["speedup"] = piv["solo"] / piv["distcc"]

    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    ax.plot(
        piv["n_arq"],
        piv["speedup"],
        "-o",
        color="#2563eb",
        linewidth=2.4,
        markersize=8,
        label="Speedup Medido (T_solo / T_distcc)",
    )
    ax.axhline(1.0, color="#dc2626", linestyle="--", linewidth=1.6, label="Limiar de Ganho (Speedup = 1.0x)")
    ax.set_xlabel("Quantidade de Arquivos .c no Projeto")
    ax.set_ylabel("Speedup (T_solo / T_distcc)")
    ax.set_title("Pergunta 5C: Nº de Arquivos .c × Ganho de Paralelização (Speedup)", pad=12)

    min_x, max_x = piv["n_arq"].min(), piv["n_arq"].max()
    span_x = max(max_x - min_x, 10)
    ax.set_xlim(min_x - span_x * 0.14, max_x + span_x * 0.14)
    ax.set_ylim(0, max(piv["speedup"].max() * 1.28, 1.5))

    for _, r in piv.iterrows():
        ax.annotate(
            f"{r['speedup']:.2f}x\n({r['solo']:.1f}s vs {r['distcc']:.1f}s)",
            xy=(r["n_arq"], r["speedup"]),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.8),
        )

    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "05c_arquivos_vs_speedup.png"))
    plt.close(fig)


def plot_06_energia(df_energia: pd.DataFrame, out_dir: str):
    if df_energia.empty:
        return
    sub = df_energia.sort_values("arquivos_c").copy()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.0, 5.6))

    e_solo_mwh = sub["energia_solo_wh"] * 1000.0
    e_dist_mwh = sub["energia_dist_2maq_wh"] * 1000.0

    # Subplot 1: Energia Total (mWh) calculada sobre os tempos reais medidos
    ax1.plot(
        sub["arquivos_c"],
        e_solo_mwh,
        "-o",
        color="#64748b",
        linewidth=2.2,
        markersize=7,
        label="Solo (1 Máq. @ 150W = 45W Idle + 105W TDP)",
    )
    ax1.plot(
        sub["arquivos_c"],
        e_dist_mwh,
        "-s",
        color="#059669",
        linewidth=2.2,
        markersize=7,
        label="Distribuído (2 Máq. @ 268.5W = 2×45W Idle + Carga)",
    )
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xticks(sub["arquivos_c"])
    ax1.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax1.set_xlim(sub["arquivos_c"].min() * 0.6, sub["arquivos_c"].max() * 1.75)
    ax1.set_ylim(e_dist_mwh.min() * 0.42, e_solo_mwh.max() * 2.6)
    ax1.set_xlabel("Arquivos .c Compilados nos Testes Reais (escala log)")
    ax1.set_ylabel("Energia Consumida: P × Tempo Medido (mWh — log)")
    ax1.set_title("Consumo de Energia Total (mWh) — Dados Medidos", pad=10)
    for _, r in sub.iterrows():
        ax1.annotate(
            f"{r['energia_dist_2maq_wh']*1000:.0f} mWh",
            xy=(r["arquivos_c"], r["energia_dist_2maq_wh"] * 1000.0),
            xytext=(0, -18),
            textcoords="offset points",
            ha="center",
            fontsize=8.5,
            color="#065f46",
            fontweight="bold",
        )
    ax1.legend(fontsize=8.5, loc="upper left")

    # Subplot 2: EDP (Energy-Delay Product = mWh * s) sobre os tempos reais medidos
    edp_solo_mwhs = sub["edp_solo_wh_s"] * 1000.0
    edp_dist_mwhs = sub["edp_dist_2maq_wh_s"] * 1000.0
    ax2.plot(
        sub["arquivos_c"],
        edp_solo_mwhs,
        "-o",
        color="#64748b",
        linewidth=2.2,
        markersize=7,
        label="EDP Solo (Energia × Tempo Medido)",
    )
    ax2.plot(
        sub["arquivos_c"],
        edp_dist_mwhs,
        "-s",
        color="#2563eb",
        linewidth=2.2,
        markersize=7,
        label="EDP Distribuído (Energia × Tempo Medido)",
    )
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xticks(sub["arquivos_c"])
    ax2.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax2.set_xlim(sub["arquivos_c"].min() * 0.6, sub["arquivos_c"].max() * 1.75)
    ax2.set_ylim(edp_dist_mwhs.min() * 0.35, edp_solo_mwhs.max() * 2.8)
    ax2.set_xlabel("Arquivos .c Compilados nos Testes Reais (escala log)")
    ax2.set_ylabel("Produto Energia-Atraso: EDP (mWh · s — log)")
    ax2.set_title("Eficiência Conjunta EDP (Menor = Melhor)", pad=10)

    for _, r in sub.iterrows():
        ratio = r["edp_solo_wh_s"] / r["edp_dist_2maq_wh_s"] if r["edp_dist_2maq_wh_s"] > 0 else 1.0
        ax2.annotate(
            f"{ratio:.2f}x melhor",
            xy=(r["arquivos_c"], r["edp_dist_2maq_wh_s"] * 1000.0),
            xytext=(0, -18),
            textcoords="offset points",
            ha="center",
            fontsize=8.5,
            color="#1d4ed8",
            fontweight="bold",
        )

    ax2.legend(fontsize=8.5, loc="upper left")

    fig.suptitle(
        "Pergunta 6: Energia (TDP × Tempo Real Medido) — 8, 24, 48, 103 (SQLite) e 913 (Kernel) Arquivos",
        fontsize=12.8,
        fontweight="bold",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(os.path.join(out_dir, "06_energia_wh_edp.png"))
    plt.close(fig)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    results_dir = os.environ.get("RESULTS_DIR_OVERRIDE", os.path.join(root_dir, "results"))
    plots_dir = os.environ.get("PLOTS_DIR_OVERRIDE", os.path.join(root_dir, "plots"))
    os.makedirs(plots_dir, exist_ok=True)

    tempos_csv = os.path.join(results_dir, "tempos_compilacao.csv")
    hosts_csv = os.path.join(results_dir, "distribuicao_hosts.csv")
    energia_csv = os.path.join(results_dir, "energia_estimada.csv")

    df_tempos = pd.read_csv(tempos_csv) if os.path.exists(tempos_csv) else pd.DataFrame()
    df_hosts = pd.read_csv(hosts_csv) if os.path.exists(hosts_csv) else pd.DataFrame()
    df_energia = pd.read_csv(energia_csv) if os.path.exists(energia_csv) else pd.DataFrame()

    plot_01_individual_vs_coletivo(df_tempos, plots_dir)
    plot_02_percentual_por_maquina(df_hosts, plots_dir)
    plot_03_kernel_vs_sqlite(df_tempos, plots_dir)
    plot_04_velocidade_rede(df_tempos, plots_dir)
    plot_05a_escala_maquinas(df_tempos, plots_dir)
    plot_05b_processos_fundo(df_tempos, plots_dir)
    plot_05c_arquivos_vs_speedup(df_tempos, plots_dir)
    plot_06_energia(df_energia, plots_dir)

    generated = sorted(f for f in os.listdir(plots_dir) if f.endswith(".png"))
    print(f"[plots] {len(generated)} gráficos gerados em {plots_dir}:")
    for g in generated:
        p = os.path.join(plots_dir, g)
        print(f"  - {g} ({os.path.getsize(p) // 1024} KB)")


if __name__ == "__main__":
    main()
