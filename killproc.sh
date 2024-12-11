#!/bin/sh

# Function to display help message
display_help() {
  echo "Usage: $0 [options] <process_name>"
  echo ""
  echo "Options:"
  echo "  -help       Display this help message."
  echo "  -dry        Display the processes that would be killed without actually killing them."
  echo ""
  echo "Arguments:"
  echo "  process_name     Name of the process to kill."
}

# Check for help argument
if [ "$1" = "-help" ]; then
  display_help
  exit 0
fi

# Ensure at least one argument is provided
if [ -z "$1" ]; then
  echo "Error: Missing required argument."
  display_help
  exit 1
fi

# Check for dry run option
DRY_RUN=false
if [ "$1" = "-dry" ]; then
  DRY_RUN=true
  shift
fi

# Assign the process name from the argument
PROCESS_NAME=$1

# Get the current user
CURRENT_USER=$(whoami)

# Find the PID(s) of the process owned by the current user
PIDS=$(pgrep -u "$CURRENT_USER" -f "$PROCESS_NAME")

# Check if the process is running
if [ -z "$PIDS" ]; then
  echo "No process found with name: $PROCESS_NAME owned by user: $CURRENT_USER"
  exit 0
fi

# Display found PIDs
echo "Found process(es) with name '$PROCESS_NAME' owned by user '$CURRENT_USER': $PIDS"

# If dry run, display the processes that would be killed and exit
if [ "$DRY_RUN" = true ]; then
  echo "Dry run: The following process(es) would be killed: $PIDS"
  exit 0
fi

# Kill the process(es)
kill -9 $PIDS

if [ $? -eq 0 ]; then
  echo "Successfully killed process(es): $PIDS"
else
  echo "Failed to kill process(es): $PIDS"
fi