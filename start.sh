#!/bin/bash

# Home-IO Start Script

# Determine the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Function to print colored output
print_message() {
  local color=$1
  local message=$2
  
  if [ -t 1 ]; then
    case "$color" in
      "green") echo -e "\033[0;32m$message\033[0m" ;;
      "red") echo -e "\033[0;31m$message\033[0m" ;;
      "yellow") echo -e "\033[0;33m$message\033[0m" ;;
      "blue") echo -e "\033[0;34m$message\033[0m" ;;
      *) echo "$message" ;;
    esac
  else
    echo "$message"
  fi
}

# Create necessary directories
mkdir -p config data data/backups

# Check for Python virtual environment
if [ ! -d "venv" ]; then
  print_message "yellow" "Virtual environment not found. Creating one..."
  
  if command_exists python3; then
    python3 -m venv venv
  elif command_exists python; then
    python -m venv venv
  else
    print_message "red" "Error: Python not found. Please install Python 3.10 or higher."
    exit 1
  fi
  
  print_message "green" "Virtual environment created successfully."
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
print_message "blue" "Installing/updating Python dependencies..."
pip install -r requirements.txt

# Check for frontend dependencies
if [ -d "home-io-test" ]; then
  cd home-io-test
  
  if [ ! -d "node_modules" ]; then
    print_message "yellow" "Frontend dependencies not found. Installing..."
    
    if command_exists npm; then
      npm install
    else
      print_message "red" "Warning: npm not found. Skipping frontend dependencies."
    fi
  fi
  
  cd ..
fi

# Start the backend server
print_message "green" "Starting Home-IO backend server..."
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Check if backend started successfully
if ! ps -p $BACKEND_PID > /dev/null; then
  print_message "red" "Error: Backend server failed to start."
  exit 1
fi

print_message "green" "Backend server started successfully (PID: $BACKEND_PID)."

# Start the frontend development server if npm is available
if command_exists npm && [ -d "home-io-test" ]; then
  print_message "blue" "Starting frontend development server..."
  
  cd home-io-test
  npm start &
  FRONTEND_PID=$!
  
  print_message "green" "Frontend server started (PID: $FRONTEND_PID)."
  cd ..
else
  print_message "yellow" "Skipping frontend server (npm not found or frontend directory missing)."
fi

# Print access information
print_message "blue" "========================================================"
print_message "green" "Home-IO system is running!"
print_message "blue" "========================================================"
print_message "yellow" "Access the API at: http://localhost:8000"
print_message "yellow" "API documentation: http://localhost:8000/docs"
print_message "yellow" "Frontend: http://localhost:3000"
print_message "blue" "========================================================"

# Function to handle termination
cleanup() {
  print_message "yellow" "Shutting down Home-IO..."
  
  # Kill backend
  if [ -n "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null
    print_message "green" "Backend server stopped."
  fi
  
  # Kill frontend
  if [ -n "$FRONTEND_PID" ]; then
    kill $FRONTEND_PID 2>/dev/null
    print_message "green" "Frontend server stopped."
  fi
  
  print_message "green" "Home-IO shutdown complete."
  exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Wait for user to press Ctrl+C
print_message "yellow" "Press Ctrl+C to stop the servers."
wait