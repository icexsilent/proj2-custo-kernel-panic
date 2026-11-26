#!/usr/bin/env python3
"""
Gera a apresentacao no estilo GTA 6 (baseado no video de referencia),
SEM os slides de nomes de integrantes, contendo:
  - O Inicio (Tela PS5 -> Tela Estrelas/Rockstar -> Capa Principal Logotipo VI)
  - Os Slides de Conteudo (SLIDE 01 a SLIDE 08 no layout de Menu Pause do GTA 6 com tabelas e graficos)
  - O Encerramento ("APRESENTACAO CONCLUIDA" + Trofeu)
Inclui:
  1) Transicoes de slide nativas do PowerPoint (<p:transition> com Fade, Zoom e Push horizontal estilo Menu GTA)
  2) Animacoes automaticas de entrada em cascata (<p:timing>) para os elementos de cada slide (titulos, tabelas, graficos, KPIs e trofeu)
"""
import os
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn, _nsmap

ROOT_DIR = "/mnt/e/Faculdade/SistemasOperacionais"
ASSETS_DIR = os.path.join(ROOT_DIR, "plots_gta6")
PPTX_OUT = os.path.join(ROOT_DIR, "Apresentacao_GTA6_distcc.pptx")

# Register p14 and mc namespaces for modern PowerPoint transition durations
_nsmap["p14"] = "http://schemas.microsoft.com/office/powerpoint/2010/main"
_nsmap["mc"] = "http://schemas.openxmlformats.org/markup-compatibility/2006"

# Colors matching the GTA 6 PowerPoint template video
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
C_TEXT_BODY = RGBColor(230, 234, 242)
C_TABLE_HEADER = RGBColor(30, 41, 75)
C_TABLE_ROW1 = RGBColor(17, 23, 39)
C_TABLE_ROW2 = RGBColor(24, 32, 54)
C_TABLE_BEST = RGBColor(16, 62, 48)
C_TABLE_WARN = RGBColor(76, 22, 36)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]


def set_slide_transition(slide, kind="push", dir_attr="l", spd="med", dur_ms=550):
    """
    Injects standard OpenXML <p:transition> (wrapped with mc:AlternateContent for p14:dur)
    into the slide XML so PowerPoint 2016/2019/2021/365/Online and LibreOffice animate transitions.
    kind: 'fade' | 'zoom' | 'push' | 'wipe' | 'cover'
    """
    sld = slide._element
    # Remove any existing transition or timing before adding
    for old in sld.findall(qn("p:transition")):
        sld.remove(old)
    for old in sld.findall(qn("mc:AlternateContent")):
        sld.remove(old)

    if kind == "fade":
        inner_xml = '<p:fade thruBlk="0"/>'
    elif kind == "zoom":
        inner_xml = f'<p:zoom dir="{dir_attr}"/>'
    elif kind == "push":
        inner_xml = f'<p:push dir="{dir_attr}"/>'
    elif kind == "wipe":
        inner_xml = f'<p:wipe dir="{dir_attr}"/>'
    else:
        inner_xml = f'<p:cover dir="{dir_attr}"/>'

    ac_xml = f"""
    <mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
                         xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                         xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">
      <mc:Choice Requires="p14">
        <p:transition spd="{spd}" advClick="1" p14:dur="{dur_ms}">
          {inner_xml}
        </p:transition>
      </mc:Choice>
      <mc:Fallback>
        <p:transition spd="{spd}" advClick="1">
          {inner_xml}
        </p:transition>
      </mc:Fallback>
    </mc:AlternateContent>
    """
    ac_el = etree.fromstring(ac_xml.strip())

    # In <p:sld>, <p:transition> (or AlternateContent) must appear after <p:clrMapOvr> (or <p:cSld>) and before <p:timing>
    timing_el = sld.find(qn("p:timing"))
    if timing_el is not None:
        sld.insert(sld.index(timing_el), ac_el)
    else:
        sld.append(ac_el)


