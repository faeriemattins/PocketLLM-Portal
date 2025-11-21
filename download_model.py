import os
from huggingface_hub import hf_hub_download

MODEL_REPO = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
MODEL_FILENAME = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
DEST_DIR = "models"
DEST_FILENAME = "model.gguf"

def download_model():
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
    
    print(f"Downloading {MODEL_FILENAME} from {MODEL_REPO}...")
    model_path = hf_hub_download(
        repo_id=MODEL_REPO,
        filename=MODEL_FILENAME,
        local_dir=DEST_DIR
    )
    
    # Rename to generic name for easier loading
    final_path = os.path.join(DEST_DIR, DEST_FILENAME)
    if os.path.exists(final_path):
        os.remove(final_path)
    os.rename(model_path, final_path)
    print(f"Model downloaded and saved to {final_path}")

if __name__ == "__main__":
    download_model()
