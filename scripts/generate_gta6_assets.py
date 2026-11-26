#!/usr/bin/env python3
"""
Prepara os assets 1080p extraidos do video GTA 6 e gera os graficos experimentais
com tema escuro/neon Vice City para o PowerPoint (.pptx) e PDF (.pdf).
"""
import os
import shutil
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT_DIR = "/mnt/e/Faculdade/SistemasOperacionais"
FRAMES_DIR = "/root/distcc_lab/gta_frames"
ASSETS_DIR = os.path.join(ROOT_DIR, "plots_gta6")
RESULTS_DIR = os.path.join(ROOT_DIR, "results")

os.makedirs(ASSETS_DIR, exist_ok=True)

# 1. Prepare clean 1920x1080 background plates from the video frames
# Plate A: f_017 (PS5 home screen), cover "Seu Nome" at top center with surrounding dark sky gradient
im_ps5 = Image.open(os.path.join(FRAMES_DIR, "f_017.jpg")).convert("RGB")
# "Seu Nome" is near top center (around x=730..860, y=20..65 on 1920x1080)
# Let's replace "Seu Nome" with a clean dark pill or sample adjacent pixels
draw_ps5 = ImageDraw.Draw(im_ps5)
# Sample color around (720, 42)
bg_col = im_ps5.getpixel((1180, 50))
draw_ps5.rectangle([1115, 70, 1310, 122], fill=bg_col)
im_ps5.save(os.path.join(ASSETS_DIR, "bg_intro_ps5.jpg"), quality=95)

# Plate B: f_048 (Rockstar R* glowing police siren background)
im_rockstar = Image.open(os.path.join(FRAMES_DIR, "f_048.jpg")).convert("RGB")
im_rockstar.save(os.path.join(ASSETS_DIR, "bg_intro_rockstar.jpg"), quality=95)

# Plate C: f_092 (Clean GTA VI Roman Numeral logo on Vice City sunset beach, before text)
im_vi = Image.open(os.path.join(FRAMES_DIR, "f_092.jpg")).convert("RGB")
im_vi.save(os.path.join(ASSETS_DIR, "bg_cover_vi.jpg"), quality=95)

# Plate D: f_173 (Clean Vice City sunset beach without text) -> create darkened HUD background for content slides
im_sunset = Image.open(os.path.join(FRAMES_DIR, "f_173.jpg")).convert("RGB")
im_sunset.save(os.path.join(ASSETS_DIR, "bg_sunset_clean.jpg"), quality=95)

# Darkened content slide background (matching the dark overlay in the video's content slides)
overlay = Image.new("RGB", im_sunset.size, (10, 13, 24))
im_dark_hud = Image.blend(im_sunset, overlay, alpha=0.80)
im_dark_hud.save(os.path.join(ASSETS_DIR, "bg_content_dark.jpg"), quality=95)

# Plate E: f_177 (Final slide: "APRESENTACAO CONCLUIDA" + Trophy popup)
im_end = Image.open(os.path.join(FRAMES_DIR, "f_177.jpg")).convert("RGB")
im_end.save(os.path.join(ASSETS_DIR, "bg_end_concluida.jpg"), quality=95)

print("Saved 1080p GTA 6 background plates to", ASSETS_DIR)

# 2. Generate GTA 6 Dark/Neon Vice City Charts from real CSV data
plt.rcParams.update({
    "figure.facecolor": "#0d111f",
    "axes.facecolor": "#13192b",
    "axes.edgecolor": "#475569",
    "axes.labelcolor": "#f1f5f9",
    "text.color": "#ffffff",
    "xtick.color": "#cbd5e1",
    "ytick.color": "#cbd5e1",
    "grid.color": "#334155",
    "grid.linestyle": "--",
    "grid.alpha": 0.45,
    "font.sans-serif": ["DejaVu Sans", "Arial"],
    "font.size": 10.5,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 10.5,
    "axes.labelweight": "bold",
    "savefig.dpi": 240,
    "savefig.facecolor": "#0d111f",
    "savefig.edgecolor": "none",
})

df_t = pd.read_csv(os.path.join(RESULTS_DIR, "tempos_compilacao.csv"))
df_h = pd.read_csv(os.path.join(RESULTS_DIR, "distribuicao_hosts.csv"))
df_e = pd.read_csv(os.path.join(RESULTS_DIR, "energia_estimada.csv"))