def add_auto_entrance_animations(slide, shape_specs):
    """
    Adds automatic staggered entrance animations (<p:timing>) to the given shapes on the slide.
    shape_specs: list of tuples (shape, filter_str, delay_ms, dur_ms)
      where filter_str can be:
        'fade'
        'wipe(right)' | 'wipe(down)' | 'wipe(left)' | 'wipe(up)'
        'barn(inVertical)' | 'box(out)'
    All shapes animate automatically upon entering the slide (afterPrevious / withPrevious),
    so the presenter does NOT need extra clicks for each element.
    """
    if not shape_specs:
        return

    sld = slide._element
    for old in sld.findall(qn("p:timing")):
        sld.remove(old)

    ct_id = 3
    effect_nodes = []
    bld_nodes = []

    for idx, (shape, flt, delay_ms, dur_ms) in enumerate(shape_specs):
        spid = shape.shape_id
        node_type = "afterPrevious" if idx == 0 else "withPrevious"
        par_id1 = ct_id
        par_id2 = ct_id + 1
        set_id = ct_id + 2
        set_bhv_id = ct_id + 3
        anim_id = ct_id + 4
        anim_bhv_id = ct_id + 5
        ct_id += 6

        effect_nodes.append(f"""
        <p:par>
          <p:cTn id="{par_id1}" fill="hold">
            <p:stCondLst>
              <p:cond delay="0"/>
            </p:stCondLst>
            <p:childTnLst>
              <p:par>
                <p:cTn id="{par_id2}" presetID="10" presetClass="entr" presetSubtype="0" fill="hold" grpId="0" nodeType="{node_type}">
                  <p:stCondLst>
                    <p:cond delay="{delay_ms}"/>
                  </p:stCondLst>
                  <p:childTnLst>
                    <p:set>
                      <p:cBhvr>
                        <p:cTn id="{set_id}" dur="1" fill="hold">
                          <p:stCondLst>
                            <p:cond delay="0"/>
                          </p:stCondLst>
                        </p:cTn>
                        <p:tgtEl>
                          <p:spTgt spid="{spid}"/>
                        </p:tgtEl>
                        <p:attrNameLst>
                          <p:attrName>style.visibility</p:attrName>
                        </p:attrNameLst>
                      </p:cBhvr>
                      <p:to>
                        <p:strVal val="visible"/>
                      </p:to>
                    </p:set>
                    <p:animEffect transition="in" filter="{flt}">
                      <p:cBhvr>
                        <p:cTn id="{anim_id}" dur="{dur_ms}"/>
                        <p:tgtEl>
                          <p:spTgt spid="{spid}"/>
                        </p:tgtEl>
                      </p:cBhvr>
                    </p:animEffect>
                  </p:childTnLst>
                </p:cTn>
              </p:par>
            </p:childTnLst>
          </p:cTn>
        </p:par>
        """)
        bld_nodes.append(f'<p:bldP spid="{spid}" grpId="0"/>')

    timing_xml = f"""
    <p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
      <p:tnLst>
        <p:par>
          <p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">
            <p:childTnLst>
              <p:seq concurrent="1" nextAc="seek">
                <p:cTn id="2" dur="indefinite" nodeType="mainSeq">
                  <p:childTnLst>
                    {''.join(effect_nodes)}
                  </p:childTnLst>
                </p:cTn>
                <p:prevCondLst>
                  <p:cond evt="onPrev" delay="0">
                    <p:tgtEl><p:sldTgt/></p:tgtEl>
                  </p:cond>
                </p:prevCondLst>
                <p:nextCondLst>
                  <p:cond evt="onNext" delay="0">
                    <p:tgtEl><p:sldTgt/></p:tgtEl>
                  </p:cond>
                </p:nextCondLst>
              </p:seq>
            </p:childTnLst>
          </p:cTn>
        </p:par>
      </p:tnLst>
      <p:bldLst>
        {''.join(bld_nodes)}
      </p:bldLst>
    </p:timing>
    """
    sld.append(etree.fromstring(timing_xml.strip()))


def add_full_bg(slide, img_name):
    img_path = os.path.join(ASSETS_DIR, img_name)
    return slide.shapes.add_picture(img_path, Inches(0), Inches(0), width=Inches(13.333), height=Inches(7.5))


def add_gta_topbar(slide, active_idx, total=8):
    """Draws the GTA Pause Menu top navigation bar with SLIDE 01 .. SLIDE 08 tabs."""
    bar_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.55))
    bar_bg.fill.solid()
    bar_bg.fill.fore_color.rgb = RGBColor(5, 7, 12)
    bar_bg.line.color.rgb = RGBColor(45, 55, 75)
    bar_bg.line.width = Pt(1)

    start_x = 4.25
    tab_w = 1.05
    gap = 0.07
    active_tab_shape = None
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
        run.font.size = Pt(8.5)
        run.font.bold = True
        run.font.color.rgb = C_BLACK if is_active else C_WHITE
        if is_active:
            active_tab_shape = tab
    return active_tab_shape


def add_hud_frame(slide, x, y, w, h, border_color=C_BORDER):
    """Adds a dark GTA pause-menu frame box with thin border."""
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    box.fill.solid()
    box.fill.fore_color.rgb = C_DARK_PANEL
    box.line.color.rgb = border_color
    box.line.width = Pt(1.2)
    return box


