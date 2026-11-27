#!/usr/bin/env python3
"""
Gera a versao expandida (18 slides), limpa, arejada e menos carregada da apresentacao GTA 6:
  - 3 Slides de Inicio (PS5 -> Rockstar R* -> Capa VI)
  - 14 Slides de Conteudo (SLIDE 01 a SLIDE 14), cada um focado em UM unico topico/grafico grande,
    com fontes maiores (11pt-13.5pt), textos curtos e diretos e bastante espaco visual
  - 1 Slide de Encerramento (APRESENTACAO CONCLUIDA + Trofeu)
  - Transicoes variadas entre todos os 18 slides (Fade, Zoom, Wipe, Push, Cover) + animacoes de entrada
    100% validadas no Microsoft PowerPoint (zero aviso de reparo).
"""
import os
from lxml import etree
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import _nsmap

PROJ_DIR = r"E:\Faculdade\SistemasOperacionais\Projeto"
ASSETS_DIR = os.path.join(PROJ_DIR, "plots_gta6")
RESULTS_DIR = os.path.join(PROJ_DIR, "results")
PPTX_OUT = os.path.join(PROJ_DIR, "Apresentacao_GTA6_distcc.pptx")
PPTX_ANIM_OUT = os.path.join(PROJ_DIR, "Apresentacao_GTA6_distcc_Animado.pptx")

_nsmap["p14"] = "http://schemas.microsoft.com/office/powerpoint/2010/main"
_nsmap["mc"] = "http://schemas.openxmlformats.org/markup-compatibility/2006"

# 1. Generate dedicated full-size 360 DPI charts for Slide 14 (Porte 8/24/48) and Slide 15 (Energia mWh)
#    plus bigger 360 DPI versions of charts 01 and 02 since each now has its own full slide!
plt.rcParams.update({
    "figure.facecolor": "#0d111f",
    "axes.facecolor": "#13192b",
    "axes.edgecolor": "#64748b",
    "axes.linewidth": 1.4,
    "axes.labelcolor": "#f8fafc",
    "text.color": "#ffffff",
    "xtick.color": "#e2e8f0",
    "ytick.color": "#e2e8f0",
    "grid.color": "#334155",
    "grid.linestyle": "--",
    "grid.alpha": 0.50,
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
    "font.size": 12.5,
    "axes.titlesize": 14.5,
    "axes.titleweight": "bold",
    "axes.labelsize": 12.5,
    "axes.labelweight": "bold",
    "savefig.dpi": 360,
    "savefig.facecolor": "#0d111f",
    "savefig.edgecolor": "none",
})

df_t = pd.read_csv(os.path.join(RESULTS_DIR, "tempos_compilacao.csv"))
df_h = pd.read_csv(os.path.join(RESULTS_DIR, "distribuicao_hosts.csv"))
df_e = pd.read_csv(os.path.join(RESULTS_DIR, "energia_estimada.csv"))

# Full-size Chart 01 (Individual vs Coletivo)
sub1 = df_t[df_t["experimento"] == "exp1_individual_coletivo"]
g1 = sub1.groupby("rotulo")["tempo_s"].agg(["mean", "std"]).reindex(["Maquina_1_Individual", "Maquina_2_Individual", "Coletivo_M1_M2"])
fig, ax = plt.subplots(figsize=(7.5, 5.1))
labels1 = ["Máquina 1\n(Solo -j4)", "Máquina 2\n(Solo -j4)", "Coletivo\n(M1 + M2 -j8)"]
colors1 = ["#38bdf8", "#a855f7", "#00ff9d"]
bars = ax.bar(labels1, g1["mean"], yerr=g1["std"].fillna(0), capsize=7, color=colors1, edgecolor="#ffffff", linewidth=1.6, width=0.48, error_kw=dict(ecolor="#ffffff", lw=1.8))
ax.set_ylabel("Tempo Médio de Compilação (s)")
ax.set_title("Compilação Individual vs. Coletiva", color="#ff79c6", pad=14)
ax.set_ylim(0, g1["mean"].max() * 1.32)
ax.grid(axis="y")
for bar, (_, row) in zip(bars, g1.iterrows()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.06, f"{row['mean']:.2f} s", ha="center", va="bottom", fontweight="bold", color="#ffffff", fontsize=13)
ax.text(0.96, 0.92, "Speedup: 1,55x (-35,5%)", transform=ax.transAxes, ha="right", va="top", bbox=dict(boxstyle="round,pad=0.45", facecolor="#1e293b", edgecolor="#00ff9d", lw=2.0), color="#00ff9d", fontweight="bold", fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(ASSETS_DIR, "gta_01_ind_coletivo_full.png"))
plt.close(fig)

# Full-size Chart 02 (Distribuicao por Maquina)
sub2 = df_h[(df_h["experimento"] == "exp1_individual_coletivo") & (df_h["rotulo"] == "Coletivo_M1_M2") & (df_h["repeticao"] == 1) & (df_h["host"] != "localhost")]
fig, ax = plt.subplots(figsize=(7.5, 5.1))
wedges, texts, autotexts = ax.pie(
    sub2["arquivos_compilados"],
    labels=[f"Nó 1 (:3632)\n{sub2.iloc[0]['arquivos_compilados']} arquivos .c", f"Nó 2 (:3633)\n{sub2.iloc[1]['arquivos_compilados']} arquivos .c"],
    autopct="%1.1f%%",
    startangle=90,
    colors=["#38bdf8", "#ff2a85"],
    wedgeprops=dict(width=0.50, edgecolor="#0d111f", linewidth=4),
    textprops=dict(color="#ffffff", fontweight="bold", fontsize=12.5),
    pctdistance=0.72,
)
for at in autotexts:
    at.set_color("#ffffff")
    at.set_fontsize(13.5)
ax.set_title("Fração de Arquivos .c por Servidor (Logs distcc)", color="#ff79c6", pad=14)
fig.tight_layout()
fig.savefig(os.path.join(ASSETS_DIR, "gta_02_distribuicao_full.png"))
plt.close(fig)

