from flask import Flask, request, jsonify
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

# Define available models
MODELS = {
    "chemistry-t5": "GT4SD/multitask-text-and-chemistry-t5-base-augm",
    "blenderbot": "facebook/blenderbot-400M-distill",
    "flan-t5": "google/flan-t5-small"
}

# Load default model
default_model_name = MODELS["chemistry-t5"]
tokenizer = AutoTokenizer.from_pretrained(default_model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(default_model_name)

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Flask API
app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate_response():
    data = request.json
    user_input = data.get("message", "")
    selected_model = data.get("model", "chemistry-t5")  # Default to chemistry model

    if selected_model not in MODELS:
        return jsonify({"error": "Invalid model name. Choose from: " + ", ".join(MODELS.keys())}), 400

    # Load the requested model dynamically
    model_name = MODELS[selected_model]
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)

    # Encode input and generate response
    inputs = tokenizer(user_input, return_tensors="pt").to(device)
    output_tokens = model.generate(**inputs)
    output_text = tokenizer.decode(output_tokens[0], skip_special_tokens=True)

    return jsonify({"response": output_text})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