def add_gta_header_and_bullets(slide, x, y, w, title_txt, sub_txt, bullets):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(2.6))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p0 = tf.paragraphs[0]
    r0 = p0.add_run()
    r0.text = title_txt.upper()
    r0.font.name = "Impact"
    r0.font.size = Pt(28)
    r0.font.bold = True
    r0.font.color.rgb = C_WHITE

    p1 = tf.add_paragraph()
    p1.space_after = Pt(8)
    r1 = p1.add_run()
    r1.text = sub_txt
    r1.font.name = "Impact"
    r1.font.size = Pt(14)
    r1.font.color.rgb = C_NEON_PURPLE

    for b_lead, b_rest in bullets:
        pb = tf.add_paragraph()
        pb.space_after = Pt(5)
        rl = pb.add_run()
        rl.text = f"▸ {b_lead}: "
        rl.font.name = "Segoe UI"
        rl.font.size = Pt(10.5)
        rl.font.bold = True
        rl.font.color.rgb = C_NEON_CYAN

        rr = pb.add_run()
        rr.text = b_rest
        rr.font.name = "Segoe UI"
        rr.font.size = Pt(10.5)
        rr.font.color.rgb = C_TEXT_BODY
    return tb


def add_gta_table(slide, x, y, w, h, headers, rows, highlight_rows=None, warn_rows=None):
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
        r.font.size = Pt(9.5)
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
            r.font.size = Pt(9.2)
            r.font.bold = (is_best or is_warn or c_idx == 0)
            r.font.color.rgb = C_NEON_GREEN if is_best else (C_NEON_PINK if is_warn else C_WHITE)
    return t_shape


def add_framed_chart(slide, x, y, w, h, img_name):
    frame_box = add_hud_frame(slide, x, y, w, h, border_color=C_BORDER)
    pad = 0.08
    pic = slide.shapes.add_picture(
        os.path.join(ASSETS_DIR, img_name),
        Inches(x + pad), Inches(y + pad),
        width=Inches(w - 2*pad), height=Inches(h - 2*pad)
    )
    return frame_box, pic


# ==============================================================================
# SLIDE 1 (INÍCIO 1): PS5 Dashboard — Selecting Grand Theft Auto VI ("Start")
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
add_full_bg(s1, "bg_intro_ps5.jpg")
badge1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(0.22), Inches(3.8), Inches(0.45))
badge1.fill.solid()
badge1.fill.fore_color.rgb = RGBColor(15, 20, 35)
badge1.line.color.rgb = C_NEON_PINK
tf1 = badge1.text_frame
p1 = tf1.paragraphs[0]
p1.alignment = PP_ALIGN.CENTER
r1 = p1.add_run()
r1.text = "SISTEMAS OPERACIONAIS · DISTCC"
r1.font.name = "Impact"
r1.font.size = Pt(12)
r1.font.color.rgb = C_WHITE

set_slide_transition(s1, kind="fade", spd="med", dur_ms=700)
add_auto_entrance_animations(s1, [
    (badge1, "wipe(down)", 200, 450),
])

# ==============================================================================
# SLIDE 2 (INÍCIO 2): Estrelas de Procurado + Rockstar Siren Intro
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
add_full_bg(s2, "bg_intro_rockstar.jpg")
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

set_slide_transition(s2, kind="zoom", dir_attr="in", spd="med", dur_ms=650)
add_auto_entrance_animations(s2, [
    (tb_stars, "wipe(left)", 150, 500),
    (tb_intro, "fade", 350, 550),
])

# ==============================================================================
# SLIDE 3 (CAPA PRINCIPAL): Logotipo VI sobre Vice City Sunset (sem nomes!)
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
add_full_bg(s3, "bg_cover_vi.jpg")
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

set_slide_transition(s3, kind="zoom", dir_attr="in", spd="med", dur_ms=750)
add_auto_entrance_animations(s3, [
    (tb_vi, "box(out)", 250, 600),
])

# ==============================================================================
# SLIDE 4 (SLIDE 01): AMBIENTE REAL & METODOLOGIA
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
add_full_bg(s4, "bg_content_dark.jpg")
tab4 = add_gta_topbar(s4, active_idx=1, total=8)
hud4 = add_hud_frame(s4, 0.55, 0.80, 12.23, 6.25)