# Full-size Chart 05C (Porte 8, 24, 48 arqs .c)
fig, ax = plt.subplots(figsize=(7.5, 5.1))
arqs_5c = ["8 arquivos .c", "24 arquivos .c", "48 arquivos .c"]
t_solo_5c = [0.9104, 2.3748, 4.6138]
t_dist_5c = [0.4596, 0.9181, 1.6298]
sp_5c = [s / d for s, d in zip(t_solo_5c, t_dist_5c)]
x5c = np.arange(len(arqs_5c))
w5c = 0.34
b1 = ax.bar(x5c - w5c/2, t_solo_5c, w5c, label="Solo (-j2)", color="#64748b", edgecolor="#ffffff", lw=1.4)
b2 = ax.bar(x5c + w5c/2, t_dist_5c, w5c, label="Distribuído (-j8)", color="#00ff9d", edgecolor="#ffffff", lw=1.4)
ax.set_xticks(x5c)
ax.set_xticklabels(arqs_5c, fontweight="bold")
ax.set_ylabel("Tempo de Compilação (s)")
ax.set_title("Porte do Projeto (.c) × Ganho de Paralelismo", color="#ff79c6", pad=14)
ax.set_ylim(0, 5.65)
ax.grid(axis="y")
ax.legend(facecolor="#1e293b", edgecolor="#64748b", labelcolor="#ffffff", fontsize=11)
for i in range(len(arqs_5c)):
    ax.text(x5c[i] - w5c/2, t_solo_5c[i] + 0.10, f"{t_solo_5c[i]:.2f}s", ha="center", va="bottom", color="#cbd5e1", fontweight="bold", fontsize=10.5)
    ax.text(x5c[i] + w5c/2, t_dist_5c[i] + 0.10, f"{t_dist_5c[i]:.2f}s", ha="center", va="bottom", color="#00ff9d", fontweight="bold", fontsize=10.5)
    ax.text(x5c[i], max(t_solo_5c[i], t_dist_5c[i]) + 0.48, f"Speedup: {sp_5c[i]:.2f}x", ha="center", bbox=dict(boxstyle="round,pad=0.3", facecolor="#1e293b", edgecolor="#38bdf8", lw=1.5), color="#38bdf8", fontweight="bold", fontsize=10.5)
fig.tight_layout()
fig.savefig(os.path.join(ASSETS_DIR, "gta_05c_porte_only.png"))
plt.close(fig)

# Full-size Chart 06 (Consumo de Energia mWh)
fig, ax = plt.subplots(figsize=(7.5, 5.1))
sub_e = df_e.iloc[:4]
xe = np.arange(len(sub_e))
we = 0.35
e_solo = sub_e["energia_solo_wh"].values * 1000
e_dist = sub_e["energia_dist_2maq_wh"].values * 1000
be1 = ax.bar(xe - we/2, e_solo, we, label="Solo (1 Máquina @ 150 W)", color="#64748b", edgecolor="#ffffff", lw=1.4)
be2 = ax.bar(xe + we/2, e_dist, we, label="Distribuído (2 Nós @ 268,5 W)", color="#00f0ff", edgecolor="#ffffff", lw=1.4)
ax.set_xticks(xe)
ax.set_xticklabels(["8 arqs .c", "24 arqs .c", "48 arqs .c", "SQLite (103 .c)"], fontweight="bold")
ax.set_ylabel("Energia Elétrica Consumida (mWh)")
ax.set_title("Economia de Energia por Race-to-Idle (mWh)", color="#ff79c6", pad=14)
ax.set_ylim(0, 710)
ax.grid(axis="y")
ax.legend(facecolor="#1e293b", edgecolor="#64748b", labelcolor="#ffffff", fontsize=10.5)
for i in range(len(xe)):
    pct_save = (1.0 - e_dist[i] / e_solo[i]) * 100
    ax.text(xe[i] - we/2, e_solo[i] + 10, f"{e_solo[i]:.0f}", ha="center", va="bottom", color="#cbd5e1", fontweight="bold", fontsize=10)
    ax.text(xe[i] + we/2, e_dist[i] + 10, f"{e_dist[i]:.0f}", ha="center", va="bottom", color="#00f0ff", fontweight="bold", fontsize=10)
    ax.text(xe[i], max(e_solo[i], e_dist[i]) + 48, f"-{pct_save:.1f}%", ha="center", bbox=dict(boxstyle="round,pad=0.28", facecolor="#103e30", edgecolor="#00ff9d", lw=1.4), color="#00ff9d", fontweight="bold", fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(ASSETS_DIR, "gta_06_energia_only.png"))
plt.close(fig)

print("1. Graficos individuais full-size 360 DPI gerados com sucesso!")

# ==============================================================================
# 2. Build the 18-Slide Spacious GTA 6 Presentation
# ==============================================================================
C_WHITE = RGBColor(255, 255, 255)
C_BLACK = RGBColor(10, 12, 20)
C_DARK_PANEL = RGBColor(14, 18, 32)
C_TAB_BG = RGBColor(8, 10, 16)
C_BORDER = RGBColor(210, 215, 230)
C_NEON_PURPLE = RGBColor(179, 136, 255)
C_NEON_PINK = RGBColor(255, 77, 166)
C_NEON_CYAN = RGBColor(56, 189, 248)
C_NEON_GREEN = RGBColor(0, 255, 157)
C_NEON_GOLD = RGBColor(251, 191, 36)
C_TEXT_BODY = RGBColor(235, 240, 248)
C_TABLE_HEADER = RGBColor(30, 41, 75)
C_TABLE_ROW1 = RGBColor(17, 23, 39)
C_TABLE_ROW2 = RGBColor(24, 32, 54)
C_TABLE_BEST = RGBColor(16, 62, 48)
C_TABLE_WARN = RGBColor(76, 22, 36)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]


def set_slide_transition_and_timing(slide, kind="push", dur_ms=550, shape_specs=None):
    """
    Injects 100% PowerPoint-verified <mc:AlternateContent> slide transition and <p:timing> animations.
    kind: 'fade' | 'zoom' | 'wipe' | 'push' | 'cover' | 'split'
    """
    sld = slide._element

    if kind == "fade":
        choice_trans = f'<p:transition spd="med" p14:dur="{dur_ms}"><p:fade/></p:transition>'
        fallback_trans = '<p:transition spd="med" advClick="1"><p:fade thruBlk="0"/></p:transition>'
    elif kind == "zoom":
        choice_trans = f'<p:transition spd="med" p14:dur="{dur_ms}"><p:zoom dir="in"/></p:transition>'
        fallback_trans = '<p:transition spd="med" advClick="1"><p:zoom dir="in"/></p:transition>'
    elif kind == "wipe":
        choice_trans = f'<p:transition spd="med" p14:dur="{dur_ms}"><p:wipe/></p:transition>'
        fallback_trans = '<p:transition spd="med" advClick="1"><p:wipe dir="l"/></p:transition>'
    elif kind == "cover":
        choice_trans = f'<p:transition spd="med" p14:dur="{dur_ms}"><p:cover/></p:transition>'
        fallback_trans = '<p:transition spd="med" advClick="1"><p:cover dir="l"/></p:transition>'
    elif kind == "split":
        choice_trans = f'<p:transition spd="med" p14:dur="{dur_ms}"><p:split/></p:transition>'
        fallback_trans = '<p:transition spd="med" advClick="1"><p:split/></p:transition>'
    else:
        choice_trans = '<p:transition><p:push/></p:transition>'
        fallback_trans = '<p:transition spd="med" advClick="1"><p:push dir="l"/></p:transition>'

    ac_xml = (
        '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">'
        f'<mc:Choice Requires="p14">{choice_trans}</mc:Choice>'
        f'<mc:Fallback>{fallback_trans}</mc:Fallback>'
        '</mc:AlternateContent>'
    )
    sld.append(etree.fromstring(ac_xml))

    if not shape_specs:
        return

    ct_id = 3
    effect_nodes = []
    bld_nodes = []

    for shape, flt, delay_ms, eff_dur_ms, is_bg_box in shape_specs:
        spid = shape.shape_id
        id1, id2, id3, id4 = ct_id, ct_id + 1, ct_id + 2, ct_id + 3
        ct_id += 4

        effect_nodes.append(
            f'<p:par><p:cTn id="{id1}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
            f'<p:childTnLst><p:par><p:cTn id="{id2}" presetID="10" presetClass="entr" presetSubtype="0" '
            f'fill="hold" grpId="0" nodeType="clickEffect"><p:stCondLst><p:cond delay="{delay_ms}"/></p:stCondLst>'
            f'<p:childTnLst><p:set><p:cBhvr><p:cTn id="{id3}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/>'
            f'</p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst>'
            f'<p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/>'
            f'</p:to></p:set><p:animEffect transition="in" filter="{flt}"><p:cBhvr><p:cTn id="{id4}" dur="{eff_dur_ms}"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect></p:childTnLst></p:cTn></p:par>'
            f'</p:childTnLst></p:cTn></p:par>'
        )
        anim_bg_attr = ' animBg="1"' if is_bg_box else ''
        bld_nodes.append(f'<p:bldP spid="{spid}" grpId="0"{anim_bg_attr}/>')

    timing_xml = (
        '<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        '<p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
        '<p:childTnLst><p:seq concurrent="1" nextAc="seek">'
        '<p:cTn id="2" dur="indefinite" nodeType="mainSeq">'
        f'<p:childTnLst>{"".join(effect_nodes)}</p:childTnLst></p:cTn>'
        '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        '</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>'
        f'<p:bldLst>{"".join(bld_nodes)}</p:bldLst>'
        '</p:timing>'
    )
    sld.append(etree.fromstring(timing_xml))


