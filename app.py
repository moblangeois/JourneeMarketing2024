import gradio as gr
from openai import OpenAI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from fpdf import FPDF
import requests
from PIL import Image
import tempfile
import numpy as np

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Modèle pour la réponse de l'analyse des biais
class BiasAnalysisResponse(BaseModel):
    biases: list[str]
    advice: list[str]

# Fonction pour définir la clé API
def set_openai_api_key(api_key):
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        return "Clé API définie avec succès !"
    else:
        return "La clé API est requise !"

# Fonction pour analyser les biais dans le texte de l'objectif
def analyze_biases(objective_text):
    try:
        prompt = f"""
        Vous êtes un assistant IA formé à l'analyse de textes pour y déceler des biais cognitifs.
        Analysez le texte suivant à la recherche de biais cognitifs potentiels et donnez des conseils sur la manière de les atténuer.

        Texte :
        {objective_text}

        Fournissez votre analyse dans un langage clair et concis, en deux parties : 
        1. Analyse des biais cognitifs.
        2. Conseils pour atténuer ces biais.
        """
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Vous êtes un système d'IA qui analyse des textes pour y déceler des biais cognitifs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=800,
            response_format=BiasAnalysisResponse
        )
        
        # Obtenir la réponse structurée
        response_content = completion.choices[0].message.parsed
        return response_content.dict()

    except Exception as e:
        return {"error": str(e)}

def generate_persona_image(first_name, last_name, age, persona_description):
    if not first_name or not last_name or not age:
        return "Veuillez remplir tous les champs pour générer l'image du persona."

    prompt = f"""
    A portrait photograph of a persona named {first_name} {last_name}, a {age}-year-old individual.  A headshot for a social media profile. High-quality portrait, natural lighting, neutral background, genuine expression.
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

        return image_url

    except Exception as e:
        return {"error": str(e)}

# Function to assist in creating the detailed profile
def assist_persona_creation(first_name, last_name, age, personal_history, consumption_preferences, behaviors_habits):
    prompt = f"""
You are an AI assistant that helps in creating detailed marketing personas.
Based on the following information, provide suggestions to enhance the persona's profile and identify any potential cognitive or algorithmic biases.

Persona Information:
Name: {first_name} {last_name}
Age: {age}
Personal History: {personal_history}
Consumption Preferences: {consumption_preferences}
Behaviors and Habits: {behaviors_habits}

Provide your suggestions and bias analysis.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500,
    )
    suggestions = response.choices[0].message.content.strip()
    return suggestions

# Function to generate the PDF of the persona
def generate_pdf(first_name, last_name, age, personal_history, consumption_preferences, behaviors_habits, image_array):
    pdf = FPDF()
    pdf.add_page()

    # Vérification que image_array est bien une matrice numpy
    if not isinstance(image_array, np.ndarray):
        return "L'image fournie n'est pas une matrice valide."

    try:
        # Convertir la matrice d'octets en image avec Pillow
        image = Image.fromarray(image_array)

        # Sauvegarder l'image dans un fichier temporaire
        temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        image.save(temp_image.name, format="PNG")

        # Ajouter l'image au PDF
        pdf.image(temp_image.name, x=10, y=8, w=50)

    except Exception as e:
        return f"Erreur lors de la conversion de la matrice en image : {e}"

    finally:
        # Supprimer le fichier temporaire après usage
        if temp_image:
            temp_image.close()
        if os.path.exists(temp_image.name):
            os.unlink(temp_image.name)

    # Ajouter les informations de la persona
    pdf.set_xy(70, 10)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'{first_name} {last_name}, Age: {age}', ln=True)

    pdf.set_font('Arial', '', 12)
    pdf.ln(20)
    pdf.multi_cell(0, 10, f'**Histoire personnelle:**\n{personal_history}')
    pdf.ln(5)
    pdf.multi_cell(0, 10, f'**Préférences de consommation:**\n{consumption_preferences}')
    pdf.ln(5)
    pdf.multi_cell(0, 10, f'**Comportements et habitudes:**\n{behaviors_habits}')

    # Sauvegarder le PDF dans un fichier temporaire
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    try:
        pdf.output(temp_pdf.name)
    except IOError as e:
        return f"Erreur lors de la sauvegarde du PDF : {e}"

    return temp_pdf.name

