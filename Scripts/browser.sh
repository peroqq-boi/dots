#!/bin/bash

# Start the server in the background
python /home/user721/.config/browser/server.py &

# Get the PID of the running server process
SERVER_PID=$!

# Start Firefox
librewolf

# Monitor the Firefox process
while pgrep -x "librewolf" > /dev/null; do
    sleep 2  # Wait for Firefox to close
done

# After Firefox is closed, stop the server
kill $SERVER_PID
echo "The server has been stopped because Firefox has been closed."
