#!/usr/bin/env bash
# Manage a local standalone Milvus container (Docker).
# Usage: bash scripts/standalone_embed.sh start|stop|restart|delete

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CONFIG_DIR="$PROJECT_ROOT/config"
VOLUMES_DIR="$PROJECT_ROOT/volumes/milvus"
EMBED_ETCD_CONFIG="$CONFIG_DIR/embedEtcd.yaml"
USER_CONFIG="$CONFIG_DIR/user.yaml"

DOCKER="docker"

if ! docker info >/dev/null 2>&1; then
    if command -v sudo >/dev/null 2>&1 && sudo docker info >/dev/null 2>&1; then
        DOCKER="sudo docker"
    else
        echo "Docker is not running or is not accessible."
        exit 1
    fi
fi

ensure_config_files() {
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$VOLUMES_DIR"

    cat > "$EMBED_ETCD_CONFIG" <<CONFIG
listen-client-urls: http://0.0.0.0:2379
advertise-client-urls: http://0.0.0.0:2379
quota-backend-bytes: 4294967296
auto-compaction-mode: revision
auto-compaction-retention: '1000'
CONFIG

    if [ ! -f "$USER_CONFIG" ]; then
        cat > "$USER_CONFIG" <<CONFIG
# Extra config to override default milvus.yaml
CONFIG
    fi
}

run_embed() {
    ensure_config_files

    $DOCKER run -d \
        --name milvus-standalone \
        --security-opt seccomp:unconfined \
        -e ETCD_USE_EMBED=true \
        -e ETCD_DATA_DIR=/var/lib/milvus/etcd \
        -e ETCD_CONFIG_PATH=/milvus/configs/embedEtcd.yaml \
        -e COMMON_STORAGETYPE=local \
        -e DEPLOY_MODE=STANDALONE \
        -v "$VOLUMES_DIR:/var/lib/milvus" \
        -v "$EMBED_ETCD_CONFIG:/milvus/configs/embedEtcd.yaml" \
        -v "$USER_CONFIG:/milvus/configs/user.yaml" \
        -p 19530:19530 \
        -p 9091:9091 \
        -p 2379:2379 \
        --health-cmd="curl -f http://localhost:9091/healthz" \
        --health-interval=30s \
        --health-start-period=90s \
        --health-timeout=20s \
        --health-retries=3 \
        milvusdb/milvus:v2.6.13 \
        milvus run standalone 1> /dev/null
}

wait_for_milvus_running() {
    echo "Waiting for Milvus to start..."

    while true; do
        res=$($DOCKER ps | grep milvus-standalone | grep healthy | wc -l | tr -d ' ')
        if [ "$res" -eq 1 ]; then
            echo "Milvus started successfully."
            break
        fi
        sleep 1
    done
}

start() {
    ensure_config_files

    res=$($DOCKER ps | grep milvus-standalone | grep healthy | wc -l | tr -d ' ')
    if [ "$res" -eq 1 ]; then
        echo "Milvus is already running."
        exit 0
    fi

    res=$($DOCKER ps -a | grep milvus-standalone | wc -l | tr -d ' ')
    if [ "$res" -eq 1 ]; then
        $DOCKER start milvus-standalone 1> /dev/null
    else
        run_embed
    fi

    wait_for_milvus_running
}

stop() {
    $DOCKER stop milvus-standalone 1> /dev/null
    echo "Milvus stopped successfully."
}

restart() {
    stop
    start
}

delete_container() {
    res=$($DOCKER ps | grep milvus-standalone | wc -l | tr -d ' ')
    if [ "$res" -eq 1 ]; then
        echo "Please stop Milvus before deleting the container."
        exit 1
    fi

    $DOCKER rm milvus-standalone 1> /dev/null
    echo "Milvus container deleted successfully."
}

delete() {
    read -p "This will delete the Milvus container and local Milvus data. Continue? [y/n] " check

    if [ "$check" = "y" ] || [ "$check" = "Y" ]; then
        delete_container
        rm -rf "$PROJECT_ROOT/volumes"
        echo "Milvus local data deleted successfully."
    else
        echo "Delete cancelled."
    fi
}

case "${1:-}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    delete)
        delete
        ;;
    *)
        echo "Usage: bash scripts/standalone_embed.sh start|stop|restart|delete"
        ;;
esac
