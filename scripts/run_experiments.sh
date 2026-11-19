#!/usr/bin/env bash
# run_experiments.sh
# Orquestra os experimentos do roteiro distcc (Perguntas 1 a 6).
# Uso:
#   ./run_experiments.sh {all|smoke|exp1|exp3|exp4|exp5a|exp5b|exp5c|exp6} [reps]

set -euo pipefail

MODE="${1:-all}"
REPS="${2:-3}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_DIR="${RESULTS_DIR_OVERRIDE:-$ROOT_DIR/results}"
LAB_DIR="$HOME/distcc_lab"

# Hosts configuraveis via variaveis de ambiente (permite trocar por IPs reais facilmente)
NODE1_HOST="${NODE1_HOST:-127.0.0.1:3632}"
NODE2_HOST="${NODE2_HOST:-127.0.0.1:3633}"
NODE3_HOST="${NODE3_HOST:-127.0.0.1:3634}"
NODE4_HOST="${NODE4_HOST:-127.0.0.1:3635}"
JOBS_PER_NODE="${JOBS_PER_NODE:-4}"
NET_IFACE="${NET_IFACE:-lo}"

mkdir -p "$RESULTS_DIR" "$LAB_DIR"

cleanup_tc_and_stress() {
    tc qdisc del dev "$NET_IFACE" root 2>/dev/null || true
    tc qdisc del dev veth_host root 2>/dev/null || true
    ip netns del distcc_ns 2>/dev/null || true
    pkill -f "stress-ng" 2>/dev/null || true
}
trap cleanup_tc_and_stress EXIT

collect_hardware_specs() {
    local hw_csv="$RESULTS_DIR/hardware_specs.csv"
    local cpu_model cores threads ram_gb kernel_ver gcc_ver
    cpu_model=$(lscpu | awk -F: '/Model name/ {gsub(/^[ \t]+/, "", $2); print $2; exit}')
    threads=$(nproc)
    cores=$((threads / 2))
    ram_gb=$(free -g | awk '/^Mem:/ {print $2}')
    kernel_ver=$(uname -r)
    gcc_ver=$(gcc --version | head -n 1)

    cat <<EOF > "$hw_csv"
maquina,papel,cpu_modelo,nucleos_fisicos,threads_logicas,ram_gb,sistema_kernel,compilador,tdp_w,idle_w
Maquina_1_Local,Cliente + Servidor Node1,"$cpu_model",$cores,$threads,$ram_gb,"Ubuntu WSL2 ($kernel_ver)","$gcc_ver",105,45
Node_2_Worker,Servidor Node2,"$cpu_model",$cores,$threads,$ram_gb,"Ubuntu WSL2 ($kernel_ver)","$gcc_ver",105,45
EOF
    echo "[hw] Especificacoes salvas em $hw_csv"
}

