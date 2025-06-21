#!/bin/bash
ROOT_DIR="$(pwd)"
x-terminal-emulator --title="Server" -- bash -c "cd \"$ROOT_DIR\" && python3 -m server.server; exec bash"
x-terminal-emulator --title="Client 1" -- bash -c "cd \"$ROOT_DIR\" && python3 -m client.client; exec bash"
x-terminal-emulator --title="Client 2" -- bash -c "cd \"$ROOT_DIR\" && python3 -m client.client; exec bash"