# Chart 01: Individual vs Coletivo
sub1 = df_t[df_t["experimento"] == "exp1_individual_coletivo"]
g1 = sub1.groupby("rotulo")["tempo_s"].agg(["mean", "std"]).reindex(["Maquina_1_Individual", "Maquina_2_Individual", "Coletivo_M1_M2"])
fig, ax = plt.subplots(figsize=(6.8, 4.3))
labels1 = ["Máquina 1\n(Solo -j4)", "Máquina 2\n(Solo -j4)", "Coletivo\n(M1 + M2 -j8)"]
colors1 = ["#38bdf8", "#a855f7", "#00ff9d"]
bars = ax.bar(labels1, g1["mean"], yerr=g1["std"].fillna(0), capsize=5, color=colors1, edgecolor="#ffffff", linewidth=1.2, width=0.52, error_kw=dict(ecolor="#ffffff", lw=1.4))
ax.set_ylabel("Tempo Médio (s)")
ax.set_title("Tempo de Compilação: Individual vs. Coletivo", color="#ff79c6", pad=10)
ax.set_ylim(0, g1["mean"].max() * 1.28)
ax.grid(axis="y")
for bar, (_, row) in zip(bars, g1.iterrows()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.06, f"{row['mean']:.2f}s", ha="center", va="bottom", fontweight="bold", color="#ffffff", fontsize=11)
ax.text(0.97, 0.92, "Speedup: 1,55x (-35,5%)", transform=ax.transAxes, ha="right", va="top", bbox=dict(boxstyle="round,pad=0.35", facecolor="#1e293b", edgecolor="#00ff9d", lw=1.5), color="#00ff9d", fontweight="bold", fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(ASSETS_DIR, "gta_01_ind_coletivo.png"))
plt.close(fig)

# Chart 02: Percentual por Maquina
sub2 = df_h[(df_h["experimento"] == "exp1_individual_coletivo") & (df_h["rotulo"] == "Coletivo_M1_M2") & (df_h["repeticao"] == 1) & (df_h["host"] != "localhost")]
fig, ax = plt.subplots(figsize=(6.8, 4.3))
wedges, texts, autotexts = ax.pie(
    sub2["arquivos_compilados"],
    labels=[f"Nó 1 (:3632)\n{sub2.iloc[0]['arquivos_compilados']} arqs .c", f"Nó 2 (:3633)\n{sub2.iloc[1]['arquivos_compilados']} arqs .c"],
    autopct="%1.1f%%",
    startangle=90,
    colors=["#38bdf8", "#ff2a85"],
    wedgeprops=dict(width=0.52, edgecolor="#0d111f", linewidth=3),
    textprops=dict(color="#ffffff", fontweight="bold", fontsize=10.5),
    pctdistance=0.72,
)
for at in autotexts:
    at.set_color("#ffffff")
    at.set_fontsize(11)
ax.set_title("Distribuição de Tarefas entre Servidores (Logs distcc)", color="#ff79c6", pad=10)
fig.tight_layout()
fig.savefig(os.path.join(ASSETS_DIR, "gta_02_distribuicao.png"))
plt.close(fig)

# Chart 03: SQLite vs Kernel Linux
sub3 = df_t[df_t["experimento"] == "exp3_projetos"]
g3 = sub3.groupby(["projeto", "rotulo"])["tempo_s"].mean().unstack()
fig, ax = plt.subplots(figsize=(7.2, 4.8))
projetos = ["SQLite", "Kernel_Linux"]
x = np.arange(len(projetos))
w = 0.34
b_solo = ax.bar(x - w/2, [g3.loc[p, "Solo"] for p in projetos], w, label="Solo (Local -j2)", color="#64748b", edgecolor="#ffffff", lw=1.2)
b_dist = ax.bar(x + w/2, [g3.loc[p, "Distribuido"] for p in projetos], w, label="Distribuído (distcc -j12)", color="#38bdf8", edgecolor="#ffffff", lw=1.2)
ax.set_xticks(x)
ax.set_xticklabels(["SQLite 3.47.2\n(103 arquivos .c)", "Kernel Linux 6.6.72\n(904 objetos .o)"], fontweight="bold")
ax.set_ylabel("Tempo Médio de Compilação (s)")
ax.set_title("Projetos Reais: SQLite vs. Kernel Linux", color="#ff79c6", pad=12)
ax.set_ylim(0, 210)
ax.grid(axis="y")
ax.legend(facecolor="#1e293b", edgecolor="#475569", labelcolor="#ffffff")
for bar in list(b_solo) + list(b_dist):
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 3.5, f"{h:.2f}s", ha="center", va="bottom", fontweight="bold", color="#ffffff", fontsize=10)
ax.text(0, 32, "Speedup: 2,12x (-52,9%)", ha="center", bbox=dict(boxstyle="round,pad=0.3", facecolor="#1e293b", edgecolor="#00ff9d"), color="#00ff9d", fontweight="bold", fontsize=9.5)
ax.text(1, 188, "Speedup: 2,80x (-64,3%)", ha="center", bbox=dict(boxstyle="round,pad=0.3", facecolor="#1e293b", edgecolor="#00ff9d"), color="#00ff9d", fontweight="bold", fontsize=9.5)
fig.tight_layout()
fig.savefig(os.path.join(ASSETS_DIR, "gta_03_projetos.png"))
plt.close(fig)

