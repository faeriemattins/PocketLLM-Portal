import os
from huggingface_hub import hf_hub_download
import sys

MODELS = {
    "1": {
        "name": "TinyLlama-1.1B-Chat",
        "repo": "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
        "filename": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    },
    "2": {
        "name": "Phi-2",
        "repo": "TheBloke/phi-2-GGUF",
        "filename": "phi-2.Q4_K_M.gguf"
    },
    "3": {
        "name": "Qwen1.5-1.8B-Chat",
        "repo": "Qwen/Qwen1.5-1.8B-Chat-GGUF",
        "filename": "qwen1.5-1.8b-chat-q4_k_m.gguf"
    },
    "4": {
        "name": "Qwen2.5-0.5B-Instruct",
        "repo": "Qwen/Qwen2.5-0.5B-Instruct-GGUF",
        "filename": "qwen2.5-0.5b-instruct-q4_k_m.gguf"
    },
    "5": {
        "name": "Qwen2.5-1.5B-Instruct",
        "repo": "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        "filename": "qwen2.5-1.5b-instruct-q4_k_m.gguf"
    }
}

DEST_DIR = "models"

def download_model(choice):
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
    
    model = MODELS.get(choice)
    if not model:
        print("Invalid choice.")
        return

    print(f"Downloading {model['name']}...")
    try:
        hf_hub_download(
            repo_id=model['repo'],
            filename=model['filename'],
            local_dir=DEST_DIR,
            local_dir_use_symlinks=False
        )
        print(f"Successfully downloaded {model['filename']}")
    except Exception as e:
        print(f"Error downloading {model['name']}: {e}")

def main():
    print("Available Models:")
    for key, model in MODELS.items():
        print(f"{key}. {model['name']}")
    print("A. Download All")
    
    choice = input("Enter your choice (1-3 or A): ").strip().upper()
    
    if choice == 'A':
        for key in MODELS:
            download_model(key)
    elif choice in MODELS:
        download_model(choice)
    else:
        print("Invalid selection.")

if __name__ == "__main__":
    main()
