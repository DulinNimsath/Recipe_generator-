from flask import Flask, request, render_template_string
import pyodbc

app = Flask(__name__)

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

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = None
    results = None
    if request.method == 'POST':
        query = request.form.get('recipe_name', '').strip()
        if query:
            # Perform database search
            results = search_in_database(query)

    # HTML template with Tailwind CSS
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Recipe Search</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto p-4">
            <h1 class="text-3xl font-bold text-center mb-6">Recipe Search</h1>
            <form method="POST" action="/search" class="flex justify-center mb-6">
                <input 
                    type="text" 
                    name="recipe_name" 
                    placeholder="Enter recipe name" 
                    class="border p-2 w-1/2 rounded-lg" 
                    required>
                <button 
                    type="submit" 
                    class="ml-2 bg-blue-500 text-white p-2 rounded-lg">
                    Search
                </button>
            </form>
            {% if query %}
                <h2 class="text-xl font-semibold mb-4">Results for "{{ query }}":</h2>
                {% if recipes %}
                    <ul class="bg-white p-4 rounded-lg shadow-md">
                        {% for recipe in recipes %}
                            <li class="border-b p-4">
                                <h3 class="text-lg font-bold">{{ recipe['title'] }}</h3>
                                <p><strong>Ingredients:</strong> {{ recipe['ingredients'] }}</p>
                                <p><strong>Directions:</strong> {{ recipe['directions'] }}</p>
                            </li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <p class="text-red-500">No recipes found.</p>
                {% endif %}
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, query=query, recipes=results)

if __name__ == '__main__':
    app.run(debug=True)