# Chart 04: Velocidade da Rede
sub4 = df_t[df_t["experimento"] == "exp4_rede"].copy()
sub4["bw"] = sub4["extra"].astype(float)
g4 = sub4.groupby("bw")["tempo_s"].mean().reset_index().sort_values("bw")
fig, ax = plt.subplots(figsize=(7.2, 4.8))
ax.plot(g4["bw"], g4["tempo_s"], "-o", color="#00f0ff", linewidth=2.6, markersize=8, markerfacecolor="#ff2a85", markeredgecolor="#ffffff")
ax.set_xscale("log")
ax.set_xticks(g4["bw"])
ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.set_xlabel("Largura de Banda Limitada via tc tbf (Mbps — escala log)")
ax.set_ylabel("Tempo de Compilação (s)")
ax.set_title("Impacto da Largura de Banda da Rede no Build Distribuído", color="#ff79c6", pad=12)
ax.set_ylim(-0.8, 22.5)
ax.grid(True)
ax.axvline(50, color="#ff9e00", linestyle=":", linewidth=2)
ax.annotate("Joelho da Curva (50 Mbps)\n0,80 s — Rede deixa de travar", xy=(50, 0.80), xytext=(22, 8.5), ha="center",
            arrowprops=dict(arrowstyle="->", color="#ff9e00", lw=1.8),
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#1e293b", edgecolor="#ff9e00", lw=1.5),
            color="#ff9e00", fontweight="bold", fontsize=9.5)
for _, r in g4.iterrows():
    if r["bw"] in [1, 5, 10, 100, 1000]:
        ax.text(r["bw"], r["tempo_s"] + 0.75, f"{r['tempo_s']:.2f}s", ha="center", va="bottom", color="#ffffff", fontweight="bold", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(ASSETS_DIR, "gta_04_rede.png"))
plt.close(fig)

# Chart 05A: Escala de Maquinas (1 a 4 nos)
sub5a = df_t[df_t["experimento"] == "exp5a_escala"].copy()
sub5a["n"] = sub5a["extra"].astype(int)
g5a = sub5a.groupby("n")["tempo_s"].mean().reset_index().sort_values("n")
t1 = g5a.iloc[0]["tempo_s"]
g5a["speedup"] = t1 / g5a["tempo_s"]
fig, ax1 = plt.subplots(figsize=(7.2, 4.8))
ax2 = ax1.twinx()
l1 = ax1.plot(g5a["n"], g5a["tempo_s"], "-o", color="#38bdf8", lw=2.6, markersize=8, label="Tempo Médio (s)")
l2 = ax2.plot(g5a["n"], g5a["speedup"], "--s", color="#00ff9d", lw=2.6, markersize=8, label="Speedup Real (x)")
ax1.set_xticks([1, 2, 3, 4])
ax1.set_xticklabels(["1 Máquina\n(-j2)", "2 Máquinas\n(-j4)", "3 Máquinas\n(-j6)", "4 Máquinas\n(-j8)"], fontweight="bold")
ax1.set_ylabel("Tempo Médio (s)", color="#38bdf8")
ax2.set_ylabel("Speedup Alcançado (x)", color="#00ff9d")
ax1.set_ylim(0.4, 2.35)
ax2.set_ylim(0.8, 3.2)
ax1.grid(True)
ax1.set_title("Escalabilidade Horizontal: 1 a 4 Servidores distccd", color="#ff79c6", pad=12)
for _, r in g5a.iterrows():
    ax1.text(r["n"], r["tempo_s"] + 0.08, f"{r['tempo_s']:.2f}s", ha="center", color="#38bdf8", fontweight="bold", fontsize=9.5)
    ax2.text(r["n"], r["speedup"] - 0.18, f"{r['speedup']:.2f}x", ha="center", color="#00ff9d", fontweight="bold", fontsize=9.5)
