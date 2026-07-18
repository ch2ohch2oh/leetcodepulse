#!/bin/bash
set -e

case "${1:-}" in
    *Username*)
        printf '%s\n' "x-access-token"
        ;;
    *Password*)
        if [ -z "${GITHUB_TOKEN:-}" ]; then
            echo "GITHUB_TOKEN is required" >&2
            exit 1
        fi
        printf '%s\n' "$GITHUB_TOKEN"
        ;;
    *)
        echo "Unsupported credential prompt" >&2
        exit 1
        ;;
esac