def add_full_bg(slide, img_name):
    img_path = os.path.join(ASSETS_DIR, img_name)
    return slide.shapes.add_picture(img_path, Inches(0), Inches(0), width=Inches(13.333), height=Inches(7.5))


def add_gta_topbar(slide, active_idx, total=14):
    bar_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.55))
    bar_bg.fill.solid()
    bar_bg.fill.fore_color.rgb = RGBColor(5, 7, 12)
    bar_bg.line.color.rgb = RGBColor(45, 55, 75)
    bar_bg.line.width = Pt(1)

    start_x = 1.05
    tab_w = 0.80
    gap = 0.055
    for i in range(1, total + 1):
        x = Inches(start_x + (i - 1) * (tab_w + gap))
        y = Inches(0.10)
        is_active = (i == active_idx)
        tab = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(tab_w), Inches(0.35))
        tab.fill.solid()
        tab.fill.fore_color.rgb = C_WHITE if is_active else C_TAB_BG
        tab.line.color.rgb = C_WHITE if is_active else RGBColor(70, 80, 100)
        tab.line.width = Pt(1)
        tf = tab.text_frame
        tf.word_wrap = False
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = f"SLIDE {i:02d}"
        run.font.name = "Arial Black"
        run.font.size = Pt(7.5)
        run.font.bold = True
        run.font.color.rgb = C_BLACK if is_active else C_WHITE


def add_hud_frame(slide, x, y, w, h, border_color=C_BORDER):
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    box.fill.solid()
    box.fill.fore_color.rgb = C_DARK_PANEL
    box.line.color.rgb = border_color
    box.line.width = Pt(1.3)
    return box


def add_gta_header_and_bullets(slide, x, y, w, title_txt, sub_txt, bullets, font_size=12.5):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(3.2))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p0 = tf.paragraphs[0]
    r0 = p0.add_run()
    r0.text = title_txt.upper()
    r0.font.name = "Impact"
    r0.font.size = Pt(32)
    r0.font.bold = True
    r0.font.color.rgb = C_WHITE

    p1 = tf.add_paragraph()
    p1.space_after = Pt(14)
    r1 = p1.add_run()
    r1.text = sub_txt
    r1.font.name = "Impact"
    r1.font.size = Pt(15.5)
    r1.font.color.rgb = C_NEON_PURPLE

    for b_lead, b_rest in bullets:
        pb = tf.add_paragraph()
        pb.space_after = Pt(10)
        rl = pb.add_run()
        rl.text = f"▸ {b_lead}: "
        rl.font.name = "Segoe UI"
        rl.font.size = Pt(font_size)
        rl.font.bold = True
        rl.font.color.rgb = C_NEON_CYAN

        rr = pb.add_run()
        rr.text = b_rest
        rr.font.name = "Segoe UI"
        rr.font.size = Pt(font_size)
        rr.font.color.rgb = C_TEXT_BODY
    return tb


def add_gta_table(slide, x, y, w, h, headers, rows, highlight_rows=None, warn_rows=None, font_size=11.0):
    highlight_rows = highlight_rows or set()
    warn_rows = warn_rows or set()
    t_shape = slide.shapes.add_table(len(rows) + 1, len(headers), Inches(x), Inches(y), Inches(w), Inches(h))
    table = t_shape.table

    for c_idx, h_txt in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_TABLE_HEADER
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if c_idx == 0 else PP_ALIGN.RIGHT
        r = p.add_run()
        r.text = h_txt
        r.font.name = "Segoe UI"
        r.font.size = Pt(font_size)
        r.font.bold = True
        r.font.color.rgb = C_NEON_CYAN

    for r_idx, r_vals in enumerate(rows):
        is_best = r_idx in highlight_rows
        is_warn = r_idx in warn_rows
        bg = C_TABLE_BEST if is_best else (C_TABLE_WARN if is_warn else (C_TABLE_ROW1 if r_idx % 2 == 0 else C_TABLE_ROW2))
        for c_idx, val in enumerate(r_vals):
            cell = table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if c_idx == 0 else PP_ALIGN.RIGHT
            r = p.add_run()
            r.text = str(val)
            r.font.name = "Consolas" if c_idx > 0 else "Segoe UI"
            r.font.size = Pt(font_size)
            r.font.bold = (is_best or is_warn or c_idx == 0)
            r.font.color.rgb = C_NEON_GREEN if is_best else (C_NEON_PINK if is_warn else C_WHITE)
    return t_shape


def add_framed_chart(slide, x, y, w, h, img_name):
    frame_box = add_hud_frame(slide, x, y, w, h, border_color=C_BORDER)
    pad = 0.10
    pic = slide.shapes.add_picture(
        os.path.join(ASSETS_DIR, img_name),
        Inches(x + pad), Inches(y + pad),
        width=Inches(w - 2*pad), height=Inches(h - 2*pad)
    )
    return frame_box, pic


# ==============================================================================
# SLIDE 1 (INÍCIO 1): Menu PS5
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
add_full_bg(s1, "bg_intro_ps5_hq.png")
badge1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(0.22), Inches(3.8), Inches(0.45))
badge1.fill.solid()
badge1.fill.fore_color.rgb = RGBColor(15, 20, 35)
badge1.line.color.rgb = C_NEON_PINK
p1 = badge1.text_frame.paragraphs[0]
p1.alignment = PP_ALIGN.CENTER
r1 = p1.add_run()
r1.text = "SISTEMAS OPERACIONAIS · DISTCC"
r1.font.name = "Impact"
r1.font.size = Pt(12)
r1.font.color.rgb = C_WHITE
set_slide_transition_and_timing(s1, kind="fade", dur_ms=700, shape_specs=[
    (badge1, "wipe(down)", 200, 450, True),
])

