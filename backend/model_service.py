import os
from llama_cpp import Llama
from typing import Generator

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
DEFAULT_MODEL_PATH = os.path.join(MODEL_DIR, "model.gguf")

class ModelService:
    def __init__(self):
        self.llm = None
        self.current_model_path = DEFAULT_MODEL_PATH
        if not os.path.exists(MODEL_DIR):
            os.makedirs(MODEL_DIR)

    def list_models(self):
        if not os.path.exists(MODEL_DIR):
            return []
        return [f for f in os.listdir(MODEL_DIR) if f.endswith(".gguf")]

    def set_model(self, model_filename: str):
        new_path = os.path.join(MODEL_DIR, model_filename)
        if not os.path.exists(new_path):
            raise FileNotFoundError(f"Model {model_filename} not found")
        
        self.current_model_path = new_path
        # Reload model if it's already loaded
        if self.llm:
            self.load_model()

    def load_model(self):
        # If current path doesn't exist, try to find any .gguf file in models dir
        if not os.path.exists(self.current_model_path):
            models = self.list_models()
            if models:
                self.current_model_path = os.path.join(MODEL_DIR, models[0])
            else:
                # If still no model, check for default or raise error
                if os.path.exists(DEFAULT_MODEL_PATH):
                    self.current_model_path = DEFAULT_MODEL_PATH
                else:
                    raise FileNotFoundError(f"No models found in {MODEL_DIR}. Please run download_model.py first.")
        
        # Initialize Llama model with CPU settings
        # n_ctx=2048 is a reasonable default for small models
        self.llm = Llama(
            model_path=self.current_model_path,
            n_ctx=2048,
            n_threads=os.cpu_count(), # Use all available cores
            verbose=True
        )
        print(f"Model loaded successfully: {os.path.basename(self.current_model_path)}")

    def stream_chat(self, messages: list, temperature: float = 0.7) -> Generator[str, None, None]:
        if not self.llm:
            self.load_model()
        
        # Convert messages to prompt format if needed, but llama-cpp-python's create_chat_completion handles it
        stream = self.llm.create_chat_completion(
            messages=messages,
            temperature=temperature,
            stream=True
        )

        for chunk in stream:
            delta = chunk['choices'][0]['delta']
            if 'content' in delta:
                yield delta['content']

    def generate_title(self, user_message: str) -> str:
        if not self.llm:
            self.load_model()
        
        prompt = f"Generate a short, concise title (3-5 words) for a chat session that starts with this message: '{user_message}'. Do not use quotes. Title:"
        
        response = self.llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=20
        )
        
        title = response['choices'][0]['message']['content'].strip()
        # Remove any surrounding quotes if the model adds them despite instructions
        title = title.strip('"').strip("'")
        return title

model_service = ModelService()
