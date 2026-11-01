#!/usr/bin/env bash

# ==============================================================================
# ResearchLens AI - Docker Development Orchestration Script
# Supports live hot-reloading for FastAPI backend and React Vite frontend.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

COMPOSE_FILE="docker-compose.dev.yml"

# Colors for terminal output
BOLD="\033[1m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

# Print banner
print_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "======================================================================"
    echo "         ResearchLens AI - Docker Development Environment             "
    echo "======================================================================"
    echo -e "${RESET}"
}

# Preflight checks
check_environment() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}[ERROR] 'docker' command could not be found.${RESET}"
        echo "Please install Docker Desktop: https://www.docker.com/products/docker-desktop"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        echo -e "${RED}[ERROR] Docker daemon is not running.${RESET}"
        echo "Please launch Docker Desktop and try running this script again."
        exit 1
    fi

    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            echo -e "${YELLOW}[WARNING] .env file not found. Auto-creating from .env.example...${RESET}"
            cp .env.example .env
            echo -e "${YELLOW}Please verify your GEMINI_API_KEY in .env before testing LLM synthesis.${RESET}"
        else
            echo -e "${RED}[ERROR] Neither .env nor .env.example was found.${RESET}"
            exit 1
        fi
    fi
}

show_urls() {
    echo ""
    echo -e "${GREEN}${BOLD}Active Development Services:${RESET}"
    echo -e "  🌐 ${BOLD}React Frontend:${RESET}        http://localhost:5173"
    echo -e "  ⚡ ${BOLD}FastAPI Backend:${RESET}       http://localhost:8000"
    echo -e "  📖 ${BOLD}Interactive Swagger:${RESET}   http://localhost:8000/docs"
    echo -e "  🩺 ${BOLD}Health Probe:${RESET}          http://localhost:8000/health"
    echo -e "  🔍 ${BOLD}Qdrant Vector DB:${RESET}      http://localhost:6333/dashboard"
    echo ""
}

show_help() {
    print_banner
    echo -e "${BOLD}Usage:${RESET} ./docker-dev.sh [command]"
    echo ""
    echo -e "${BOLD}Commands:${RESET}"
    echo -e "  ${CYAN}up${RESET}               Start all services (Qdrant, Backend, Frontend) with hot reload"
    echo -e "  ${CYAN}up -d | detached${RESET}  Start all services in background (detached mode)"
    echo -e "  ${CYAN}backend${RESET}          Start only Qdrant + FastAPI backend (run frontend locally)"
    echo -e "  ${CYAN}down${RESET}             Stop and remove development containers"
    echo -e "  ${CYAN}restart${RESET}          Restart all development services"
    echo -e "  ${CYAN}build${RESET}            Rebuild containers from scratch without cache"
    echo -e "  ${CYAN}logs [service]${RESET}   Follow live container logs (e.g. ./docker-dev.sh logs api)"
    echo -e "  ${CYAN}shell [service]${RESET}  Open interactive bash in a container (default: api)"
    echo -e "  ${CYAN}eval${RESET}             Run 6-baseline benchmark suite inside the running API container"
    echo -e "  ${CYAN}help${RESET}             Display this guide"
    echo ""
}

# Main command dispatcher
COMMAND="${1:-up}"

if [ "$COMMAND" == "help" ] || [ "$COMMAND" == "--help" ] || [ "$COMMAND" == "-h" ]; then
    show_help
    exit 0
fi

check_environment

case "$COMMAND" in
    up)
        print_banner
        if [ "$2" == "-d" ] || [ "$2" == "--detached" ]; then
            echo -e "${CYAN}Starting all development services in background...${RESET}"
            docker compose -f "$COMPOSE_FILE" up -d
            show_urls
            echo -e "Run ${BOLD}./docker-dev.sh logs${RESET} to inspect live output."
        else
            echo -e "${CYAN}Starting development stack with hot-reloading (Press Ctrl+C to stop)...${RESET}"
            show_urls
            docker compose -f "$COMPOSE_FILE" up
        fi
        ;;

    detached|-d)
        print_banner
        echo -e "${CYAN}Starting all development services in background...${RESET}"
        docker compose -f "$COMPOSE_FILE" up -d
        show_urls
        echo -e "Run ${BOLD}./docker-dev.sh logs${RESET} to inspect live output."
        ;;

    backend)
        print_banner
        echo -e "${CYAN}Starting Qdrant & FastAPI backend only...${RESET}"
        docker compose -f "$COMPOSE_FILE" up qdrant api
        ;;

    down)
        print_banner
        echo -e "${YELLOW}Stopping and removing development containers...${RESET}"
        docker compose -f "$COMPOSE_FILE" down
        echo -e "${GREEN}Services stopped successfully.${RESET}"
        ;;

    restart)
        print_banner
        echo -e "${YELLOW}Restarting development services...${RESET}"
        docker compose -f "$COMPOSE_FILE" down
        docker compose -f "$COMPOSE_FILE" up -d
        show_urls
        ;;

    build)
        print_banner
        echo -e "${CYAN}Rebuilding development Docker containers...${RESET}"
        docker compose -f "$COMPOSE_FILE" build --no-cache
        echo -e "${GREEN}Containers built successfully. Launch with ./docker-dev.sh up${RESET}"
        ;;

    logs)
        SERVICE="$2"
        if [ -n "$SERVICE" ]; then
            docker compose -f "$COMPOSE_FILE" logs -f "$SERVICE"
        else
            docker compose -f "$COMPOSE_FILE" logs -f
        fi
        ;;

    shell)
        SERVICE="${2:-api}"
        echo -e "${CYAN}Connecting to ${SERVICE} container shell...${RESET}"
        docker compose -f "$COMPOSE_FILE" exec "$SERVICE" /bin/bash 2>/dev/null || docker compose -f "$COMPOSE_FILE" exec "$SERVICE" /bin/sh
        ;;

    eval)
        print_banner
        echo -e "${CYAN}Running 6-baseline evaluation inside API container...${RESET}"
        docker compose -f "$COMPOSE_FILE" exec api python3 -m eval.runners.run_benchmarks
        ;;

    help|--help|-h)
        show_help
        ;;

    *)
        echo -e "${RED}[ERROR] Unknown command: $COMMAND${RESET}"
        show_help
        exit 1
        ;;
esac
