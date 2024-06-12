from flask import Flask, render_template, request, jsonify
from scripts import scraper, cleaner

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    # Get input from the form
    source = request.form['source']
    destination = request.form['destination']
    # Pass input to the scraper
    scraper.scrape_data(source, destination)
    return jsonify({'message': 'Data scraped successfully!'})

@app.route('/clean', methods=['POST'])
def clean():
    # Call the cleaning function
    cleaner.clean_data()
    return jsonify({'message': 'Data cleaned successfully!'})

@app.route('/result')
def result():
    # Load and display the processed data
    # This might involve loading from cleaned data directory or performing further processing
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)