hb4 = add_gta_header_and_bullets(
    s4, 0.90, 1.05, 5.8,
    "AMBIENTE & METODOLOGIA",
    "hardware real, ferramentas e controle experimental",
    [
        ("Pergunta Central", "Quanto acelera a compilação limpa em C ao distribuir processos entre múltiplos nós, e onde estão os limites de rede, CPU e energia?"),
        ("Mecanismos do SO", "Escalonador CFS do Linux, trocas de contexto (context switch), paralelismo SMT, shaping TCP (tc qdisc tbf) e estados de energia (race-to-idle)."),
        ("Rigor de Medição", "make clean antes de cada rodada + 1 warm-up descartado + repetições cronometradas via date +%s.%N com GCC 15.2.0 (-O2 -Wall)."),
    ]
)

tbl4 = add_gta_table(
    s4, 6.95, 1.10, 5.45, 3.35,
    ["Componente / Parâmetro", "Especificação Real Medida"],
    [
        ["Processador (CPU)", "AMD Ryzen 7 5700X3D (8C / 16T)"],
        ["Envelope Térmico", "105 W TDP · 45 W Repouso (Idle)"],
        ["Memória & Sistema", "15 GB DDR4 · Ubuntu 26.04 (WSL 2)"],
        ["Kernel Linux", "6.18.58.1-microsoft-standard-WSL2"],
        ["Compilador & Cluster", "GCC 15.2.0 (-O2) + distcc 3.4"],
        ["Projetos Reais Testados", "SQLite 3.47.2 (103 .c) e Linux 6.6.72"],
    ],
    highlight_rows={0, 5}
)

kpis = [
    ("1,55x a 2,83x", "SPEEDUP ALCANÇADO", C_NEON_CYAN),
    ("61,2s vs 171,3s", "KERNEL LINUX (904 .o)", C_NEON_GREEN),
    ("50 Mbps", "JOELHO DA REDE", C_NEON_GOLD),
    ("-36,8% Wh", "ECONOMIA DE ENERGIA", C_NEON_PINK),
]
kpi_shapes = []
for idx, (k_val, k_lbl, k_col) in enumerate(kpis):
    kx = 0.90 + idx * 2.95
    ky = 5.15
    kbox = add_hud_frame(s4, kx, ky, 2.75, 1.45, border_color=k_col)
    tfk = kbox.text_frame
    tfk.vertical_anchor = MSO_ANCHOR.MIDDLE
    pk1 = tfk.paragraphs[0]
    pk1.alignment = PP_ALIGN.CENTER
    rk1 = pk1.add_run()
    rk1.text = k_val
    rk1.font.name = "Impact"
    rk1.font.size = Pt(24)
    rk1.font.color.rgb = k_col
    pk2 = tfk.add_paragraph()
    pk2.alignment = PP_ALIGN.CENTER
    rk2 = pk2.add_run()
    rk2.text = k_lbl
    rk2.font.name = "Segoe UI"
    rk2.font.size = Pt(9)
    rk2.font.bold = True
    rk2.font.color.rgb = C_WHITE
    kpi_shapes.append(kbox)

set_slide_transition(s4, kind="wipe", dir_attr="l", spd="med", dur_ms=550)
add_auto_entrance_animations(s4, [
    (hud4, "fade", 0, 350),
    (hb4, "wipe(right)", 120, 450),
    (tbl4, "fade", 260, 450),
    (kpi_shapes[0], "wipe(up)", 380, 350),
    (kpi_shapes[1], "wipe(up)", 460, 350),
    (kpi_shapes[2], "wipe(up)", 540, 350),
    (kpi_shapes[3], "wipe(up)", 620, 350),
])

# ==============================================================================
# SLIDE 5 (SLIDE 02): INDIVIDUAL VS. COLETIVO & DISTRIBUIÇÃO (2 quadros à direita)
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
add_full_bg(s5, "bg_content_dark.jpg")
add_gta_topbar(s5, active_idx=2, total=8)
hud5 = add_hud_frame(s5, 0.55, 0.80, 12.23, 6.25)

hb5 = add_gta_header_and_bullets(
    s5, 0.90, 1.00, 6.1,
    "INDIVIDUAL VS. COLETIVO",
    "ganho de paralelismo e balanceamento nos logs",
    [
        ("Aceleração Coletiva", "Unir os 2 servidores reduziu o tempo de 1,24 s para 0,80 s (Speedup de 1,55x e redução de 35,5% no tempo)."),
        ("Divisão Simétrica", "Nos logs (/tmp/distcc-client.log), o Nó 1 compilou 9 arquivos (52,94%) e o Nó 2 compilou 8 arquivos (47,06%)."),
        ("Limite Serial (Amdahl)", "A linkedição final do binário (ld) ocorre sempre na máquina cliente local."),
    ]
)

