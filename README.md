# PocketLLM Portal - Execution Guide

This guide provides step-by-step instructions on how to set up and run the PocketLLM Portal application.

## Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18 or higher
- **npm**: Included with Node.js

## Setup

### 1. Backend Setup

It is recommended to use a virtual environment for the backend dependencies.

```bash
# Create a virtual environment (if you haven't already)
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 2. Download the Model

The application requires a local GGUF model to function. Run the provided script to download it.

```bash
# Make sure your virtual environment is activated
python download_model.py
```
This will download `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` to the `models/` directory.

### 3. Frontend Setup

Install the Node.js dependencies for the frontend.

```bash
cd frontend
npm install
cd ..
```

## Running the Application

You will need two terminal windows to run the application (one for the backend, one for the frontend).

### Terminal 1: Backend

From the project root directory:

```bash
# Ensure venv is activated
source venv/bin/activate

# Run the FastAPI server
uvicorn backend.main:app --reload
```
The backend will start at `http://localhost:8000`.

### Terminal 2: Frontend

From the project root directory:

```bash
cd frontend
npm run dev
```
The frontend will start at `http://localhost:5173` (or similar, check the output).

## Accessing the App

Open your browser and navigate to the URL shown in the Frontend terminal (usually `http://localhost:5173`).