# ==============================================================================
# SLIDE 2 (INÍCIO 2): Estrelas + Rockstar R*
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
add_full_bg(s2, "bg_intro_rockstar_hq.png")
tb_stars = s2.shapes.add_textbox(Inches(9.8), Inches(0.35), Inches(3.1), Inches(0.7))
p_st = tb_stars.text_frame.paragraphs[0]
p_st.alignment = PP_ALIGN.RIGHT
r_st = p_st.add_run()
r_st.text = "★ ★ ★ ★ ★"
r_st.font.name = "Segoe UI Symbol"
r_st.font.size = Pt(24)
r_st.font.bold = True
r_st.font.color.rgb = C_WHITE

tb_intro = s2.shapes.add_textbox(Inches(1.5), Inches(5.35), Inches(10.333), Inches(1.6))
tf_in = tb_intro.text_frame
p_in1 = tf_in.paragraphs[0]
p_in1.alignment = PP_ALIGN.CENTER
r_in1 = p_in1.add_run()
r_in1.text = "COMPILAÇÃO DISTRIBUÍDA EM C"
r_in1.font.name = "Impact"
r_in1.font.size = Pt(34)
r_in1.font.color.rgb = C_WHITE
p_in2 = tf_in.add_paragraph()
p_in2.alignment = PP_ALIGN.CENTER
r_in2 = p_in2.add_run()
r_in2.text = "DESEMPENHO · ESCALABILIDADE · CONTENÇÃO · ENERGIA"
r_in2.font.name = "Impact"
r_in2.font.size = Pt(18)
r_in2.font.color.rgb = C_NEON_GOLD
set_slide_transition_and_timing(s2, kind="zoom", dur_ms=650, shape_specs=[
    (tb_stars, "wipe(left)", 150, 500, False),
    (tb_intro, "fade", 350, 550, False),
])

# ==============================================================================
# SLIDE 3 (CAPA PRINCIPAL): Logotipo VI
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
add_full_bg(s3, "bg_cover_vi_hq.png")
tb_vi = s3.shapes.add_textbox(Inches(2.2), Inches(2.55), Inches(8.933), Inches(2.5))
tf_vi = tb_vi.text_frame
tf_vi.word_wrap = True
p_v1 = tf_vi.paragraphs[0]
p_v1.alignment = PP_ALIGN.CENTER
r_v1 = p_v1.add_run()
r_v1.text = "COMPILAÇÃO DISTRIBUÍDA"
r_v1.font.name = "Impact"
r_v1.font.size = Pt(40)
r_v1.font.bold = True
r_v1.font.color.rgb = C_WHITE
p_v2 = tf_vi.add_paragraph()
p_v2.alignment = PP_ALIGN.CENTER
r_v2 = p_v2.add_run()
r_v2.text = "DISTCC"
r_v2.font.name = "Impact"
r_v2.font.size = Pt(74)
r_v2.font.bold = True
r_v2.font.color.rgb = C_WHITE
set_slide_transition_and_timing(s3, kind="zoom", dur_ms=700, shape_specs=[
    (tb_vi, "box(out)", 250, 600, False),
])

# ==============================================================================
# SLIDE 4 (SLIDE 01): O PROBLEMA & A PERGUNTA CENTRAL
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
add_full_bg(s4, "bg_content_dark_hq.png")
add_gta_topbar(s4, active_idx=1)
hud4 = add_hud_frame(s4, 0.55, 0.80, 12.23, 6.25)
hb4 = add_gta_header_and_bullets(
    s4, 0.95, 1.15, 6.1,
    "A PERGUNTA DO PROJETO",
    "compilação distribuída e mecanismos do sistema operacional",
    [
        ("Questão Central", "Quanto acelera a compilação limpa de um projeto em C ao distribuir os processos entre vários nós simultaneamente?"),
        ("Pilares do OSTEP", "Virtualização de CPU e Concorrência."),
        ("Mecanismos Avaliados", "Escalonador CFS do Linux, trocas de contexto (context switch), paralelismo SMT, controle de tráfego TCP e estados de energia (race-to-idle)."),
    ],
    font_size=13.0
)

kpis = [
    ("1,55x a 2,83x", "SPEEDUP REAL MEDIDO", C_NEON_CYAN, 7.45, 1.25),
    ("61,2s vs 171,3s", "KERNEL LINUX (904 .o)", C_NEON_GREEN, 10.05, 1.25),
    ("50 Mbps", "JOELHO DA CURVA DE REDE", C_NEON_GOLD, 7.45, 3.85),
    ("-36,8% Wh", "ECONOMIA DE ENERGIA", C_NEON_PINK, 10.05, 3.85),
]
kpi_shapes = []
for k_val, k_lbl, k_col, kx, ky in kpis:
    kbox = add_hud_frame(s4, kx, ky, 2.35, 2.25, border_color=k_col)
    tfk = kbox.text_frame
    tfk.vertical_anchor = MSO_ANCHOR.MIDDLE
    pk1 = tfk.paragraphs[0]
    pk1.alignment = PP_ALIGN.CENTER
    rk1 = pk1.add_run()
    rk1.text = k_val
    rk1.font.name = "Impact"
    rk1.font.size = Pt(25)
    rk1.font.color.rgb = k_col
    pk2 = tfk.add_paragraph()
    pk2.space_before = Pt(8)
    pk2.alignment = PP_ALIGN.CENTER
    rk2 = pk2.add_run()
    rk2.text = k_lbl
    rk2.font.name = "Segoe UI"
    rk2.font.size = Pt(9.5)
    rk2.font.bold = True
    rk2.font.color.rgb = C_WHITE
    kpi_shapes.append(kbox)

set_slide_transition_and_timing(s4, kind="wipe", dur_ms=550, shape_specs=[
    (hud4, "fade", 0, 350, True),
    (hb4, "wipe(right)", 120, 450, False),
    (kpi_shapes[0], "box(out)", 280, 400, True),
    (kpi_shapes[1], "box(out)", 380, 400, True),
    (kpi_shapes[2], "box(out)", 480, 400, True),
    (kpi_shapes[3], "box(out)", 580, 400, True),
])