tbl5 = add_gta_table(
    s5, 0.90, 3.85, 6.1, 2.85,
    ["Cenário / Servidor", "Jobs", "R1 (s)", "R2 (s)", "Média / Fração"],
    [
        ["Máquina 1 Individual (:3632)", "-j4", "1,235", "1,242", "1,24 s (1,00x)"],
        ["Máquina 2 Individual (:3633)", "-j4", "1,183", "1,233", "1,21 s (1,02x)"],
        ["Coletivo (Máq. 1 + Máq. 2)", "-j8", "0,802", "0,796", "0,80 s (1,55x)"],
        ["Log Nó 1 (127.0.0.1:3632)", "cc1", "9 arqs", "9 arqs", "52,94% dos .c"],
        ["Log Nó 2 (127.0.0.1:3633)", "cc1", "8 arqs", "8 arqs", "47,06% dos .c"],
    ],
    highlight_rows={2}
)

fr5a, pic5a = add_framed_chart(s5, 7.30, 1.00, 5.15, 2.82, "gta_01_ind_coletivo.png")
fr5b, pic5b = add_framed_chart(s5, 7.30, 3.98, 5.15, 2.82, "gta_02_distribuicao.png")

set_slide_transition(s5, kind="push", dir_attr="l", spd="med", dur_ms=500)
add_auto_entrance_animations(s5, [
    (hb5, "wipe(right)", 100, 400),
    (tbl5, "fade", 240, 400),
    (fr5a, "fade", 360, 350),
    (pic5a, "box(out)", 380, 450),
    (fr5b, "fade", 480, 350),
    (pic5b, "box(out)", 500, 450),
])

# ==============================================================================
# SLIDE 6 (SLIDE 03): PROJETOS REAIS — SQLITE VS. KERNEL LINUX (Quadro à direita)
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
add_full_bg(s6, "bg_content_dark.jpg")
add_gta_topbar(s6, active_idx=3, total=8)
hud6 = add_hud_frame(s6, 0.55, 0.80, 12.23, 6.25)

hb6 = add_gta_header_and_bullets(
    s6, 0.90, 1.00, 6.0,
    "SQLITE VS. KERNEL LINUX",
    "cargas reais de código aberto de diferentes portes",
    [
        ("SQLite 3.47.2 (103 .c)", "Compilado de forma desmembrada (USE_AMALGAMATION=0); o tempo caiu de 14,24 s para 6,72 s (Speedup de 2,12x / -52,9%)."),
        ("Kernel Linux 6.6.72 (904 .o)", "Compilação completa do vmlinux; o tempo caiu de 171,31 s (~2m51s) para 61,20 s (~1m01s), economizando 110 segundos (2,80x)."),
        ("Por que o Kernel escala mais?", "Os 904 objetos mantêm todos os workers 100% ocupados e diluem o custo fixo de rede e linkedição."),
    ]
)

tbl6 = add_gta_table(
    s6, 0.90, 4.10, 6.0, 2.55,
    ["Projeto Real", "Porte", "Modo", "R1 (s)", "R2 (s)", "Média (Speedup)"],
    [
        ["SQLite 3.47.2", "103 .c", "Solo (-j2)", "14,24", "14,25", "14,24 s (1,00x)"],
        ["SQLite 3.47.2", "103 .c", "Dist (-j12)", "6,65", "6,78", "6,72 s (2,12x)"],
        ["Linux 6.6.72", "904 .o", "Solo (-j2)", "173,46", "169,15", "171,31 s (1,00x)"],
        ["Linux 6.6.72", "904 .o", "Dist (-j12)", "65,62", "56,78", "61,20 s (2,80x)"],
    ],
    highlight_rows={1, 3}
)

fr6, pic6 = add_framed_chart(s6, 7.20, 1.10, 5.25, 5.55, "gta_03_projetos.png")

set_slide_transition(s6, kind="push", dir_attr="l", spd="med", dur_ms=500)
add_auto_entrance_animations(s6, [
    (hb6, "wipe(right)", 100, 400),
    (tbl6, "fade", 250, 400),
    (fr6, "fade", 380, 350),
    (pic6, "box(out)", 400, 450),
])

# ==============================================================================
# SLIDE 7 (SLIDE 04): LARGURA DE BANDA DA REDE (Quadro à esquerda, Texto à direita)
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
add_full_bg(s7, "bg_content_dark.jpg")
add_gta_topbar(s7, active_idx=4, total=8)
hud7 = add_hud_frame(s7, 0.55, 0.80, 12.23, 6.25)

