from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from pydantic import BaseModel
from typing import List
import json
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def index():
    return "Allez sur localhost:3000 pour accéder à l'application React."

@app.route("/generate-persona-image", methods=["POST"])
def generate_persona_image():
    print("Received request for image generation")
    data = request.json
    print("Received data:", data)
    persona = data.get("persona")

    if not persona:
        print("Error: Persona data is missing")
        return jsonify({"error": "Persona data is required"}), 400

    prompt = f"""
    A portrait photograph of a persona named {persona['name']}, {persona['age']} years old. A headshot for a social media profile. High-quality portrait, natural lighting, neutral background, genuine expression.
    """

    try:
        print("Sending request to OpenAI")
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        print("Received response from OpenAI")

        image_url = response.data[0].url
        print("Generated image URL:", image_url)

        return jsonify({"image_url": image_url})

    except Exception as e:
        print("Error in image generation:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
