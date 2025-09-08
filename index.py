from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()  
app = Flask(__name__)

# Baad mei yh api key ko .env mei daal dena
genai.configure(api_key= os.getenv("API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

@app.route('/ask', methods=["GET", "POST"])
def home():
    data = request.json
    user_input = data.get("query", "")          # If "query" does not exist, it will return the default value "" (an empty string).

    if not user_input:
        return jsonify({"error": "Query is not present"}), 400

    response = model.generate_content(user_input)

    return jsonify({"response": response.text})             # if status code is not mentioned here, Flask defaults it to 200 

if __name__ == '__main__':
    app.run(port= 5000, debug=True)