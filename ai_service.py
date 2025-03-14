from flask import Flask, request, jsonify
from flask_cors import CORS  # 🚀 Add this import
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, AutoModelForCausalLM
import torch

# Define available models (CPU-friendly)
MODELS = {
    "flan-t5": "google/flan-t5-small",
    "distil-gpt2": "distilgpt2",
    "tiny-llama": "TinyLlama/TinyLlama-1.1B-Chat-v0.3",
    "phi-2": "microsoft/phi-2",
    "gpt2": "gpt2",
    "llama-2": "meta-llama/Llama-2-13b-hf"
}

# Set up device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Cache for loaded models and tokenizers
model_cache = {}

def load_model(model_name):
    """Load model and tokenizer, caching for efficiency."""
    if model_name not in model_cache:
        print(f"🔄 Loading model: {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = (
            AutoModelForSeq2SeqLM.from_pretrained(
                model_name, torch_dtype=torch.float32, low_cpu_mem_usage=True
            ) if "t5" in model_name else AutoModelForCausalLM.from_pretrained(
                model_name, torch_dtype=torch.float32, low_cpu_mem_usage=True
            )
        ).to(device)
        model_cache[model_name] = (tokenizer, model)
    return model_cache[model_name]

# Flask API setup
app = Flask(__name__)
CORS(app)  # 🚀 Enable CORS for all routes

@app.route("/", methods=["GET"])
def home():
    return "🚀 Local AI Chatbot is running!"

@app.route("/generate", methods=["POST"])
def generate_response():
    data = request.json
    user_input = data.get("message", "").strip()
    selected_model = data.get("model", "flan-t5").strip()

    # Input validation
    if not user_input:
        return jsonify({"error": "Message input is empty."}), 400
    if selected_model not in MODELS:
        return jsonify({"error": f"Invalid model name. Choose from: {', '.join(MODELS.keys())}"}), 400

    # Load and use the selected model
    model_name = MODELS[selected_model]
    tokenizer, model = load_model(model_name)

    # Process input and generate output
    inputs = tokenizer(user_input, return_tensors="pt").to(device)
    output_tokens = model.generate(
        **inputs,
        max_new_tokens=50,
        num_beams=1,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        early_stopping=True
    )
    output_text = tokenizer.decode(output_tokens[0], skip_special_tokens=True)

    return jsonify({"response": output_text})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
