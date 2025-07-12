from flask import Flask, render_template
from app.webhook import create_app
import os

# Explicit template folder path
TEMPLATE_DIR = os.path.abspath('templates')

app = create_app(template_folder=TEMPLATE_DIR)

@app.route('/')

def home():
    return render_template("index.html")

for rule in app.url_map.iter_rules():
    print(rule)

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')