fr7, pic7 = add_framed_chart(s7, 0.85, 1.10, 5.25, 5.55, "gta_04_rede.png")

hb7 = add_gta_header_and_bullets(
    s7, 6.40, 1.00, 6.05,
    "VELOCIDADE DA REDE",
    "controle de tráfego real via tc qdisc tbf (1 a 1000 mbps)",
    [
        ("Isolamento em Namespace", "Par virtual veth_host <-> veth_ns em ip netns limitando 100% dos bytes TCP dos arquivos pré-processados (.i) e objetos (.o)."),
        ("Gargalo Severo (≤ 10 Mbps)", "Em 1 Mbps o build leva 19,24 s (42x mais lento que em 1 Gbps) devido ao bloqueio de escrita nos sockets TCP."),
        ("Joelho da Curva (50 Mbps)", "A partir de 50 Mbps (0,80 s) e 100 Mbps (0,61 s), a rede deixa de travar os compiladores e o processo torna-se CPU-bound."),
    ]
)

tbl7 = add_gta_table(
    s7, 6.40, 3.85, 6.05, 2.85,
    ["Banda Limitada", "R1 (s)", "R2 (s)", "Média (s)", "Regime de Operação"],
    [
        ["1 Mbit/s", "19,242", "19,234", "19,24 s", "Gargalo severo (42x mais lento)"],
        ["5 Mbit/s", "4,120", "4,122", "4,12 s", "Rede saturada (pior que solo)"],
        ["10 Mbit/s", "2,267", "2,241", "2,25 s", "Transição limitada por I/O TCP"],
        ["50 Mbit/s", "0,818", "0,781", "0,80 s", "JOELHO DA CURVA (Ponto ideal)"],
        ["100 Mbit/s", "0,643", "0,576", "0,61 s", "Fast Ethernet — ganho pleno"],
        ["500 / 1000 Mbps", "0,442", "0,451", "0,45 s", "Platô de saturação da CPU"],
    ],
    highlight_rows={3, 5},
    warn_rows={0, 1}
)

set_slide_transition(s7, kind="push", dir_attr="l", spd="med", dur_ms=500)
add_auto_entrance_animations(s7, [
    (fr7, "fade", 100, 350),
    (pic7, "box(out)", 120, 450),
    (hb7, "wipe(left)", 250, 400),
    (tbl7, "fade", 380, 400),
])

# ==============================================================================
# SLIDE 8 (SLIDE 05): ESCALABILIDADE DE SERVIDORES (1 A 4 NÓS)
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
add_full_bg(s8, "bg_content_dark.jpg")
add_gta_topbar(s8, active_idx=5, total=8)
hud8 = add_hud_frame(s8, 0.55, 0.80, 12.23, 6.25)

hb8 = add_gta_header_and_bullets(
    s8, 0.90, 1.00, 6.0,
    "ESCALA DE SERVIDORES",
    "variação de 1 a 4 máquinas disponíveis (lei de amdahl)",
    [
        ("Escala Horizontal (2 jobs/nó)", "O tempo cai continuamente de 1,97 s (1 nó) para 1,12 s (2 nós), 0,89 s (3 nós) e 0,73 s (4 nós)."),
        ("Speedup vs. Eficiência", "Em 4 máquinas o Speedup chega a 2,69x, porém a eficiência por nó recua de 100% para 67,3%."),
        ("Explicação no SO", "A fração não-paralelizável (~12% do tempo gasta no pré-processador cpp, envio TCP e linker ld) impõe o teto sublinear da Lei de Amdahl."),
    ]
)

tbl8 = add_gta_table(
    s8, 0.90, 4.05, 6.0, 2.60,
    ["Servidores distccd", "Jobs", "R1 (s)", "R2 (s)", "Média", "Speedup (Efic.)"],
    [
        ["1 Máquina (:3632)", "-j2", "1,986", "1,964", "1,97 s", "1,00x (100,0%)"],
        ["2 Máquinas (:3632..33)", "-j4", "1,131", "1,119", "1,12 s", "1,76x (87,8%)"],
        ["3 Máquinas (:3632..34)", "-j6", "0,912", "0,870", "0,89 s", "2,22x (73,9%)"],
        ["4 Máquinas (:3632..35)", "-j8", "0,730", "0,738", "0,73 s", "2,69x (67,3%)"],
    ],
    highlight_rows={3}
)

fr8, pic8 = add_framed_chart(s8, 7.20, 1.10, 5.25, 5.55, "gta_05a_escala.png")