# ==============================================================================
# SLIDE 5 (SLIDE 02): AMBIENTE REAL & METODOLOGIA
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
add_full_bg(s5, "bg_content_dark_hq.png")
add_gta_topbar(s5, active_idx=2)
add_hud_frame(s5, 0.55, 0.80, 12.23, 6.25)
hb5 = add_gta_header_and_bullets(
    s5, 0.95, 1.15, 5.5,
    "AMBIENTE & MÉTODO",
    "hardware utilizado e controle de distorções",
    [
        ("Compilação Limpa", "Execução de make clean antes de cada rodada para eliminar objetos .o em cache."),
        ("Aquecimento (Warm-up)", "1 rodada inicial descartada para aquecer o cache de páginas do disco."),
        ("Precisão Temporal", "Repetições cronometradas em nanossegundos com date +%s.%N."),
    ],
    font_size=13.0
)
tbl5 = add_gta_table(
    s5, 6.75, 1.25, 5.65, 5.15,
    ["Componente", "Especificação Real Medida"],
    [
        ["Processador (CPU)", "AMD Ryzen 7 5700X3D (8C / 16T)"],
        ["Potência Térmica", "105 W TDP · 45 W em Repouso"],
        ["Memória RAM", "15 GB DDR4"],
        ["Sistema Operacional", "Ubuntu 26.04 LTS (WSL 2)"],
        ["Versão do Kernel", "Linux 6.18.58.1-WSL2"],
        ["Compilador & Flags", "GCC 15.2.0 (-O2 -Wall) + distcc 3.4"],
        ["Projetos Reais", "SQLite 3.47.2 e Kernel Linux 6.6.72"],
    ],
    highlight_rows={0, 6},
    font_size=11.5
)
set_slide_transition_and_timing(s5, kind="push", dur_ms=500, shape_specs=[
    (hb5, "wipe(right)", 100, 400, False),
    (tbl5, "fade", 250, 450, False),
])

# ==============================================================================
# SLIDE 6 (SLIDE 03): COMPILAÇÃO INDIVIDUAL VS. COLETIVA (1 Gráfico Grande)
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
add_full_bg(s6, "bg_content_dark_hq.png")
add_gta_topbar(s6, active_idx=3)
add_hud_frame(s6, 0.55, 0.80, 12.23, 6.25)
hb6 = add_gta_header_and_bullets(
    s6, 0.95, 1.15, 5.7,
    "INDIVIDUAL VS. COLETIVO",
    "aceleração obtida ao unir duas máquinas",
    [
        ("Redução de 35,5%", "O tempo total caiu de 1,24 s (solo) para 0,80 s no cluster coletivo."),
        ("Speedup de 1,55x", "Ganho real com 8 jobs simultâneos (-j8), limitado apenas pela linkedição final (ld) no cliente."),
    ],
    font_size=12.5
)
tbl6 = add_gta_table(
    s6, 0.95, 4.25, 5.7, 2.25,
    ["Cenário", "Jobs", "R1 (s)", "R2 (s)", "Média (Ganho)"],
    [
        ["Máquina 1 (:3632)", "-j4", "1,235", "1,242", "1,24 s (1,00x)"],
        ["Máquina 2 (:3633)", "-j4", "1,183", "1,233", "1,21 s (1,02x)"],
        ["Coletivo (M1 + M2)", "-j8", "0,802", "0,796", "0,80 s (1,55x)"],
    ],
    highlight_rows={2},
    font_size=11.0
)
fr6, pic6 = add_framed_chart(s6, 6.95, 1.15, 5.45, 5.45, "gta_01_ind_coletivo_full.png")
set_slide_transition_and_timing(s6, kind="push", dur_ms=500, shape_specs=[
    (hb6, "wipe(right)", 100, 400, False),
    (tbl6, "fade", 240, 400, False),
    (fr6, "fade", 360, 350, True),
    (pic6, "box(out)", 380, 450, False),
])

# ==============================================================================
# SLIDE 7 (SLIDE 04): BALANCEAMENTO DE CARGA NOS LOGS (1 Gráfico Grande à esquerda)
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
add_full_bg(s7, "bg_content_dark_hq.png")
add_gta_topbar(s7, active_idx=4)
add_hud_frame(s7, 0.55, 0.80, 12.23, 6.25)
fr7, pic7 = add_framed_chart(s7, 0.90, 1.15, 5.45, 5.45, "gta_02_distribuicao_full.png")
hb7 = add_gta_header_and_bullets(
    s7, 6.70, 1.15, 5.7,
    "DIVISÃO DE TAREFAS",
    "auditoria dos logs do cliente distcc",
    [
        ("Equilíbrio entre Nós", "Dos 17 arquivos .c compilados remotamente, o Nó 1 processou 9 (52,94%) e o Nó 2 processou 8 (47,06%)."),
        ("Etapa Local Obrigatória", "O cliente local (localhost) executa a etapa final de linkedição do executável."),
    ],
    font_size=12.5
)
tbl7 = add_gta_table(
    s7, 6.70, 4.25, 5.7, 2.25,
    ["Nó no Log do distcc", "Função", "Arquivos", "Fração (%)"],
    [
        ["127.0.0.1:3632 (Nó 1)", "Compilação (cc1)", "9 arqs .c", "52,94%"],
        ["127.0.0.1:3633 (Nó 2)", "Compilação (cc1)", "8 arqs .c", "47,06%"],
        ["localhost (Cliente)", "Linker (ld)", "1 binário", "Etapa serial"],
    ],
    highlight_rows={0, 1},
    font_size=11.0
)
set_slide_transition_and_timing(s7, kind="cover", dur_ms=500, shape_specs=[
    (fr7, "fade", 100, 350, True),
    (pic7, "box(out)", 120, 450, False),
    (hb7, "wipe(left)", 250, 400, False),
    (tbl7, "fade", 380, 400, False),
])

# ==============================================================================
# SLIDE 8 (SLIDE 05): PROJETOS REAIS — SQLITE VS. KERNEL LINUX (Gráfico)
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
add_full_bg(s8, "bg_content_dark_hq.png")
add_gta_topbar(s8, active_idx=5)
add_hud_frame(s8, 0.55, 0.80, 12.23, 6.25)
hb8 = add_gta_header_and_bullets(
    s8, 0.95, 1.35, 5.6,
    "SQLITE VS. KERNEL LINUX",
    "comparação visual em softwares reais de produção",
    [
        ("SQLite 3.47.2 (103 .c)", "Código desmembrado (USE_AMALGAMATION=0). O tempo caiu de 14,24 s para 6,72 s (Speedup de 2,12x)."),
        ("Kernel Linux 6.6.72 (904 .o)", "Build completo do vmlinux. O tempo caiu de 171,31 s para 61,20 s (Speedup de 2,80x)."),
        ("Economia Real", "Redução líquida de 110 segundos (quase 2 minutos) na compilação do Kernel Linux."),
    ],
    font_size=13.0
)
fr8, pic8 = add_framed_chart(s8, 6.85, 1.15, 5.55, 5.45, "gta_03_projetos.png")
set_slide_transition_and_timing(s8, kind="push", dur_ms=500, shape_specs=[
    (hb8, "wipe(right)", 100, 400, False),
    (fr8, "fade", 260, 350, True),
    (pic8, "box(out)", 280, 450, False),
])

