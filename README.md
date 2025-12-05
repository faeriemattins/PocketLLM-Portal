# PocketLLM Portal

PocketLLM Portal is a local LLM interface that allows you to interact with GGUF models using a React frontend and a FastAPI backend.

## 🚀 Quick Start (Docker)

The easiest way to run the application is using Docker. This will set up both the backend and frontend services for you.

### Prerequisites
- **Docker** and **Docker Compose** installed on your machine.

### Running the App

1.  **Build and Start**:
    ```bash
    docker-compose up --build
    ```
    *Note: The first build may take a few minutes as it compiles `llama-cpp-python`.*

2.  **Access the App**:
    - **Frontend**: [http://localhost:3000](http://localhost:3000)
    - **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

3.  **Stop the App**:
    Press `Ctrl+C` in the terminal or run:
    ```bash
    docker-compose down
    ```

---

## 🛠️ Local Development Setup

If you prefer to run the services locally for development, follow these steps.

### Prerequisites
- **Python**: 3.10 or higher
- **Node.js**: 18 or higher

### 1. Backend Setup

It is recommended to use a virtual environment.

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Download Model

The application requires a local GGUF model.

```bash
# Ensure venv is activated
python download_model.py
```
This downloads `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` to the `models/` directory.

### 3. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 4. Running Locally

You will need two terminal windows.

**Terminal 1: Backend**
```bash
source venv/bin/activate
uvicorn backend.main:app --reload
# Backend runs at http://localhost:8000
```

**Terminal 2: Frontend**
```bash
cd frontend
npm run dev
# Frontend runs at http://localhost:5173
```

---

## 🧰 Utility Scripts

The project includes helper scripts to manage and inspect the application cache.

### Inspect Cache (`inspect_cache.py`)
View the contents of the SQLite cache database directly in your terminal.

```bash
python inspect_cache.py
```
This will print the tables, schema, and rows found in `cache/cache.db`.

### Export Cache (`export_cache_to_md.py`)
Export the cache contents to a Markdown file for easier reading or sharing.

```bash
python export_cache_to_md.py
```
This creates a `cache_contents.md` file containing a table of cache entries and their full values.