# Gera um projeto C sintetico com N arquivos .c independentes que exigem trabalho real do otimizador do GCC (-O2)
generate_synthetic_project() {
    local target_dir="$1"
    local num_files="$2"
    local funcs_per_file="${3:-35}"
    local header_kb="${4:-0}"

    mkdir -p "$target_dir"
    rm -f "$target_dir"/*.c "$target_dir"/*.h "$target_dir"/*.o "$target_dir"/app "$target_dir"/Makefile

    cat << 'EOF' > "$target_dir/common.h"
#ifndef COMMON_H
#define COMMON_H
#include <stdint.h>
#include <stddef.h>
#include <math.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#define STEP_MIX(a, b, c) do { \
    a ^= b; a -= (b << 13) | (b >> 19); \
    b ^= c; b -= (c << 7)  | (c >> 25); \
    c ^= a; c -= (a << 16) | (a >> 16); \
} while (0)
EOF

    if [ "$header_kb" -gt 0 ]; then
        # Simula headers grandes de projetos reais (ex.: 100 KB de declaracoes pos-preprocessamento)
        local n_decls=$((header_kb * 14))
        for d in $(seq 1 "$n_decls"); do
            echo "struct hdr_type_${d} { uint64_t f1_${d}; uint64_t f2_${d}; uint32_t flags_${d}; };"
        done >> "$target_dir/common.h"
    fi
    echo "#endif" >> "$target_dir/common.h"

    local srcs="main.c"
    for i in $(seq 1 "$num_files"); do
        srcs="$srcs mod_${i}.c"
        {
            echo "#include \"common.h\""
            for f in $(seq 1 "$funcs_per_file"); do
                cat <<EOF
uint64_t compute_${i}_${f}(uint64_t seed) {
    uint64_t a = seed + ${i}ULL * 0x9e3779b97f4a7c15ULL;
    uint64_t b = seed ^ (${f}ULL * 0xbf58476d1ce4e5b9ULL);
    uint64_t c = (a + b) ^ 0x94d049bb133111ebULL;
    for (int k = 0; k < 128; k++) {
        STEP_MIX(a, b, c);
        a += (b ^ (c >> 3)) * 31ULL + k;
        b += (c ^ (a << 5)) * 17ULL;
        c ^= (a + b);
    }
    return a ^ b ^ c;
}
EOF
            done
            echo "uint64_t entry_mod_${i}(uint64_t x) {"
            echo "    uint64_t acc = x;"
            for f in $(seq 1 "$funcs_per_file"); do
                echo "    acc ^= compute_${i}_${f}(acc + ${f});"
            done
            echo "    return acc;"
            echo "}"
        } > "$target_dir/mod_${i}.c"
    done

    {
        echo "#include \"common.h\""
        for i in $(seq 1 "$num_files"); do
            echo "uint64_t entry_mod_${i}(uint64_t x);"
        done
        echo "int main(void) {"
        echo "    uint64_t total = 1;"
        for i in $(seq 1 "$num_files"); do
            echo "    total ^= entry_mod_${i}(total + ${i});"
        done
        echo "    printf(\"Check=%llu\\n\", (unsigned long long)total);"
        echo "    return 0;"
        echo "}"
    } > "$target_dir/main.c"

    cat <<EOF > "$target_dir/Makefile"
CC ?= gcc
CFLAGS = -O2 -Wall
SRCS = $srcs
OBJS = \$(SRCS:.c=.o)

all: app

app: \$(OBJS)
	\$(CC) \$(CFLAGS) -o app \$(OBJS)

%.o: %.c
	\$(CC) \$(CFLAGS) -c \$< -o \$@

clean:
	rm -f *.o app
EOF
}

run_exp1_2() {
    echo "================================================================="
    echo " [EXP 1 & 2] Tempo Individual vs. Coletivo + % por Maquina"
    echo "================================================================="
    local proj_dir="$LAB_DIR/bench_exp1"
    local nfiles="${EXP1_FILES:-48}"
    generate_synthetic_project "$proj_dir" "$nfiles" 40

    "$SCRIPT_DIR/manage_distccd.sh" start 192.168.0.0/16 "$JOBS_PER_NODE" 4 >/dev/null

    # Maquina 1 isolada (4 jobs)
    "$SCRIPT_DIR/bench_core.sh" "exp1_individual_coletivo" "bench_c" "$proj_dir" \
        "Maquina_1_Individual" "distcc" "${NODE1_HOST}/${JOBS_PER_NODE}" "$JOBS_PER_NODE" "$REPS" 1 "1_maquina"

    # Maquina 2 isolada (4 jobs)
    "$SCRIPT_DIR/bench_core.sh" "exp1_individual_coletivo" "bench_c" "$proj_dir" \
        "Maquina_2_Individual" "distcc" "${NODE2_HOST}/${JOBS_PER_NODE}" "$JOBS_PER_NODE" "$REPS" 0 "1_maquina"

    # Coletivo (Maquina 1 + Maquina 2 = 8 jobs)
    local total_jobs=$((JOBS_PER_NODE * 2))
    "$SCRIPT_DIR/bench_core.sh" "exp1_individual_coletivo" "bench_c" "$proj_dir" \
        "Coletivo_M1_M2" "distcc" "${NODE1_HOST}/${JOBS_PER_NODE} ${NODE2_HOST}/${JOBS_PER_NODE}" "$total_jobs" "$REPS" 0 "coletivo"
}

run_exp3() {
    echo "================================================================="
    echo " [EXP 3] Comparacao entre Projetos (SQLite vs. Kernel Linux)"
    echo "================================================================="
    local j_solo="${EXP3_SOLO_JOBS:-2}"
    local j_per_node="${EXP3_NODE_JOBS:-4}"
    local total_jobs=$((j_per_node * 3))
    "$SCRIPT_DIR/manage_distccd.sh" start 192.168.0.0/16 "$j_per_node" 4 >/dev/null
    local hosts="${NODE1_HOST}/${j_per_node} ${NODE2_HOST}/${j_per_node} ${NODE3_HOST}/${j_per_node}"

    # Se os projetos reais da Fase 4 ja estiverem preparados em ~/distcc_lab/{sqlite_src,linux_src}, usa-os;
    # caso contrario (teste da Fase 2), usa projetos sinteticos representativos.
    if [ -d "$LAB_DIR/sqlite_src" ] && [ -f "$LAB_DIR/sqlite_src/Makefile" ]; then
        echo "  -> Usando repositorio real do SQLite (103 arquivos .c) em $LAB_DIR/sqlite_src"
        "$SCRIPT_DIR/bench_core.sh" "exp3_projetos" "SQLite" "$LAB_DIR/sqlite_src" \
            "Solo" "solo" "localhost" "$j_solo" "$REPS" 1 "sqlite" "sqlite3"
        "$SCRIPT_DIR/bench_core.sh" "exp3_projetos" "SQLite" "$LAB_DIR/sqlite_src" \
            "Distribuido" "distcc" "$hosts" "$total_jobs" "$REPS" 0 "sqlite" "sqlite3"
    else
        echo "  -> Usando perfil sintetico SQLite (poucos arquivos + link pesado) para validacao da Fase 2"
        local sq_dir="$LAB_DIR/sim_sqlite"
        generate_synthetic_project "$sq_dir" 12 30
        "$SCRIPT_DIR/bench_core.sh" "exp3_projetos" "SQLite" "$sq_dir" \
            "Solo" "solo" "localhost" "$j_solo" "$REPS" 1 "sqlite_sim"
        "$SCRIPT_DIR/bench_core.sh" "exp3_projetos" "SQLite" "$sq_dir" \
            "Distribuido" "distcc" "$hosts" "$total_jobs" "$REPS" 0 "sqlite_sim"
    fi

    if [ -d "$LAB_DIR/linux_src" ] && [ -f "$LAB_DIR/linux_src/.config" ]; then
        echo "  -> Usando fonte real do Kernel Linux (904 objetos) em $LAB_DIR/linux_src"
        "$SCRIPT_DIR/bench_core.sh" "exp3_projetos" "Kernel_Linux" "$LAB_DIR/linux_src" \
            "Solo" "solo" "localhost" "$j_solo" "$REPS" 1 "linux" "vmlinux"
        "$SCRIPT_DIR/bench_core.sh" "exp3_projetos" "Kernel_Linux" "$LAB_DIR/linux_src" \
            "Distribuido" "distcc" "$hosts" "$total_jobs" "$REPS" 0 "linux" "vmlinux"
    else
        echo "  -> Usando perfil sintetico Kernel Linux (muitos arquivos independentes) para validacao da Fase 2"
        local lx_dir="$LAB_DIR/sim_kernel"
        generate_synthetic_project "$lx_dir" 80 40
        "$SCRIPT_DIR/bench_core.sh" "exp3_projetos" "Kernel_Linux" "$lx_dir" \
            "Solo" "solo" "localhost" "$j_solo" "$REPS" 1 "kernel_sim"
        "$SCRIPT_DIR/bench_core.sh" "exp3_projetos" "Kernel_Linux" "$lx_dir" \
            "Distribuido" "distcc" "$hosts" "$total_jobs" "$REPS" 0 "kernel_sim"
    fi
}

run_exp4() {
    echo "================================================================="
    echo " [EXP 4] Velocidade de Rede (tc qdisc tbf: 1 a 1000 Mbit/s)"
    echo "================================================================="
    local proj_dir="$LAB_DIR/bench_exp4"
    local nfiles="${EXP4_FILES:-12}"
    generate_synthetic_project "$proj_dir" "$nfiles" 30 65

    local total_jobs=$((JOBS_PER_NODE * 2))
    local hosts=""
    local use_veth=0

    if [ "$NET_IFACE" = "lo" ] || [ "$NET_IFACE" = "veth" ]; then
        use_veth=1
        echo "  [veth] Criando par Ethernet virtual (veth_host <-> veth_ns em ip netns) para modelagem exata do tc tbf..."
        ip netns del distcc_ns 2>/dev/null || true
        ip netns add distcc_ns
        ip link add veth_host type veth peer name veth_ns
        ip link set veth_ns netns distcc_ns
        ip addr add 10.200.1.1/24 dev veth_host
        ip link set veth_host up
        ip netns exec distcc_ns ip addr add 10.200.1.2/24 dev veth_ns
        ip netns exec distcc_ns ip link set lo up
        ip netns exec distcc_ns ip link set veth_ns up
        ip netns exec distcc_ns distccd --daemon --user distccd --port 3632 --listen 10.200.1.2 --jobs "$JOBS_PER_NODE" --allow 10.200.1.0/24 --log-file /tmp/distccd_veth1.log --verbose
        ip netns exec distcc_ns distccd --daemon --user distccd --port 3633 --listen 10.200.1.2 --jobs "$JOBS_PER_NODE" --allow 10.200.1.0/24 --log-file /tmp/distccd_veth2.log --verbose
        hosts="10.200.1.2:3632/${JOBS_PER_NODE} 10.200.1.2:3633/${JOBS_PER_NODE}"
    else
        "$SCRIPT_DIR/manage_distccd.sh" start 192.168.0.0/16 "$JOBS_PER_NODE" 4 >/dev/null
        hosts="${NODE1_HOST}/${JOBS_PER_NODE} ${NODE2_HOST}/${JOBS_PER_NODE}"
    fi

    local speeds="${EXP4_SPEEDS:-1 5 10 50 100 500 1000}"
    local first=1
    for bw in $speeds; do
        if [ "$use_veth" = "1" ]; then
            tc qdisc del dev veth_host root 2>/dev/null || true
            ip netns exec distcc_ns tc qdisc del dev veth_ns root 2>/dev/null || true
            tc qdisc add dev veth_host root tbf rate "${bw}mbit" burst 64kbit limit 4194304
            ip netns exec distcc_ns tc qdisc add dev veth_ns root tbf rate "${bw}mbit" burst 64kbit limit 4194304
            echo "  [tc] Banda limitada em ${bw} Mbit/s na interface veth_host <-> veth_ns"
        else
            tc qdisc del dev "$NET_IFACE" root 2>/dev/null || true
            tc qdisc add dev "$NET_IFACE" root tbf rate "${bw}mbit" burst 64kbit limit 4194304
            echo "  [tc] Banda limitada em ${bw} Mbit/s na interface ${NET_IFACE}"
        fi

        DISTCC_CONNECT_TIMEOUT=30 "$SCRIPT_DIR/bench_core.sh" "exp4_rede" "bench_c" "$proj_dir" \
            "${bw}_Mbps" "distcc" "$hosts" "$total_jobs" "$REPS" "$first" "$bw"
        first=0
    done

    if [ "$use_veth" = "1" ]; then
        tc qdisc del dev veth_host root 2>/dev/null || true
        ip netns del distcc_ns 2>/dev/null || true
    else
        tc qdisc del dev "$NET_IFACE" root 2>/dev/null || true
    fi
}

run_exp5a() {
    echo "================================================================="
    echo " [EXP 5A] Escala: Numero de Maquinas / Nos (1 a 4)"
    echo "================================================================="
    local proj_dir="$LAB_DIR/bench_exp5a"
    local nfiles="${EXP5A_FILES:-48}"
    generate_synthetic_project "$proj_dir" "$nfiles" 35

    # Fixamos 2 jobs por no para ver claramente o escalonamento de 1, 2, 3 e 4 nos (2, 4, 6 e 8 threads totais)
    local j_node="${EXP5A_JOBS_PER_NODE:-2}"
    "$SCRIPT_DIR/manage_distccd.sh" start 192.168.0.0/16 "$j_node" 4 >/dev/null

    "$SCRIPT_DIR/bench_core.sh" "exp5a_escala" "bench_c" "$proj_dir" \
        "1_Maquina" "distcc" "${NODE1_HOST}/${j_node}" "$((j_node * 1))" "$REPS" 1 "1"

    "$SCRIPT_DIR/bench_core.sh" "exp5a_escala" "bench_c" "$proj_dir" \
        "2_Maquinas" "distcc" "${NODE1_HOST}/${j_node} ${NODE2_HOST}/${j_node}" "$((j_node * 2))" "$REPS" 0 "2"

    "$SCRIPT_DIR/bench_core.sh" "exp5a_escala" "bench_c" "$proj_dir" \
        "3_Maquinas" "distcc" "${NODE1_HOST}/${j_node} ${NODE2_HOST}/${j_node} ${NODE3_HOST}/${j_node}" "$((j_node * 3))" "$REPS" 0 "3"

    "$SCRIPT_DIR/bench_core.sh" "exp5a_escala" "bench_c" "$proj_dir" \
        "4_Maquinas" "distcc" "${NODE1_HOST}/${j_node} ${NODE2_HOST}/${j_node} ${NODE3_HOST}/${j_node} ${NODE4_HOST}/${j_node}" "$((j_node * 4))" "$REPS" 0 "4"
}

run_exp5b() {
    echo "================================================================="
    echo " [EXP 5B] Processos de Fundo Competindo (stress-ng: 0% a 100%)"
    echo "================================================================="
    local proj_dir="$LAB_DIR/bench_exp5b"
    local nfiles="${EXP5B_FILES:-40}"
    generate_synthetic_project "$proj_dir" "$nfiles" 35

    "$SCRIPT_DIR/manage_distccd.sh" start 192.168.0.0/16 "$JOBS_PER_NODE" 4 >/dev/null
    local total_jobs=$((JOBS_PER_NODE * 2))
    local hosts="${NODE1_HOST}/${JOBS_PER_NODE} ${NODE2_HOST}/${JOBS_PER_NODE}"
    local total_cpus
    total_cpus=$(nproc)

    local loads="0 25 50 100"
    local first=1
    for pct in $loads; do
        pkill -f "stress-ng" 2>/dev/null || true
        local stress_PID=""
        if [ "$pct" -gt 0 ]; then
            local workers=$(( (total_cpus * pct) / 100 ))
            [ "$workers" -lt 1 ] && workers=1
            echo "  [stress-ng] Iniciando carga de fundo: ${pct}% (${workers} de ${total_cpus} threads)..."
            stress-ng --cpu "$workers" --timeout 600s --quiet &
            stress_PID=$!
            sleep 1
        else
            echo "  [stress-ng] Sem carga de fundo (0%)..."
        fi

        "$SCRIPT_DIR/bench_core.sh" "exp5b_stress" "bench_c" "$proj_dir" \
            "Carga_${pct}pct" "distcc" "$hosts" "$total_jobs" "$REPS" "$first" "$pct"
        first=0

        if [ -n "$stress_PID" ]; then
            kill "$stress_PID" 2>/dev/null || true
            pkill -f "stress-ng" 2>/dev/null || true
            wait "$stress_PID" 2>/dev/null || true
        fi
    done
}

run_exp5c() {
    echo "================================================================="
    echo " [EXP 5C] Numero de Arquivos .c x Paralelizacao (Speedup)"
    echo "================================================================="
    local j_solo=2
    local j_dist=8
    "$SCRIPT_DIR/manage_distccd.sh" start 192.168.0.0/16 4 4 >/dev/null
    local hosts="${NODE1_HOST}/4 ${NODE2_HOST}/4"

    local counts="${EXP5C_COUNTS:-10 25 50 100 150}"
    for cnt in $counts; do
        local proj_dir="$LAB_DIR/bench_exp5c_${cnt}"
        generate_synthetic_project "$proj_dir" "$cnt" 30
        "$SCRIPT_DIR/bench_core.sh" "exp5c_num_arquivos" "bench_${cnt}c" "$proj_dir" \
            "Solo_${cnt}arq" "solo" "localhost" "$j_solo" "$REPS" 1 "$cnt"
        "$SCRIPT_DIR/bench_core.sh" "exp5c_num_arquivos" "bench_${cnt}c" "$proj_dir" \
            "Dist_${cnt}arq" "distcc" "$hosts" "$j_dist" "$REPS" 0 "$cnt"
    done
}

run_exp6() {
    echo "================================================================="
    echo " [EXP 6] Modelagem e Analise de Energia (Wh e EDP)"
    echo "================================================================="
    python3 "$SCRIPT_DIR/calc_energy.py" "$RESULTS_DIR/tempos_compilacao.csv" "$RESULTS_DIR/energia_estimada.csv"
}

collect_hardware_specs

case "$MODE" in
    all)
        run_exp1_2
        run_exp3
        run_exp4
        run_exp5a
        run_exp5b
        run_exp5c
        run_exp6
        ;;
    smoke)
        export EXP1_FILES=16 EXP4_FILES=16 EXP5A_FILES=16 EXP5B_FILES=16
        export EXP4_SPEEDS="1 10 100 1000"
        export EXP5C_COUNTS="8 24 48"
        run_exp1_2
        run_exp3
        run_exp4
        run_exp5a
        run_exp5b
        run_exp5c
        run_exp6
        ;;
    exp1|exp2) run_exp1_2 ;;
    exp3) run_exp3 ;;
    exp4) run_exp4 ;;
    exp5a) run_exp5a ;;
    exp5b) run_exp5b ;;
    exp5c) run_exp5c ;;
    exp6) run_exp6 ;;
    *)
        echo "Uso: $0 {all|smoke|exp1|exp3|exp4|exp5a|exp5b|exp5c|exp6} [reps]"
        exit 1
        ;;
esac
