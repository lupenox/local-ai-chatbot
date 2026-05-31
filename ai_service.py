import os

import requests
import torch
from flask import Flask, jsonify, request
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer

# Define available Hugging Face models (CPU-friendly)
HUGGINGFACE_MODELS = {
    "flan-t5": "google/flan-t5-small",
    "distil-gpt2": "distilgpt2",
    "tiny-llama": "TinyLlama/TinyLlama-1.1B-Chat-v0.3",
    "phi-2": "microsoft/phi-2",
    "gpt2": "gpt2",
    "llama-2": "meta-llama/Llama-2-13b-hf",
}

DEFAULT_HUGGINGFACE_MODEL = "flan-t5"
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434/api/generate")

# Set up device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Cache for loaded Hugging Face models and tokenizers
model_cache = {}


def load_huggingface_model(model_name):
    """Load a Hugging Face model and tokenizer, caching for efficiency."""
    if model_name not in model_cache:
        print(f"Loading Hugging Face model: {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model_class = AutoModelForSeq2SeqLM if "t5" in model_name else AutoModelForCausalLM
        model = model_class.from_pretrained(
            model_name,
            dtype=torch.float32,
            low_cpu_mem_usage=True,
        ).to(device)
        model_cache[model_name] = (tokenizer, model)
    return model_cache[model_name]


def generate_with_huggingface(prompt, selected_model):
    """Generate text with a locally loaded Hugging Face model."""
    if selected_model not in HUGGINGFACE_MODELS:
        valid_models = ", ".join(HUGGINGFACE_MODELS.keys())
        raise ValueError(f"Invalid Hugging Face model. Choose from: {valid_models}")

    model_name = HUGGINGFACE_MODELS[selected_model]
    tokenizer, model = load_huggingface_model(model_name)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    output_tokens = model.generate(
        **inputs,
        max_new_tokens=50,
        num_beams=1,
        do_sample=True,
        top_k=50,
        top_p=0.95,
    )
    return tokenizer.decode(output_tokens[0], skip_special_tokens=True)


def generate_with_ollama(prompt, selected_model):
    """Generate text with a locally running Ollama model."""
    response = requests.post(
        OLLAMA_API_URL,
        json={
            "model": selected_model or DEFAULT_OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json().get("response", "")


# Flask API setup
app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "status": "running",
            "service": "Local Multi-Model AI Assistant",
            "backends": ["huggingface", "ollama"],
        }
    )


@app.route("/generate", methods=["POST"])
def generate_response():
    data = request.get_json(silent=True) or {}
    user_input = data.get("message", "").strip()
    backend = data.get("backend", "huggingface").strip().lower()

    if not user_input:
        return jsonify({"error": "Message input is empty."}), 400

    try:
        if backend == "ollama":
            selected_model = data.get("model", DEFAULT_OLLAMA_MODEL).strip()
            output_text = generate_with_ollama(user_input, selected_model)
        elif backend == "huggingface":
            selected_model = data.get("model", DEFAULT_HUGGINGFACE_MODEL).strip()
            output_text = generate_with_huggingface(user_input, selected_model)
        else:
            return jsonify({"error": "Invalid backend. Choose 'huggingface' or 'ollama'."}), 400
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except requests.RequestException as error:
        return jsonify({"error": f"Ollama request failed: {error}"}), 502

    return jsonify({"response": output_text, "backend": backend, "model": selected_model})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
