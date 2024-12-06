# flask-server/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib  # or any other model loading library

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes (helpful for cross-origin requests from Electron)

# Load your model (example)
model = joblib.load("../model/your_model.pkl")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    # Process data to fit model requirements
    features = data['features']  # e.g., an array of inputs
    prediction = model.predict([features])
    return jsonify({'prediction': prediction.tolist()})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
