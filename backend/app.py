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

# Charger les variables d'environnement depuis le fichier .env
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

@app.route("/generate-persona-image2", methods=["POST"])
def generate_persona_image2():
    print("Received request for image generation")
    data = request.json
    print("Received data:", data)
    persona = data.get("persona")

    if not persona:
        print("Error: Persona data is missing")
        return jsonify({"error": "Persona data is required"}), 400

    prompt = f"""
    An original portrait photograph of a persona named {persona['name']}, {persona['age']} years old. Asiatic. High-quality portrait, natural lighting, neutral background, genuine expression.
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

class Keyword(BaseModel):
    word: str
    explanation: str


class KeywordResponse(BaseModel):
    keywords: List[Keyword]
    explanation: str


@app.route("/generate-keywords", methods=["POST"])
def generate_keywords():
    try:
        data = request.json
        persona = data.get("persona")

        if not persona:
            return jsonify({"error": "Persona data is required"}), 400

        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Vous êtes un système d'IA qui génère cinq mots-clés en français pertinents basés sur un persona donné en format JSON. Générez une liste de mots-clés avec leur explication.",
                },
                {
                    "role": "user",
                    "content": f"""
                    Générez 5 mots-clés originaux avec une explication pour ce persona : {json.dumps(persona)}
                    """,
                },
            ],
            temperature=1,
            response_format=KeywordResponse,
        )

        response_content = completion.choices[0].message.parsed

        return jsonify(response_content.dict())

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/generate-keywords2", methods=["POST"])
def generate_keywords2():
    try:
        data = request.json
        persona = data.get("persona")

        if not persona:
            return jsonify({"error": "Persona data is required"}), 400

        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Vous êtes un système d'IA qui génère cinq mots-clés en français pertinents basés sur un persona donné en format JSON. Générez une liste de mots-clés avec leur explication.",
                },
                {
                    "role": "user",
                    "content": f"""
                    Générez 5 mots-clés originaux avec une explication pour ce persona : {json.dumps(persona)}
                    Détachez-vous des clichés habituels et proposez 5 mots-clés très originaux qui pourraient être moins évidents, mais qui sont pertinents pour décrire ce persona.
                    """,
                },
            ],
            temperature=1,
            response_format=KeywordResponse,
        )

        response_content = completion.choices[0].message.parsed

        return jsonify(response_content.dict())

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/generate-brand", methods=["POST"])
def generate_brand():
    try:
        data = request.json
        keywords = data.get("keywords")
        entity_type = data.get("entityType")

        print("Received keywords:", keywords)
        print("Received entity type:", entity_type)

        if not keywords:
            return jsonify({"error": "Keywords data is required"}), 400

        entity_message = "une entreprise technologique." if entity_type == "entreprise" else "une association à but non lucratif axée sur le développement durable."

        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"Vous êtes un expert en création de marque. Générez un nom de marque et un slogan basés sur les mots-clés fournis pour {entity_message}. Vous pouvez également utiliser des mots-clés supplémentaires si nécessaire.",
                },
                {
                    "role": "user",
                    "content": f"Générez un nom de marque et un slogan basés sur ces mots-clés : {json.dumps(keywords)}",
                },
            ],
            response_format=BrandResponse,
        )

        response_content = json.loads(completion.choices[0].message.content)
        return jsonify(response_content)

    except Exception as e:
        print("Error in generate_brand:", str(e))
        return jsonify({"error": str(e)}), 500

class BrandResponse(BaseModel):
    name: str
    slogan: str

class AdResponse(BaseModel):
    title: str
    description: str


@app.route("/generate-ad", methods=["POST"])
def generate_ad():
    try:
        data = request.json
        keywords = data.get("keywords")
        brand = data.get("brand")
        entityType = data.get("entityType")

        if not keywords or not brand:
            return jsonify({"error": "Keywords and brand data are required"}), 400

        print("Received keywords:", keywords)
        print("Received brand:", brand)
        print("Received entityType:", entityType)

        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Vous êtes un expert en publicité. Générez un titre et une description de publicité basés sur les mots-clés et la marque fournis.",
                },
                {
                    "role": "user",
                    "content": f"""Générez un titre et une description de publicité pour la marque {brand['name']} avec le slogan '{brand['slogan']}',
                    basés sur ces mots-clés : {json.dumps(keywords)}. Cette publicité est destinée à promouvoir une {entityType}.
                    Choisissez un seul aspect des mots-clés pour mettre en avant la marque. Si vous ne choisissez pas un aspect spécifique, l'utilisateur est perdu.
                    Par exemple, si les mots-clés mentionnent le cheval et le réseautage : choisissez un seul aspect pour mettre en avant la marque.
                    Si celle-ci est une association, elle est axée sur le développement durable. Si c'est une entreprise, elle est axée sur la technologie.""",
                },
            ],
            response_format=AdResponse,
        )

        response_content = json.loads(completion.choices[0].message.content)
        print("Generated ad:", response_content)
        return jsonify(response_content)

    except Exception as e:
        print("Error in generate_ad:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/generate-logo", methods=["POST"])
def generate_logo():
    try:
        data = request.json
        brand = data.get("brand")

        if not brand:
            return jsonify({"error": "Brand data is required"}), 400

        prompt = f"""
        Vector logo design for '{brand['name']}'.  Minimalistic, professional, with a clean, white background with sharp lines and distinct shapes."""

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        logo_url = response.data[0].url
        return jsonify({"logo_url": logo_url})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
