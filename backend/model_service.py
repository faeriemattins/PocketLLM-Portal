import os
from llama_cpp import Llama
from typing import Generator

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "model.gguf")

class ModelService:
    def __init__(self):
        self.llm = None

    def load_model(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Please run download_model.py first.")
        
        # Initialize Llama model with CPU settings
        # n_ctx=2048 is a reasonable default for small models
        self.llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=2048,
            n_threads=os.cpu_count(), # Use all available cores
            verbose=True
        )
        print("Model loaded successfully.")

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
