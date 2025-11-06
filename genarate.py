from flask import Flask, render_template, request, jsonify
from model import load_models, generate_recipe, load_tokenizer
import os

app = Flask(__name__)

# Load tokenizer and models from local storage
tokenizer_path = "model/tokenizer.json"
encoder_path = "model/encoder_model.h5"
decoder_path = "model/decoder_model.h5"

if not os.path.exists(tokenizer_path):
    raise FileNotFoundError(f"Tokenizer file not found: {tokenizer_path}")
if not os.path.exists(encoder_path):
    raise FileNotFoundError(f"Encoder model file not found: {encoder_path}")
if not os.path.exists(decoder_path):
    raise FileNotFoundError(f"Decoder model file not found: {decoder_path}")

tokenizer = load_tokenizer(tokenizer_path)
encoder_model, decoder_model = load_models(encoder_path, decoder_path)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    ingredients = data.get("ingredients", "")
    if not ingredients:
        return jsonify({"error": "No ingredients provided"}), 400
    
    recipe = generate_recipe(ingredients, tokenizer, encoder_model, decoder_model)
    return jsonify({"recipe": recipe})

if __name__ == '__main__':
    app.run(debug=True)
