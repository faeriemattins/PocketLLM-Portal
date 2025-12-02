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

    def stream_chat(self, messages: list, temperature: float = 0.7, top_p: float = 0.9, max_tokens: int = 2048, system_prompt: str = None) -> Generator[str, None, None]:
        if not self.llm:
            self.load_model()
        
        # Create a copy to avoid mutating the original
        messages_copy = list(messages)
        
        # Debug logging
        print(f"[DEBUG] System prompt received: {system_prompt}")
        print(f"[DEBUG] Messages before: {messages_copy}")
        
        # Prepend system prompt if provided and not already present
        if system_prompt:
            if not messages_copy or messages_copy[0].get('role') != 'system':
                messages_copy.insert(0, {"role": "system", "content": system_prompt})
                print(f"[DEBUG] System prompt ADDED to messages")
            else:
                print(f"[DEBUG] System message already present, skipping")
        else:
            print(f"[DEBUG] No system prompt provided")
        
        print(f"[DEBUG] Messages after: {messages_copy}")
        print(f"[DEBUG] Temperature: {temperature}, Top-P: {top_p}, Max Tokens: {max_tokens}")
        
        stream = self.llm.create_chat_completion(
            messages=messages_copy,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
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
