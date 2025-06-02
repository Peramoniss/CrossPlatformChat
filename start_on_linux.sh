#!/bin/bash

# Open a terminal and run the server.
gnome-terminal --title="Servidor" -- bash -c "python3 server.py; exec bash"

# Open another terminal for client 1.
gnome-terminal --title="Cliente 1" -- bash -c "python3 client.py; exec bash"

# Open another terminal for client 2.
gnome-terminal --title="Cliente 2" -- bash -c "python3 client.py; exec bash"
