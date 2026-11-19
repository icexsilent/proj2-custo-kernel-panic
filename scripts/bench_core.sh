#!/usr/bin/env bash
# bench_core.sh
# Executa N repeticoes de um build (solo ou distcc), com rodada inicial de aquecimento (warm-up)
# e registra os tempos e a distribuicao de arquivos por host em CSV.
#
# Uso:
#   ./bench_core.sh <experimento> <projeto> <dir_projeto> <rotulo> <modo:solo|distcc> <hosts> <jobs> <reps> <warmup:0|1> <extra> [make_target]

set -euo pipefail

EXPERIMENTO="${1}"
PROJETO="${2}"
DIR_PROJETO="${3}"
ROTULO="${4}"
MODO="${5}"
HOSTS="${6}"
JOBS="${7}"
REPS="${8}"
WARMUP="${9:-1}"
EXTRA="${10:-none}"
MAKE_TARGET="${11:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_DIR="${RESULTS_DIR_OVERRIDE:-$ROOT_DIR/results}"

mkdir -p "$RESULTS_DIR"

TEMPOS_CSV="$RESULTS_DIR/tempos_compilacao.csv"
HOSTS_CSV="$RESULTS_DIR/distribuicao_hosts.csv"

if [ ! -f "$TEMPOS_CSV" ]; then
    echo "experimento,projeto,rotulo,modo,hosts,jobs,extra,repeticao,tempo_s,arquivos_compilados" > "$TEMPOS_CSV"
fi

cd "$DIR_PROJETO"

run_single_build() {
    make clean >/dev/null 2>&1 || true
    rm -f /tmp/distcc-client.log

    if [ "$MODO" = "distcc" ]; then
        export DISTCC_HOSTS="$HOSTS"
        if [ "$EXPERIMENTO" = "exp1_individual_coletivo" ]; then
            export DISTCC_VERBOSE=1
            export DISTCC_LOG="/tmp/distcc-client.log"
        else
            unset DISTCC_VERBOSE || true
            unset DISTCC_LOG || true
        fi
        export DISTCC_FALLBACK=1
        export DISTCC_POTENTIAL_HOSTS=""
        CC_CMD="distcc gcc"
        HOSTCC_CMD="gcc"
    else
        unset DISTCC_HOSTS || true
        unset DISTCC_VERBOSE || true
        unset DISTCC_LOG || true
        CC_CMD="gcc"
        HOSTCC_CMD="gcc"
    fi

    local start_ts end_ts elapsed
    start_ts=$(date +%s.%N)
    if [ -n "$MAKE_TARGET" ]; then
        make -j"$JOBS" CC="$CC_CMD" HOSTCC="$HOSTCC_CMD" "$MAKE_TARGET" >/dev/null 2>&1
    else
        make -j"$JOBS" CC="$CC_CMD" HOSTCC="$HOSTCC_CMD" >/dev/null 2>&1
    fi
    end_ts=$(date +%s.%N)
    elapsed=$(echo "$end_ts - $start_ts" | bc -l | awk '{printf "%.4f", $0}')
    echo "$elapsed"
}

if [ "$WARMUP" = "1" ]; then
    echo "  [warm-up] Aquecendo cache de disco para ($PROJETO | $ROTULO)..."
    run_single_build >/dev/null
fi

for rep in $(seq 1 "$REPS"); do
    elapsed=$(run_single_build)
    if [ "$MODO" = "distcc" ] && [ "$EXPERIMENTO" = "exp1_individual_coletivo" ]; then
        num_files=$(python3 "$SCRIPT_DIR/parse_distcc_logs.py" "/tmp/distcc-client.log" "$HOSTS_CSV" "$EXPERIMENTO" "$PROJETO" "$ROTULO" "$rep")
    else
        num_files=$(find . -name "*.o" 2>/dev/null | wc -l)
    fi
    echo "  [rep $rep/$REPS] $EXPERIMENTO | $PROJETO | $ROTULO ($MODO, -j$JOBS) -> ${elapsed}s (${num_files} objs)"
    echo "$EXPERIMENTO,$PROJETO,$ROTULO,$MODO,$HOSTS,$JOBS,$EXTRA,$rep,$elapsed,$num_files" >> "$TEMPOS_CSV"
done