set_slide_transition(s8, kind="push", dir_attr="l", spd="med", dur_ms=500)
add_auto_entrance_animations(s8, [
    (hb8, "wipe(right)", 100, 400),
    (tbl8, "fade", 250, 400),
    (fr8, "fade", 380, 350),
    (pic8, "box(out)", 400, 450),
])

# ==============================================================================
# SLIDE 9 (SLIDE 06): CONTENÇÃO DE PROCESSOS EM 2º PLANO (Quadro à esquerda)
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
add_full_bg(s9, "bg_content_dark.jpg")
add_gta_topbar(s9, active_idx=6, total=8)
hud9 = add_hud_frame(s9, 0.55, 0.80, 12.23, 6.25)

fr9, pic9 = add_framed_chart(s9, 0.85, 1.10, 5.25, 5.55, "gta_05b_contencao.png")

hb9 = add_gta_header_and_bullets(
    s9, 6.40, 1.00, 6.05,
    "CONTENÇÃO DE CPU",
    "processos concorrentes em segundo plano (stress-ng)",
    [
        ("Regime Tolerante (0% a 50%)", "Com 4 threads (25%) e 8 threads (50%) do stress-ng, o tempo sobe apenas de 0,75 s para 0,82 s (+9%) e 0,95 s (+27%)."),
        ("Atuação do Escalonador CFS", "Como o Ryzen 7 5700X3D possui 16 threads lógicos (SMT), o CFS aloca os processos cc1 do GCC nos 8 threads ainda ociosos."),
        ("Colapso em 100% (16 threads)", "Com todos os 16 threads saturados, a disputa na runqueue gera trocas de contexto (context switches) em massa e o tempo salta +247% (2,60 s)."),
    ]
)

tbl9 = add_gta_table(
    s9, 6.40, 4.05, 6.05, 2.60,
    ["Carga Concorrente", "Threads", "R1 (s)", "R2 (s)", "Média", "Impacto"],
    [
        ["0% (CPU Livre)", "0 / 16", "0,733", "0,764", "0,75 s", "Baseline (0%)"],
        ["25% (stress-ng)", "4 / 16", "0,825", "0,810", "0,82 s", "+9,2% (1,09x)"],
        ["50% (stress-ng)", "8 / 16", "0,953", "0,953", "0,95 s", "+27,3% (1,27x)"],
        ["100% (stress-ng)", "16 / 16", "2,216", "2,980", "2,60 s", "+247,0% (3,47x)"],
    ],
    highlight_rows={0},
    warn_rows={3}
)

set_slide_transition(s9, kind="push", dir_attr="l", spd="med", dur_ms=500)
add_auto_entrance_animations(s9, [
    (fr9, "fade", 100, 350),
    (pic9, "box(out)", 120, 450),
    (hb9, "wipe(left)", 250, 400),
    (tbl9, "fade", 380, 400),
])

# ==============================================================================
# SLIDE 10 (SLIDE 07): PORTE DO PROJETO & EFICIÊNCIA ENERGÉTICA (mWh e EDP)
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
add_full_bg(s10, "bg_content_dark.jpg")
add_gta_topbar(s10, active_idx=7, total=8)
hud10 = add_hud_frame(s10, 0.55, 0.80, 12.23, 6.25)

hb10 = add_gta_header_and_bullets(
    s10, 0.90, 1.00, 6.0,
    "PORTE (.C) & ENERGIA",
    "quantidade de arquivos, consumo em mwh e race-to-idle",
    [
        ("Complexidade (8 → 24 → 48 .c)", "Quanto mais arquivos .c, maior o Speedup (1,98x → 2,59x → 2,83x), mantendo a fila paralela cheia."),
        ("Modelo Energético Real", "1 Máquina Solo = 150,0 W (45W Idle + 105W TDP) vs. 2 Máquinas = 268,5 W (2 × [45W + 0,85 × 105W])."),
        ("Limiar Race-to-Idle (1,79x)", "Como 268,5W / 150W = 1,79x, sempre que o Speedup supera 1,79x as CPUs voltam ao repouso (C-states) muito antes, economizando até 36,8% de energia."),
    ]
)

tbl10 = add_gta_table(
    s10, 0.90, 3.90, 6.0, 2.80,
    ["Carga Compilada", "Speedup", "Solo (150W)", "Dist (268,5W)", "Economia (EDP)"],
    [
        ["Projeto C (8 arqs)", "1,98x", "37,94 mWh", "34,28 mWh", "-9,6% (2,19x EDP)"],
        ["Projeto C (24 arqs)", "2,59x", "98,95 mWh", "68,48 mWh", "-30,8% (3,74x EDP)"],
        ["Projeto C (48 arqs)", "2,83x", "192,24 mWh", "121,56 mWh", "-36,8% (4,48x EDP)"],
        ["SQLite (103 .c)", "2,12x", "593,47 mWh", "500,83 mWh", "-15,6% (2,51x EDP)"],
        ["Kernel Linux (904 .o)", "2,80x", "7,14 Wh", "4,56 Wh", "-36,1% (4,38x EDP)"],
    ],
    highlight_rows={2, 4}
)

