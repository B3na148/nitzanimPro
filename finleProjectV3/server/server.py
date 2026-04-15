from flask import Flask, request
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow requests from the Chrome extension

SAVE_FOLDER = "history_data"
os.makedirs(SAVE_FOLDER, exist_ok=True)  # Create folder if it doesn't exist


@app.route('/save-history', methods=['POST'])
def save_history():
    data = request.get_json()

    # Create a unique filename using timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SAVE_FOLDER}/history_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    return {"status": "saved", "file": filename}, 200
    #run categorization.py
    os.system("python categorization.py")

if __name__ == '__main__':
    app.run(port=5000)