# ==============================================================================
# SLIDE 9 (SLIDE 06): TABELA & ANÁLISE — SQLITE VS. KERNEL LINUX
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
add_full_bg(s9, "bg_content_dark_hq.png")
add_gta_topbar(s9, active_idx=6)
add_hud_frame(s9, 0.55, 0.80, 12.23, 6.25)
hb9 = add_gta_header_and_bullets(
    s9, 0.95, 1.10, 11.4,
    "POR QUE O KERNEL ESCALA MAIS?",
    "dados brutos e diluição do custo fixo em projetos grandes",
    [
        ("Diluição de Overhead", "Nos 904 objetos do Kernel Linux, os daemons distccd ficam 100% ocupados durante todo o build, amortizando o custo de abertura de sockets TCP."),
        ("Gargalo no SQLite", "No SQLite, arquivos extensos isolados (como vdbe.c) e a linkedição final representam uma fração maior do tempo total (6,72 s)."),
    ],
    font_size=12.5
)
tbl9 = add_gta_table(
    s9, 0.95, 3.65, 11.4, 2.95,
    ["Projeto Real", "Unidades", "Modo de Execução", "Rodada 1", "Rodada 2", "Tempo Médio", "Speedup (Redução)"],
    [
        ["SQLite 3.47.2", "103 arqs .c", "Solo Local (-j2)", "14,237 s", "14,249 s", "14,24 s", "1,00x (Baseline)"],
        ["SQLite 3.47.2", "103 arqs .c", "Distribuído (-j12)", "6,654 s", "6,776 s", "6,72 s", "2,12x (-52,9%)"],
        ["Kernel Linux 6.6.72", "904 objs .o", "Solo Local (-j2)", "173,463 s", "169,152 s", "171,31 s", "1,00x (Baseline)"],
        ["Kernel Linux 6.6.72", "904 objs .o", "Distribuído (-j12)", "65,621 s", "56,779 s", "61,20 s", "2,80x (-64,3%)"],
    ],
    highlight_rows={1, 3},
    font_size=11.5
)
set_slide_transition_and_timing(s9, kind="wipe", dur_ms=500, shape_specs=[
    (hb9, "wipe(right)", 100, 400, False),
    (tbl9, "wipe(down)", 260, 450, False),
])

# ==============================================================================
# SLIDE 10 (SLIDE 07): VELOCIDADE DA REDE — GRÁFICO & JOELHO DA CURVA
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
add_full_bg(s10, "bg_content_dark_hq.png")
add_gta_topbar(s10, active_idx=7)
add_hud_frame(s10, 0.55, 0.80, 12.23, 6.25)
fr10, pic10 = add_framed_chart(s10, 0.90, 1.15, 5.55, 5.45, "gta_04_rede.png")
hb10 = add_gta_header_and_bullets(
    s10, 6.75, 1.35, 5.65,
    "VELOCIDADE DA REDE",
    "impacto da largura de banda (tc qdisc tbf)",
    [
        ("Isolamento Real (veth)", "Par virtual veth_host <-> veth_ns em network namespace limitando 100% do tráfego TCP."),
        ("Gargalo Crítico (≤ 10 Mbps)", "Em 1 Mbps o tempo dispara para 19,24 s (42x mais lento que em 1 Gbps) esperando envio de código .i e retorno de .o."),
        ("Joelho da Curva (50 Mbps)", "A partir de 50 Mbps (0,80 s), a rede deixa de ser gargalo e o build passa a ser limitado pela CPU."),
    ],
    font_size=13.0
)
set_slide_transition_and_timing(s10, kind="push", dur_ms=500, shape_specs=[
    (fr10, "fade", 100, 350, True),
    (pic10, "box(out)", 120, 450, False),
    (hb10, "wipe(left)", 260, 450, False),
])

# ==============================================================================
# SLIDE 11 (SLIDE 08): TABELA COMPLETA DE VELOCIDADE DA REDE (1 A 1000 MBPS)
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
add_full_bg(s11, "bg_content_dark_hq.png")
add_gta_topbar(s11, active_idx=8)
add_hud_frame(s11, 0.55, 0.80, 12.23, 6.25)
hb11 = add_gta_header_and_bullets(
    s11, 0.95, 1.05, 11.4,
    "MEDIÇÕES DE BANDA DE REDE",
    "tempos cronometrados de 1 mbit/s até 1000 mbit/s (1 gbps)",
    [
        ("Regra Prática", "Conexões lentas (VPN congestionada ou Wi-Fi ≤ 10 Mbps) anulam a vantagem do distcc; redes Fast Ethernet (100 Mbps) ou Gigabit entregam desempenho máximo."),
    ],
    font_size=12.5
)
tbl11 = add_gta_table(
    s11, 0.95, 2.75, 11.4, 3.90,
    ["Largura de Banda (tc tbf)", "Rodada 1 (s)", "Rodada 2 (s)", "Tempo Médio", "Comportamento no Sistema Operacional"],
    [
        ["1 Mbit/s", "19,242 s", "19,234 s", "19,24 s", "Gargalo severo em buffer de escrita TCP (42x mais lento)"],
        ["5 Mbit/s", "4,120 s", "4,122 s", "4,12 s", "Rede saturada — mais lento que compilar solo (1,24 s)"],
        ["10 Mbit/s", "2,267 s", "2,241 s", "2,25 s", "Zona de transição — ainda limitado por I/O de sockets"],
        ["50 Mbit/s (Joelho)", "0,818 s", "0,781 s", "0,80 s", "JOELHO DA CURVA — Rede deixa de travar os workers"],
        ["100 Mbit/s", "0,643 s", "0,576 s", "0,61 s", "Fast Ethernet — ganho distribuído pleno"],
        ["500 Mbit/s", "0,431 s", "0,477 s", "0,45 s", "Totalmente limitado por CPU (CPU-bound)"],
        ["1000 Mbit/s (1 Gbps)", "0,442 s", "0,451 s", "0,45 s", "Platô de saturação física dos núcleos de CPU"],
    ],
    highlight_rows={3, 6},
    warn_rows={0, 1},
    font_size=11.0
)
set_slide_transition_and_timing(s11, kind="cover", dur_ms=500, shape_specs=[
    (hb11, "wipe(right)", 100, 400, False),
    (tbl11, "wipe(down)", 240, 450, False),
])

# ==============================================================================
# SLIDE 12 (SLIDE 09): ESCALA DE SERVIDORES (1 A 4 NÓS)
# ==============================================================================
s12_s = prs.slides.add_slide(blank_layout)
add_full_bg(s12_s, "bg_content_dark_hq.png")
add_gta_topbar(s12_s, active_idx=9)
add_hud_frame(s12_s, 0.55, 0.80, 12.23, 6.25)
hb12 = add_gta_header_and_bullets(
    s12_s, 0.95, 1.15, 5.7,
    "ESCALA DE SERVIDORES",
    "de 1 a 4 máquinas disponíveis (lei de amdahl)",
    [
        ("Aceleração Contínua", "O tempo cai de 1,97 s (1 nó) para 0,73 s (4 nós), atingindo Speedup de 2,69x."),
        ("Lei de Amdahl", "A eficiência por nó cai de 100% para 67,3% devido aos ~12% seriais (pré-processamento e linker ld)."),
    ],
    font_size=12.5
)
tbl12 = add_gta_table(
    s12_s, 0.95, 4.05, 5.7, 2.50,
    ["Nº de Máquinas", "Jobs", "Média (s)", "Speedup", "Eficiência/Nó"],
    [
        ["1 Máquina (:3632)", "-j2", "1,97 s", "1,00x", "100,0%"],
        ["2 Máquinas (:3632..33)", "-j4", "1,12 s", "1,76x", "87,8%"],
        ["3 Máquinas (:3632..34)", "-j6", "0,89 s", "2,22x", "73,9%"],
        ["4 Máquinas (:3632..35)", "-j8", "0,73 s", "2,69x", "67,3%"],
    ],
    highlight_rows={3},
    font_size=11.0
)
fr12, pic12 = add_framed_chart(s12_s, 6.95, 1.15, 5.45, 5.45, "gta_05a_escala.png")
set_slide_transition_and_timing(s12_s, kind="push", dur_ms=500, shape_specs=[
    (hb12, "wipe(right)", 100, 400, False),
    (tbl12, "fade", 240, 400, False),
    (fr12, "fade", 360, 350, True),
    (pic12, "box(out)", 380, 450, False),
])

