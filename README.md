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

---

# Containerization Walkthrough

I have containerized the PocketLLM Portal application using Docker and Docker Compose. This allows you to run the entire application (backend and frontend) with a single command.

## Changes

### Backend
- Created `backend/Dockerfile` using `python:3.10-slim`.
- Added system dependencies (`build-essential`, `cmake`, `gcc`) required for `llama-cpp-python`.
- Configured to run with `uvicorn` on port 8000.

### Frontend
- Created `frontend/Dockerfile` using a multi-stage build.
- **Stage 1**: Builds the React application using `node:18-alpine`.
- **Stage 2**: Serves the built static files using `nginx:alpine`.
- Configured to expose port 80.

### Orchestration
- Created `docker-compose.yml` in the root directory.
- Maps backend port 8000 to host port 8000.
- Maps frontend port 80 to host port 3000.
- Sets up a volume for the backend to persist data and allow for development updates.

## Verification Results

### Automated Tests
- Ran `docker-compose up --build` to initiate the build process.
- Verified that system dependencies are installed correctly.
- **Note**: The build process for `llama-cpp-python` can take several minutes to complete as it compiles from source.

### Manual Verification
Once the build completes, you can verify the application by accessing:
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Next Steps
1.  Run `docker-compose up --build` to start the application.
2.  Wait for the build to complete (this may take a while for the first time).
3.  Access the application in your browser.