def generate_pdf_wrapper(first_name, last_name, age, personal_history, consumption_preferences, behaviors_habits, image_url):
    pdf_file = generate_pdf(first_name, last_name, age, personal_history, consumption_preferences, behaviors_habits, image_url)
    return pdf_file

# Function to review the persona details
def review_persona(first_name, last_name, age, personal_history, consumption_preferences, behaviors_habits, image_url):
    html_content = f"""
    <h2>{first_name} {last_name}, Age: {age}</h2>
    <img src="{image_url}" alt="Persona Image" width="200">
    <h3>Hisoire personnelle</h3>
    <p>{personal_history}</p>
    <h3>Préférences de consommation</h3>
    <p>{consumption_preferences}</p>
    <h3>Comportements et habitudes</h3>
    <p>{behaviors_habits}</p>
    """
    return html_content

# Interface utilisateur Gradio avec des blocs dynamiques pour les biais
with gr.Blocks(theme=gr.themes.Citrus()) as demo:
    gr.Markdown("# Assistant de création de persona")

    with gr.Tab("Informations sur l'API OpenAI"):
        gr.Markdown("### Informations sur l'API OpenAI")
        gr.Markdown("Veuillez entrer votre clé API OpenAI pour commencer.")

        # Section de connexion API
        api_key_input = gr.Textbox(label="Entrez votre clé API OpenAI", type="password")
        api_key_button = gr.Button("Définir la clé API")
        api_key_status = gr.Textbox(label="Statut de la clé API", interactive=False)
        api_key_button.click(fn=set_openai_api_key, inputs=api_key_input, outputs=api_key_status)

    with gr.Tab("Étape 1: Objectif et analyse des biais"):
        objective_input = gr.Textbox(label="Objectif du persona", lines=3)

        # Utilisation du décorateur @gr.render pour générer dynamiquement les biais
        @gr.render(inputs=objective_input)
        def analyze_biases(text):
            # Compter les mots dans le texte
            word_count = len(text.split())
            if word_count < 30:
                return "Veuillez entrer un texte plus long pour analyser les biais."
            else:
                response = "Placeholder for bias analysis"
                if "error" in response:
                    return f"Erreur: {response['error']}"
                else:
                    gr.Markdown(f"{response}")

    # Autres étapes comme avant (image, révision et PDF)

    with gr.Tab("Étape 2: Image du persona et informations de base"):
        first_name_input = gr.Textbox(label="Prénom")
        last_name_input = gr.Textbox(label="Nom de famille")
        age_input = gr.Slider(label="Âge", minimum=18, maximum=100, step=1)
        persona_description_input = gr.Textbox(label="Description du persona", lines=3)
        generate_image_button = gr.Button("Générer l'image du persona")
        persona_image_output = gr.Image(label="Image du persona")
        generate_image_button.click(
            fn=generate_persona_image,
            inputs=[first_name_input, last_name_input, age_input, persona_description_input],
            outputs=persona_image_output
        )

    with gr.Tab("Étape 3: Révision du persona"):
        personal_history_input = gr.Textbox(label="Histoire personnelle", lines=3)
        consumption_preferences_input = gr.CheckboxGroup(
            label="Préférences de consommation", choices=["Technologie", "Mode", "Alimentation", "Voyages"]
        )
        behaviors_habits_input = gr.CheckboxGroup(
            label="Comportements et habitudes", choices=["Acheteur compulsif", "Consommateur réfléchi", "Socialement influencé"]
        )
        review_button = gr.Button("Réviser le persona")
        review_output = gr.HTML()
        review_button.click(
            fn=review_persona,
            inputs=[first_name_input, last_name_input, age_input, personal_history_input, consumption_preferences_input, behaviors_habits_input, persona_image_output],
            outputs=review_output
        )

    with gr.Tab("Étape 4: Génération du PDF"):
        gr.Markdown("### Génération du PDF du persona")
        generate_pdf_button = gr.Button("Générer le PDF")
        pdf_output = gr.File(label="Télécharger le PDF")
        generate_pdf_button.click(
            fn=generate_pdf,
            inputs=[first_name_input, last_name_input, age_input, personal_history_input, consumption_preferences_input, behaviors_habits_input, persona_image_output],
            outputs=pdf_output
        )

demo.launch(debug=True)