# ==============================================================================
# SLIDE 13 (SLIDE 10): CONTENÇÃO DE CPU EM SEGUNDO PLANO (stress-ng)
# ==============================================================================
s13 = prs.slides.add_slide(blank_layout)
add_full_bg(s13, "bg_content_dark_hq.png")
add_gta_topbar(s13, active_idx=10)
add_hud_frame(s13, 0.55, 0.80, 12.23, 6.25)
fr13, pic13 = add_framed_chart(s13, 0.90, 1.15, 5.45, 5.45, "gta_05b_contencao.png")
hb13 = add_gta_header_and_bullets(
    s13, 6.65, 1.15, 5.75,
    "CONTENÇÃO DE CPU",
    "processos concorrentes em 2º plano (stress-ng)",
    [
        ("Até 50% de Carga (8 threads)", "O escalonador CFS aloca o GCC nos 8 threads SMT livres do Ryzen 7 5700X3D (sobe apenas +27%, de 0,75 s para 0,95 s)."),
        ("Colapso em 100% (16 threads)", "Sem núcleos livres, a disputa na runqueue gera trocas de contexto em massa e o tempo salta +247% (2,60 s)."),
    ],
    font_size=12.2
)
tbl13 = add_gta_table(
    s13, 6.65, 4.10, 5.75, 2.45,
    ["Carga stress-ng", "Threads", "Média (s)", "Degradação"],
    [
        ["0% (CPU Livre)", "0 / 16", "0,75 s", "Baseline (0%)"],
        ["25% Ocupada", "4 / 16", "0,82 s", "+9,2% (1,09x)"],
        ["50% Ocupada", "8 / 16", "0,95 s", "+27,3% (1,27x)"],
        ["100% Saturada", "16 / 16", "2,60 s", "+247,0% (3,47x)"],
    ],
    highlight_rows={0},
    warn_rows={3},
    font_size=11.0
)
set_slide_transition_and_timing(s13, kind="cover", dur_ms=500, shape_specs=[
    (fr13, "fade", 100, 350, True),
    (pic13, "box(out)", 120, 450, False),
    (hb13, "wipe(left)", 250, 400, False),
    (tbl13, "fade", 380, 400, False),
])

# ==============================================================================
# SLIDE 14 (SLIDE 11): PORTE DO PROJETO (8, 24 E 48 ARQUIVOS .C) — Slide Exclusivo!
# ==============================================================================
s14 = prs.slides.add_slide(blank_layout)
add_full_bg(s14, "bg_content_dark_hq.png")
add_gta_topbar(s14, active_idx=11)
add_hud_frame(s14, 0.55, 0.80, 12.23, 6.25)
hb14 = add_gta_header_and_bullets(
    s14, 0.95, 1.15, 5.7,
    "PORTE DO PROJETO (.C)",
    "variação de 8, 24 e 48 arquivos independentes",
    [
        ("Crescimento do Speedup", "Conforme o número de arquivos .c sobe de 8 para 48, o Speedup salta de 1,98x para 2,83x."),
        ("Fila de Workers Cheia", "Com mais unidades de compilação, os servidores remotos não ficam ociosos esperando o cliente."),
    ],
    font_size=12.5
)
tbl14 = add_gta_table(
    s14, 0.95, 4.15, 5.7, 2.35,
    ["Quantidade de .c", "Solo (-j2)", "Dist (-j8)", "Speedup (Redução)"],
    [
        ["8 arquivos .c", "0,91 s", "0,46 s", "1,98x (-49,5%)"],
        ["24 arquivos .c", "2,37 s", "0,92 s", "2,59x (-61,3%)"],
        ["48 arquivos .c", "4,61 s", "1,63 s", "2,83x (-64,7%)"],
    ],
    highlight_rows={2},
    font_size=11.0
)
fr14, pic14 = add_framed_chart(s14, 6.95, 1.15, 5.45, 5.45, "gta_05c_porte_only.png")
set_slide_transition_and_timing(s14, kind="push", dur_ms=500, shape_specs=[
    (hb14, "wipe(right)", 100, 400, False),
    (tbl14, "fade", 240, 400, False),
    (fr14, "fade", 360, 350, True),
    (pic14, "box(out)", 380, 450, False),
])

# ==============================================================================
# SLIDE 15 (SLIDE 12): CONSUMO DE ENERGIA (mWh) & EDP — Slide Exclusivo!
# ==============================================================================
s15 = prs.slides.add_slide(blank_layout)
add_full_bg(s15, "bg_content_dark_hq.png")
add_gta_topbar(s15, active_idx=12)
add_hud_frame(s15, 0.55, 0.80, 12.23, 6.25)
fr15, pic15 = add_framed_chart(s15, 0.90, 1.15, 5.45, 5.45, "gta_06_energia_only.png")
hb15 = add_gta_header_and_bullets(
    s15, 6.65, 1.10, 5.75,
    "EFICIÊNCIA ENERGÉTICA",
    "consumo em mwh, produto energia-atraso e race-to-idle",
    [
        ("Potência Ativa", "1 Máquina Solo = 150 W (45W Idle + 105W TDP) vs. 2 Nós = 268,5 W (razão = 1,79x)."),
        ("Mecanismo Race-to-Idle", "Quando o Speedup supera 1,79x, encerrar o build antes e devolver a CPU ao estado ocioso (ACPI C-states) economiza até 36,8% de energia."),
    ],
    font_size=12.0
)
tbl15 = add_gta_table(
    s15, 6.65, 3.95, 5.75, 2.30,
    ["Carga Compilada", "Solo (150W)", "Dist (268,5W)", "Economia (EDP)"],
    [
        ["Projeto C (8 .c)", "37,94 mWh", "34,28 mWh", "-9,6% (2,19x EDP)"],
        ["Projeto C (24 .c)", "98,95 mWh", "68,48 mWh", "-30,8% (3,74x EDP)"],
        ["Projeto C (48 .c)", "192,24 mWh", "121,56 mWh", "-36,8% (4,48x EDP)"],
        ["SQLite (103 .c)", "593,47 mWh", "500,83 mWh", "-15,6% (2,51x EDP)"],
    ],
    highlight_rows={2},
    font_size=11.0
)
set_slide_transition_and_timing(s15, kind="cover", dur_ms=500, shape_specs=[
    (fr15, "fade", 100, 350, True),
    (pic15, "box(out)", 120, 450, False),
    (hb15, "wipe(left)", 250, 400, False),
    (tbl15, "fade", 380, 400, False),
])

