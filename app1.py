from flask import Flask, render_template, request, jsonify
from model import load_models, generate_recipe, load_tokenizer
import os
import pyodbc

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

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Generate recipe route
@app.route('/generate', methods=['GET', 'POST'])
def generate():
    recipe = None  # Initialize recipe variable
    if request.method == 'POST':
        # Check if the request is JSON
        if request.is_json:
            data = request.json
        else:
            # Fallback to form data
            data = request.form
        
        ingredients = data.get("ingredients", "")
        if not ingredients:
            return render_template('generate.html', error="No ingredients provided")
        
        # Generate the recipe
        recipe = generate_recipe(ingredients, tokenizer, encoder_model, decoder_model)
    
    # Render the template with the recipe (if generated)
    return render_template('generate.html', recipe=recipe)

# Database connection string
DB_CONNECTION_STRING = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-VOEQVJB;"  # Replace with your server name
    "Database=RecipeDB;"  # Replace with your database name
    "Trusted_Connection=yes;"
)

def search_in_database(query):
    try:
        # Connect to the database
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        # Execute the search query (only select top 100 title, ingredients, and directions)
        sql_query = """
        SELECT TOP 100 title, ingredients, directions
        FROM Recipes
        WHERE title LIKE ?
        """
        cursor.execute(sql_query, f"%{query}%")
        results = cursor.fetchall()

        # Convert results to a list of dictionaries
        recipes = [
            {
                "title": row.title,
                "ingredients": row.ingredients,
                "directions": row.directions,
            }
            for row in results
        ]

        conn.close()
        return recipes
    except Exception as e:
        print(f"Database error: {e}")
        return []

# Search route
@app.route('/search', methods=['GET', 'POST'])
def search():
    query = None
    results = None
    if request.method == 'POST':
        query = request.form.get('recipe_name', '').strip()
        if query:
            # Perform database search
            results = search_in_database(query)

    return render_template('search.html', query=query, recipes=results)

if __name__ == '__main__':
    app.run(debug=True)