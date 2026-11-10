import logging
import os

import requests
import torch
from flask import Flask, jsonify, request
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Local CPU/GPU-friendly Hugging Face models matched with the React UI selector
HUGGINGFACE_MODELS = {
    "flan-t5": "google/flan-t5-small",
    "distil-gpt2": "distilgpt2",
    "tiny-llama": "TinyLlama/TinyLlama-1.1B-Chat-v0.3",
    "phi-2": "microsoft/phi-2",
    "gpt2": "gpt2",
}

DEFAULT_HUGGINGFACE_MODEL = "flan-t5"
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434/api/generate")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "80"))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# In-memory cache of loaded (tokenizer, model) pairs keyed by Hugging Face repo ID
model_cache: dict[str, tuple] = {}


def is_seq2seq_model(model_repo_id: str) -> bool:
    """Return True for encoder-decoder architectures (e.g. T5) vs decoder-only Causal LMs."""
    return "t5" in model_repo_id.lower()


def load_huggingface_model(model_repo_id: str):
    """Load a Hugging Face tokenizer and model in eval mode, caching in memory for subsequent requests."""
    if model_repo_id not in model_cache:
        logger.info("Loading Hugging Face model: %s on %s", model_repo_id, device)
        tokenizer = AutoTokenizer.from_pretrained(model_repo_id)
        if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
            tokenizer.pad_token_id = tokenizer.eos_token_id

        model_class = AutoModelForSeq2SeqLM if is_seq2seq_model(model_repo_id) else AutoModelForCausalLM
        model = model_class.from_pretrained(
            model_repo_id,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
        ).to(device)
        model.eval()
        model_cache[model_repo_id] = (tokenizer, model)
    return model_cache[model_repo_id]


def generate_with_huggingface(prompt: str, selected_model: str) -> str:
    """Generate a response using a locally cached Hugging Face model."""
    if selected_model not in HUGGINGFACE_MODELS:
        valid_models = ", ".join(HUGGINGFACE_MODELS.keys())
        raise ValueError(f"Invalid Hugging Face model. Choose from: {valid_models}")

    model_repo_id = HUGGINGFACE_MODELS[selected_model]
    tokenizer, model = load_huggingface_model(model_repo_id)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        output_tokens = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            num_beams=1,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            pad_token_id=tokenizer.pad_token_id,
        )

    sequence = output_tokens[0]
    # Decoder-only Causal LMs prepend the input prompt tokens to the output sequence
    if not is_seq2seq_model(model_repo_id) and "input_ids" in inputs:
        input_length = inputs["input_ids"].shape[-1]
        if len(sequence) > input_length:
            sequence = sequence[input_length:]

    return tokenizer.decode(sequence, skip_special_tokens=True).strip()


def generate_with_ollama(prompt: str, selected_model: str) -> str:
    """Generate a response by forwarding the prompt to a local Ollama server."""
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
    return response.json().get("response", "").strip()


app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "status": "running",
            "service": "Local Multi-Model AI Assistant",
            "device": str(device),
            "backends": ["huggingface", "ollama"],
            "huggingface_models": list(HUGGINGFACE_MODELS.keys()),
        }
    )


@app.route("/generate", methods=["POST"])
def generate_response():
    data = request.get_json(silent=True) or {}
    user_input = (data.get("message") or "").strip()
    backend = (data.get("backend") or "huggingface").strip().lower()

    if not user_input:
        return jsonify({"error": "Message input is empty."}), 400

    try:
        if backend == "ollama":
            selected_model = (data.get("model") or DEFAULT_OLLAMA_MODEL).strip()
            output_text = generate_with_ollama(user_input, selected_model)
        elif backend == "huggingface":
            selected_model = (data.get("model") or DEFAULT_HUGGINGFACE_MODEL).strip()
            output_text = generate_with_huggingface(user_input, selected_model)
        else:
            return jsonify({"error": "Invalid backend. Choose 'huggingface' or 'ollama'."}), 400
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except requests.RequestException as error:
        return jsonify({"error": f"Ollama request failed: {error}"}), 502

    return jsonify({"response": output_text, "backend": backend, "model": selected_model})


if __name__ == "__main__":
    debug_enabled = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    app.run(host="127.0.0.1", port=5001, debug=debug_enabled)