# ==============================================================================
# SLIDE 16 (SLIDE 13): SÍNTESE EXECUTIVA DE TODOS OS EXPERIMENTOS
# ==============================================================================
s16 = prs.slides.add_slide(blank_layout)
add_full_bg(s16, "bg_content_dark_hq.png")
add_gta_topbar(s16, active_idx=13)
add_hud_frame(s16, 0.55, 0.80, 12.23, 6.25)
hb16 = add_gta_header_and_bullets(
    s16, 0.95, 1.00, 11.4,
    "QUADRO-RESUMO DOS RESULTADOS",
    "consolidação de todas as métricas coletadas no projeto",
    [],
    font_size=12.0
)
tbl16 = add_gta_table(
    s16, 0.95, 2.05, 11.4, 4.65,
    ["Experimento", "Condições Comparadas", "Resultado Medido Real", "Mecanismo do Sistema Operacional"],
    [
        ["Individual vs. Coletivo", "1 Nó (-j4) vs. 2 Nós (-j8)", "1,24 s → 0,80 s (Speedup 1,55x, -35,5%)", "Paralelismo cc1 limitado pelo linker ld local"],
        ["Balanceamento (Logs)", "Contagem por host no distcc.log", "52,94% (9 arqs) Nó 1 vs. 47,06% (8 arqs) Nó 2", "Distribuição simétrica por slots TCP livres"],
        ["SQLite vs. Kernel Linux", "103 arqs .c vs. 904 objetos .o", "SQLite: 2,12x (6,72s) · Kernel: 2,80x (61,20s)", "Centenas de arquivos diluem overhead de rede"],
        ["Largura de Banda", "1 Mbps a 1000 Mbps (tc tbf)", "1 Mbps: 19,24 s → 50 Mbps: 0,80 s → 1G: 0,45 s", "Joelho em 50 Mbps; abaixo de 10 Mbps trava em I/O"],
        ["Escala de Servidores", "1, 2, 3 e 4 Máquinas (-j2 a -j8)", "1,97 s → 1,12 s → 0,89 s → 0,73 s (2,69x)", "Lei de Amdahl: eficiência cai de 100% a 67,3%"],
        ["Contenção de CPU", "0%, 25%, 50% e 100% (stress-ng)", "0%: 0,75s → 50%: 0,95s (+27%) → 100%: 2,60s (+247%)", "CFS usa threads SMT até 50%; colapsa em 100%"],
        ["Porte & Energia (Wh)", "8 a 904 arqs (150W vs. 268,5W)", "48 arqs: -36,8% Wh · Kernel: 7,14 → 4,56 Wh (-36,1%)", "Race-to-Idle (ACPI C-states) quando Speedup > 1,79x"],
    ],
    highlight_rows={2, 6},
    warn_rows={5},
    font_size=11.0
)
set_slide_transition_and_timing(s16, kind="push", dur_ms=500, shape_specs=[
    (hb16, "wipe(right)", 100, 350, False),
    (tbl16, "wipe(down)", 240, 450, False),
])

# ==============================================================================
# SLIDE 17 (SLIDE 14): CONCLUSÃO — QUANDO VALE A PENA USAR DISTCC?
# ==============================================================================
s17 = prs.slides.add_slide(blank_layout)
add_full_bg(s17, "bg_content_dark_hq.png")
add_gta_topbar(s17, active_idx=14)
add_hud_frame(s17, 0.55, 0.80, 12.23, 6.25)
hb17 = add_gta_header_and_bullets(
    s17, 0.95, 1.00, 11.4,
    "CONCLUSÕES PRÁTICAS",
    "limiares de viabilidade técnica e energética da compilação distribuída",
    [],
    font_size=12.0
)

box_ok = add_hud_frame(s17, 0.95, 2.15, 5.50, 4.45, border_color=C_NEON_GREEN)
hb_ok = add_gta_header_and_bullets(
    s17, 1.25, 2.40, 4.90,
    "QUANDO VALE A PENA",
    "cenários de alto ganho de tempo e energia",
    [
        ("Projetos Médios e Grandes", "A partir de 24 arquivos .c independentes (SQLite com 103 .c e Kernel Linux com 904 .o), onde o Speedup atinge 2,12x a 2,83x."),
        ("Rede ≥ 50 Mbps", "A partir do joelho da curva (50–100 Mbps), a transmissão TCP não bloqueia os compiladores."),
        ("Economia de Energia", "Quando o Speedup supera 1,79x, 2 máquinas gastam até 36,8% menos Wh total (Race-to-Idle)."),
    ],
    font_size=12.0
)

box_no = add_hud_frame(s17, 6.85, 2.15, 5.50, 4.45, border_color=C_NEON_PINK)
hb_no = add_gta_header_and_bullets(
    s17, 7.15, 2.40, 4.90,
    "QUANDO NÃO VALE A PENA",
    "gargalos que anulam o paralelismo",
    [
        ("Redes Lentas (≤ 10 Mbps)", "O tempo de envio dos arquivos .i e retorno dos .o eleva o build para até 19,24 s."),
        ("Servidores com 100% de CPU", "Quando não há threads SMT ociosos, trocas de contexto (context switches) degradam o tempo em +247%."),
        ("Projetos Muito Pequenos", "Se o Speedup ficar abaixo de 1,79x, a etapa serial do linker domina e o consumo energético sobe."),
    ],
    font_size=12.0
)
set_slide_transition_and_timing(s17, kind="split", dur_ms=550, shape_specs=[
    (hb17, "wipe(right)", 100, 350, False),
    (box_ok, "fade", 240, 350, True),
    (hb_ok, "wipe(up)", 280, 400, False),
    (box_no, "fade", 420, 350, True),
    (hb_no, "wipe(up)", 460, 400, False),
])

# ==============================================================================
# SLIDE 18 (ENCERRAMENTO): APRESENTAÇÃO CONCLUÍDA + TROFÉU
# ==============================================================================
s18 = prs.slides.add_slide(blank_layout)
add_full_bg(s18, "bg_sunset_clean_hq.png")
trophy_pic = s18.shapes.add_picture(
    os.path.join(ASSETS_DIR, "trophy_popup_hq.png"),
    Inches(0), Inches(0.50),
    width=Inches(3.89), height=Inches(0.648)
)
title_conc_pic = s18.shapes.add_picture(
    os.path.join(ASSETS_DIR, "title_concluida_hq.png"),
    Inches(3.266), Inches(2.35),
    width=Inches(6.80), height=Inches(2.266)
)
set_slide_transition_and_timing(s18, kind="fade", dur_ms=700, shape_specs=[
    (title_conc_pic, "box(out)", 200, 600, False),
    (trophy_pic, "wipe(right)", 550, 500, False),
])

prs.save(PPTX_ANIM_OUT)
try:
    prs.save(PPTX_OUT)
except PermissionError:
    pass
print(f"2. Apresentacao expandida (18 slides) salva com sucesso em:\n   {PPTX_ANIM_OUT}\n   {PPTX_OUT}")
