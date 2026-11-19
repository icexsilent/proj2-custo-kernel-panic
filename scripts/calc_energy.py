#!/usr/bin/env python3
"""
calc_energy.py
Calcula o consumo de energia (Wh) e o Produto Energia-Atraso (EDP = Wh * s)
EXCLUSIVAMENTE a partir dos tempos reais de compilação medidos pelo computador
em results/tempos_compilacao.csv, aplicando a metodologia da Seção 4.6 do roteiro
(TDP real do AMD Ryzen 7 5700X3D + Potência Ociosa Base × Tempo Medido).
"""

import csv
import os
import sys
import pandas as pd


def main():
    if len(sys.argv) < 3:
        print("Uso: calc_energy.py <tempos_csv> <energia_output_csv>", file=sys.stderr)
        sys.exit(1)

    tempos_csv = sys.argv[1]
    out_csv = sys.argv[2]

    if not os.path.exists(tempos_csv):
        print(f"Erro: {tempos_csv} não encontrado.", file=sys.stderr)
        sys.exit(1)

    # Especificações térmicas/elétricas reais da máquina de teste:
    # CPU: AMD Ryzen 7 5700X3D -> TDP oficial AMD = 105 W
    # Potência Ociosa (Idle) do desktop (Placa-mãe + RAM + NVMe + Coolers) = 45 W
    P_IDLE_W = 45.0
    P_TDP_CPU_W = 105.0

    df = pd.read_csv(tempos_csv)
    rows = []

    # 1. Extrai todos os projetos medidos em exp5c_num_arquivos e exp3_projetos (SQLite e Kernel Linux)
    subsets = []

    df_5c = df[df["experimento"] == "exp5c_num_arquivos"]
    if not df_5c.empty:
        for extra_val, grp in df_5c.groupby("extra"):
            solo_t = grp[grp["modo"] == "solo"]["tempo_s"].mean()
            dist_t = grp[grp["modo"] == "distcc"]["tempo_s"].mean()
            n_files = int(float(extra_val))
            if pd.notna(solo_t) and pd.notna(dist_t):
                subsets.append((f" Sintético ({n_files} arqs)", n_files, float(solo_t), float(dist_t)))

    df_3 = df[df["experimento"] == "exp3_projetos"]
    if not df_3.empty:
        for proj_name, grp in df_3.groupby("projeto"):
            solo_t = grp[grp["modo"] == "solo"]["tempo_s"].mean()
            dist_t = grp[grp["modo"] == "distcc"]["tempo_s"].mean()
            n_files = int(grp["arquivos_compilados"].max())
            if pd.notna(solo_t) and pd.notna(dist_t):
                subsets.append((proj_name, n_files, float(solo_t), float(dist_t)))

    subsets.sort(key=lambda x: x[1])

    for nome_carga, n_files, t_solo, t_dist in subsets:
        # Modelo físico (Seção 4.6 do Roteiro):
        # - 1 máquina (Solo): 1x Idle (45W) + 1x TDP (105W) = 150W durante t_solo
        # - 2 máquinas (Distribuído): 2x Idle (90W) + 2x TDP efetivo (85% de 105W = 89.25W por nó devido a esperas de I/O e rede) = 268.5W
        p_solo_w = P_IDLE_W + P_TDP_CPU_W
        p_dist_w = 2.0 * (P_IDLE_W + 0.85 * P_TDP_CPU_W)

        # Energia em Wh = (Potência [W] * Tempo Medido [s]) / 3600
        e_solo_wh = (p_solo_w * t_solo) / 3600.0
        e_dist_wh = (p_dist_w * t_dist) / 3600.0

        # EDP (Energy-Delay Product) em Wh * s = Energia [Wh] * Tempo Medido [s]
        edp_solo = e_solo_wh * t_solo
        edp_dist = e_dist_wh * t_dist

        rows.append(
            {
                "tipo": "medido_real",
                "projeto_carga": nome_carga.strip(),
                "arquivos_c": n_files,
                "tempo_solo_s": round(t_solo, 4),
                "tempo_dist_2maq_s": round(t_dist, 4),
                "potencia_solo_w": round(p_solo_w, 2),
                "potencia_dist_2maq_w": round(p_dist_w, 2),
                "energia_solo_wh": round(e_solo_wh, 6),
                "energia_dist_2maq_wh": round(e_dist_wh, 6),
                "edp_solo_wh_s": round(edp_solo, 6),
                "edp_dist_2maq_wh_s": round(edp_dist, 6),
            }
        )

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "tipo",
                "projeto_carga",
                "arquivos_c",
                "tempo_solo_s",
                "tempo_dist_2maq_s",
                "potencia_solo_w",
                "potencia_dist_2maq_w",
                "energia_solo_wh",
                "energia_dist_2maq_wh",
                "edp_solo_wh_s",
                "edp_dist_2maq_wh_s",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"[energia] {len(rows)} pontos reais calculados em {out_csv}")


if __name__ == "__main__":
    main()
