#!/bin/bash
# start_agent.sh
# --------------------------------------------------------------------------
# ADK Web Launch Script: Local Persistence Mode (SQLite Session / File Artifacts)
# Includes automatic opening of the web UI with proper wait for server readiness.
# --------------------------------------------------------------------------

# --- HELPER FUNCTION ---
# Function to print a clean 65-character separator line using pure Bash 4+ idiom.
print_separator() {
    # The {1..65} creates a sequence of 65 numbers.
    # The printf then prints the dash character for each number, effectively repeating it.
    printf '%0.s-' {1..65}
    echo "" # Add a newline
}

# --- 1. ENSURE DIRECTORIES EXIST ---
# Make sure the artifact and session directories exist and are writable
PROJECT_ROOT="$PWD"
mkdir -p "$PROJECT_ROOT/.adk/artifacts"
mkdir -p "$PROJECT_ROOT/.adk"
chmod 755 "$PROJECT_ROOT/.adk"

# --- 2. CONFIGURATION: CUSTOM URIs ---
# Session Service URI (Database):
# Using 'sqlite://<path>' for local, persistent chat session history.
# This is a robust, local database solution.
# NOTE: Requires the 'sqlite' dependency to be installed!
SESSION_URI="sqlite:///$PROJECT_ROOT/.adk/sessions.sqlite"

# Artifact Service URI (Local File System):
# Using 'file://<path>' to store all generated non-text data (images, files)
# in a custom local directory.
ARTIFACT_URI="file:///$PROJECT_ROOT/.adk/artifacts"

# --- 3. EXECUTION LOGIC ---
print_separator
# Launch message with info on session and artifact persistence
echo "🚀 Launching ADK Web Environment for Agent Package: src/learning_mate"
echo "Persistence Mode: SQLite DB (Session) + Local Disk (Artifacts)"
print_separator
echo "SESSION_SERVICE_URI: $SESSION_URI"
echo "ARTIFACT_SERVICE_URI: $ARTIFACT_URI"
print_separator

# --- 4. START ADK WEB SERVER ---
# Run ADK web server in the background so we can open the browser later
adk web "src" \
    --session_service_uri "$SESSION_URI" \
    --artifact_service_uri "$ARTIFACT_URI" &

# Capture the background PID to wait for later
ADK_PID=$!

# --- 5. WAIT FOR SERVER TO BE READY ---
# Use curl to poll the dev-ui endpoint until it responds
ADK_URL="http://127.0.0.1:8000/dev-ui/?app=learning_mate"
MAX_WAIT=30
SECONDS_WAITED=0
echo "Waiting for ADK Web Server to be ready..."
until curl -s --head --request GET "$ADK_URL" | grep "200\|301\|302" > /dev/null; do
    sleep 1
    SECONDS_WAITED=$((SECONDS_WAITED+1))
    if [ $SECONDS_WAITED -ge $MAX_WAIT ]; then
        echo "⚠️ Server did not respond after $MAX_WAIT seconds. Opening browser anyway..."
        break
    fi
done
echo "✅ ADK Web Server is ready."

# --- 6. OPEN DEFAULT BROWSER TO THE FIXED ADK DEV-UI URL ---
# Detect the OS/browser command and open the URL
if command -v xdg-open >/dev/null; then
    # Linux default
    xdg-open "$ADK_URL"
elif command -v open >/dev/null; then
    # macOS default
    open "$ADK_URL"
elif command -v start >/dev/null; then
    # Windows default
    start "$ADK_URL"
else
    # Fallback if no browser opener detected
    echo "ADK Web launched! Open your browser at $ADK_URL"
fi

# --- 7. WAIT FOR ADK SERVER TO EXIT ---
# Keep the script running until the ADK process ends
wait $ADK_PID

print_separator
echo "ADK Web Server has exited."
print_separator