fig.tight_layout()
fig.savefig(os.path.join(ASSETS_DIR, "gta_05a_escala.png"))
plt.close(fig)

# Chart 05B: Contencao de CPU (stress-ng)
sub5b = df_t[df_t["experimento"] == "exp5b_stress"].copy()
sub5b["carga"] = sub5b["extra"].astype(int)
g5b = sub5b.groupby("carga")["tempo_s"].mean().reset_index().sort_values("carga")
base5b = g5b.iloc[0]["tempo_s"]
fig, ax = plt.subplots(figsize=(7.2, 4.8))
x5b = [f"{int(r['carga'])}%" for _, r in g5b.iterrows()]
cols5b = ["#00ff9d", "#fbbf24", "#f97316", "#ff2a85"]
bars5b = ax.bar(x5b, g5b["tempo_s"], color=cols5b, edgecolor="#ffffff", lw=1.3, width=0.48)
ax.set_xlabel("Ocupação de CPU em Segundo Plano (stress-ng)")
ax.set_ylabel("Tempo de Compilação (s)")
ax.set_title("Degradação por Contenção de Processos na CPU", color="#ff79c6", pad=12)
ax.set_ylim(0, 3.25)
ax.grid(axis="y")
for bar, (_, r) in zip(bars5b, g5b.iterrows()):
    pct = (r["tempo_s"] / base5b - 1.0) * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.08, f"{r['tempo_s']:.2f}s\n(+{pct:.0f}%)", ha="center", va="bottom", color="#ffffff", fontweight="bold", fontsize=9.5)
fig.tight_layout()
fig.savefig(os.path.join(ASSETS_DIR, "gta_05b_contencao.png"))
plt.close(fig)

# Chart 05C & 06: Energia e Speedup por Porte
fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(7.6, 4.4))
# Left: Speedup 8, 24, 48
arqs_5c = [8, 24, 48]
sp_5c = [0.9104/0.4596, 2.3748/0.9181, 4.6138/1.6298]
ax_l.plot(arqs_5c, sp_5c, "-o", color="#00ff9d", lw=2.5, markersize=8, markerfacecolor="#ff2a85", markeredgecolor="#ffffff")
ax_l.set_xticks(arqs_5c)
ax_l.set_xticklabels(["8 arqs", "24 arqs", "48 arqs"], fontweight="bold")
ax_l.set_ylabel("Speedup (T_solo / T_dist)")
ax_l.set_title("Porte (.c) × Speedup", color="#ff79c6", fontsize=11)
ax_l.set_ylim(1.4, 3.2)
ax_l.grid(True)
for a, s in zip(arqs_5c, sp_5c):
    ax_l.text(a, s + 0.08, f"{s:.2f}x", ha="center", color="#ffffff", fontweight="bold", fontsize=9.5)

# Right: Energia mWh (8, 24, 48, SQLite 103)
sub_e = df_e.iloc[:4]
xe = np.arange(len(sub_e))
we = 0.35
ax_r.bar(xe - we/2, sub_e["energia_solo_wh"]*1000, we, label="Solo (150W)", color="#64748b", edgecolor="#ffffff")
ax_r.bar(xe + we/2, sub_e["energia_dist_2maq_wh"]*1000, we, label="Dist 2 Nós (268,5W)", color="#00f0ff", edgecolor="#ffffff")
ax_r.set_xticks(xe)
ax_r.set_xticklabels(["8 .c", "24 .c", "48 .c", "SQLite"], fontweight="bold", fontsize=9)
ax_r.set_ylabel("Energia Consumida (mWh)")
ax_r.set_title("Consumo de Energia (mWh)", color="#ff79c6", fontsize=11)
ax_r.grid(axis="y")
ax_r.legend(facecolor="#1e293b", edgecolor="#475569", labelcolor="#ffffff", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(ASSETS_DIR, "gta_06_porte_energia.png"))
plt.close(fig)

print("Generated all GTA 6 dark/neon charts successfully.")
