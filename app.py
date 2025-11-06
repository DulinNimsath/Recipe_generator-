from flask import Flask, render_template, request, jsonify
from model import load_tokenizer, load_models, generate_recipe
from search import recipes_df
import os

app = Flask(__name__)

# Paths to models and tokenizer
TOKENIZER_PATH = os.path.join("Model", "tokenizer.json")
ENCODER_MODEL_PATH = os.path.join("Model", "encoder_model.h5")
DECODER_MODEL_PATH = os.path.join("Model", "decoder_model.h5")

# Load tokenizer and models
tokenizer = load_tokenizer(TOKENIZER_PATH)
encoder_model, decoder_model = load_models(ENCODER_MODEL_PATH, DECODER_MODEL_PATH)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        ingredients = request.form.get('ingredients', '')
        if not ingredients:
            return jsonify({'error': 'No ingredients provided'}), 400

        # Generate recipe
        recipe = generate_recipe(ingredients, tokenizer, encoder_model, decoder_model)
        return jsonify({'recipe': recipe})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = None
    results = None
    if request.method == 'POST':
        query = request.form.get('recipe_name', '').lower()
        if query:
            # Filter recipes based on the query
            results = recipes_df[recipes_df['name'].str.contains(query, case=False, na=False)]
    return render_template('search.html', query=query, recipes=results)

if __name__ == '__main__':
    app.run(debug=True)