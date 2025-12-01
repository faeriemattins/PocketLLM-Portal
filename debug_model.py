import os
try:
    from llama_cpp import Llama
    print("llama-cpp-python imported successfully")
except ImportError:
    print("llama-cpp-python NOT found")
    exit(1)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "backend", "models")
# Find a model
model_path = None
if os.path.exists(MODEL_DIR):
    files = [f for f in os.listdir(MODEL_DIR) if f.endswith(".gguf")]
    if files:
        model_path = os.path.join(MODEL_DIR, files[0])

if not model_path:
    print("No model found")
    exit(1)

print(f"Loading model: {model_path}")
llm = Llama(model_path=model_path, verbose=False)

print("Generating title...")
response = llm.create_chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
    temperature=0.7,
    max_tokens=10
)

print(f"Response type: {type(response)}")
print(f"Response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")

if isinstance(response, dict):
    choices = response.get('choices')
    print(f"Choices type: {type(choices)}")
    try:
        print(f"Choices[0]: {choices[0]}")
    except TypeError as e:
        print(f"Error accessing choices[0]: {e}")
