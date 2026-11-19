#!/usr/bin/env bash
# manage_distccd.sh
# Gerencia até 4 daemons distccd locais (portas 3632..3635) para testes multi-nó em 1 máquina
# ou modo servidor na porta 3632 para rede local (LAN).
# Uso: ./manage_distccd.sh {start|stop|restart|status|clean-logs} [allow_subnet] [jobs_per_node] [num_nodes]

set -euo pipefail

ACTION="${1:-status}"
ALLOW_SUBNET="${2:-192.168.0.0/16}"
JOBS_PER_NODE="${3:-4}"
NUM_NODES="${4:-4}"

start_daemons() {
    echo "[distccd] Parando instancias anteriores (se existirem)..."
    stop_daemons >/dev/null 2>&1 || true

    for idx in $(seq 1 "$NUM_NODES"); do
        port=$((3631 + idx))
        logfile="/tmp/distccd_node${idx}.log"
        pidfile="/tmp/distccd_node${idx}.pid"
        rm -f "$logfile"
        echo "[distccd] Iniciando Node ${idx} na porta ${port} (jobs=${JOBS_PER_NODE})..."
        distccd --daemon \
            --user distccd \
            --port "$port" \
            --listen 0.0.0.0 \
            --jobs "$JOBS_PER_NODE" \
            --allow 127.0.0.0/8 \
            --allow 172.16.0.0/12 \
            --allow 10.0.0.0/8 \
            --allow "$ALLOW_SUBNET" \
            --log-file "$logfile" \
            --pid-file "$pidfile" \
            --log-level notice
    done

    sleep 1
    status_daemons
}

stop_daemons() {
    for idx in 1 2 3 4; do
        pidfile="/tmp/distccd_node${idx}.pid"
        if [ -f "$pidfile" ]; then
            kill "$(cat "$pidfile")" 2>/dev/null || true
            rm -f "$pidfile"
        fi
    done
    pkill -x "distccd" 2>/dev/null || true
    echo "[distccd] Todos os daemons distccd foram encerrados."
}

status_daemons() {
    echo "=== Portas escutando (distccd) ==="
    ss -tlnp 2>/dev/null | grep -E "363[2-5]|distccd" || echo "Nenhum daemon distccd ativo."
    echo "=== Logs disponiveis ==="
    for f in /tmp/distccd_node1.log /tmp/distccd_node2.log /tmp/distccd_node3.log /tmp/distccd_node4.log /tmp/distcc-client.log; do
        if [ -f "$f" ]; then
            echo "  $f ($(wc -l < "$f") linhas)"
        fi
    done
}

clean_logs() {
    for idx in 1 2 3 4; do
        : > "/tmp/distccd_node${idx}.log" 2>/dev/null || true
    done
    rm -f /tmp/distcc-client.log
    echo "[distccd] Logs zerados."
}

case "$ACTION" in
    start)
        start_daemons
        ;;
    stop)
        stop_daemons
        ;;
    restart)
        stop_daemons
        start_daemons
        ;;
    status)
        status_daemons
        ;;
    clean-logs)
        clean_logs
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|clean-logs} [allow_subnet] [jobs_per_node] [num_nodes]"
        exit 1
        ;;
esac
