#!/bin/bash
ROOT_DIR="$(pwd)"
gnome-terminal --title="Server" -- bash -c "cd \"$ROOT_DIR\" && python3 -m server.server; exec bash"
gnome-terminal --title="Client 1" -- bash -c "cd \"$ROOT_DIR\" && python3 -m client.client; exec bash"
gnome-terminal --title="Client 2" -- bash -c "cd \"$ROOT_DIR\" && python3 -m client.client; exec bash"