fr10, pic10 = add_framed_chart(s10, 7.15, 1.10, 5.30, 5.55, "gta_06_porte_energia.png")

set_slide_transition(s10, kind="push", dir_attr="l", spd="med", dur_ms=500)
add_auto_entrance_animations(s10, [
    (hb10, "wipe(right)", 100, 400),
    (tbl10, "fade", 250, 400),
    (fr10, "fade", 380, 350),
    (pic10, "box(out)", 400, 450),
])

# ==============================================================================
# SLIDE 11 (SLIDE 08): SÍNTESE EXECUTIVA & REGRAS PRÁTICAS
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
add_full_bg(s11, "bg_content_dark.jpg")
add_gta_topbar(s11, active_idx=8, total=8)
hud11 = add_hud_frame(s11, 0.55, 0.80, 12.23, 6.25)

hb11 = add_gta_header_and_bullets(
    s11, 0.90, 0.95, 11.5,
    "SÍNTESE DOS RESULTADOS",
    "visão geral consolidada e limites de viabilidade do distcc",
    [
        ("Quando Vale a Pena Distribuir", "Projetos com ≥ 24 arquivos .c (SQLite, Kernel Linux), rede ≥ 50 Mbps e servidores com ≤ 50% de ocupação de CPU (ganhos de 2,12x a 2,83x e -36,8% de energia)."),
        ("Quando Não Vale a Pena", "Redes lentas ≤ 10 Mbps (bloqueio TCP de até 19,24 s), servidores com 100% da CPU ocupada (+247% por context switch) ou projetos com Speedup < 1,79x."),
    ]
)

tbl11 = add_gta_table(
    s11, 0.90, 2.85, 11.5, 3.90,
    ["Frente Experimental", "Condições Comparadas", "Resultado Medido Real", "Mecanismo do Sistema Operacional"],
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
    warn_rows={5}
)

set_slide_transition(s11, kind="push", dir_attr="l", spd="med", dur_ms=500)
add_auto_entrance_animations(s11, [
    (hb11, "wipe(right)", 100, 400),
    (tbl11, "wipe(down)", 260, 450),
])

# ==============================================================================
# SLIDE 12 (ENCERRAMENTO): "APRESENTAÇÃO CONCLUÍDA" + Troféu PlayStation Animados!
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
add_full_bg(s12, "bg_sunset_clean.jpg")

# Add Trophy popup and golden APRESENTACAO CONCLUIDA as separate animated layers
trophy_pic = s12.shapes.add_picture(
    os.path.join(ASSETS_DIR, "trophy_popup.png"),
    Inches(0), Inches(0.50),
    width=Inches(3.89), height=Inches(0.646)
)
title_conc_pic = s12.shapes.add_picture(
    os.path.join(ASSETS_DIR, "title_concluida.png"),
    Inches(3.472), Inches(2.43),
    width=Inches(6.389), height=Inches(2.292)
)

set_slide_transition(s12, kind="fade", spd="med", dur_ms=700)
add_auto_entrance_animations(s12, [
    (title_conc_pic, "box(out)", 200, 600),
    (trophy_pic, "wipe(right)", 550, 500),
])

PPTX_ANIM_OUT = os.path.join(ROOT_DIR, "Apresentacao_GTA6_distcc_Animado.pptx")
prs.save(PPTX_ANIM_OUT)
print(f"Animated PowerPoint (.pptx) saved to {PPTX_ANIM_OUT}")
try:
    prs.save(PPTX_OUT)
    print(f"Also updated {PPTX_OUT}")
except PermissionError:
    print(f"Note: {PPTX_OUT} is currently open in PowerPoint; saved new file to {PPTX_ANIM_OUT}")

import zipfile
with zipfile.ZipFile(PPTX_ANIM_OUT, "r") as z:
    slides = sorted([f for f in z.namelist() if f.startswith("ppt/slides/slide") and f.endswith(".xml")], key=lambda x: int(x.split("slides/slide")[1].split(".")[0]))
    for s in slides:
        xml_str = z.read(s).decode("utf-8")
        print(f"  {s}: transition={'<p:transition' in xml_str}, timing={'<p:timing' in xml_str}")
