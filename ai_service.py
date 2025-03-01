from flask import Flask, request, jsonify
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

# Load the T5 Model
model_name = "GT4SD/multitask-text-and-chemistry-t5-base-augm"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Initialize Flask
app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate_response():
    data = request.json
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"response": "No input provided."}), 400

    # Encode input and generate response
    inputs = tokenizer(user_input, return_tensors="pt").to(device)
    output_tokens = model.generate(**inputs)
    output_text = tokenizer.decode(output_tokens[0], skip_special_tokens=True)

    return jsonify({"response": output_text})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
