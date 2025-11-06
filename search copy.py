from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the dataset
DATASET_PATH = "recipes_data.csv"
recipes_df = pd.read_csv(DATASET_PATH)

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