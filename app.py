import gradio as gr
from openai import OpenAI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import requests
from PIL import Image
import tempfile
import numpy as np
from io import BytesIO  # Ajouté pour gérer BytesIO
from gradio_client import Client
from uuid import uuid4  # Pour identifier les suggestions
import pandas as pd  # Pour utiliser un DataFrame

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# Modèle pour la réponse de l'analyse des biais
class BiasAnalysisResponse(BaseModel):
    biases: list[str]
    advice: list[str]

# Fonction pour définir la clé API
def set_openai_api_key(api_key):
    if (api_key):
        os.environ["OPENAI_API_KEY"] = api_key
        global client
        client = OpenAI(api_key=api_key)
        return "Clé API définie avec succès !"
    else:
        return "La clé API est requise !"

# Fonction pour analyser les biais dans le texte de l'objectif
def analyze_biases(objective_text):
    try:
        system__prompt = f"""
        Le texte est écrit par un professionnel du marketing qui essaie de créer un persona.
        Analysez le texte suivant à la recherche de biais cognitifs potentiels et donnez des conseils sur la manière de les atténuer.
        Répondez dans le même langage de l'utilisateur.
        Liste de biais cognitifs

        Biais attentionnels
        Biais d'attention — avoir ses perceptions influencées par ses propres centres d’intérêt.

        Biais mnésique
        Biais de négativité — également connu sous le nom d'effet de négativité, est la notion que, même à intensité égale, les choses de nature plus négative ont un effet plus important sur l'état et les processus psychologiques que les choses neutres ou positives.
        Effet de récence — mieux se souvenir des dernières informations auxquelles on a été confronté.
        Effet de simple exposition — avoir préalablement été exposé à une personne ou à une situation la rend plus positive.
        Effet de primauté — mieux se souvenir des premiers éléments d'une liste mémorisée.
        Oubli de la fréquence de base — oublier de considérer la fréquence de base de l'occurrence d'un événement alors qu'on cherche à en évaluer une probabilité.
        
        Biais de jugement
        Appel à la probabilité — tendance à prendre quelque chose pour vrai parce que cela peut probablement être le cas.
        Appel à la tradition — tendance à considérer que l’ancienneté d’une théorie ou d’une assertion étaye sa véracité.
        Aversion à la dépossession — tendance à donner plus de valeur à un bien ou un service lorsque celui-ci est sa propriété.
        Biais d'ancrage — influence laissée par la première impression.
        Biais d'attribution (attribution causale) — façon d'attribuer la responsabilité d'une situation à soi ou aux autres.
        
        Biais d'attribution hostile
        Biais d'auto-complaisance — se croire à l'origine de ses réussites, mais pas de ses échecs.
        Biais d'engagement — tendance à poursuivre l'action engagée malgré la confrontation à des résultats de plus en plus négatifs.
        Biais d'équiprobabilité — tendance à penser qu'en l'absence d'information, des évènements sont équiprobables.
        Biais d'immunité à l'erreur — ne pas voir ses propres erreurs.
        Biais d'intentionnalité — consiste à percevoir l'action d'une volonté ou d'une décision derrière ce qui est fortuit ou accidentel.
        Biais de confirmation — tendance à valider ses opinions auprès des instances qui les confirment, et à rejeter d'emblée les instances qui les réfutent.
        Biais de normalité — tendance à penser que tout va se passer comme d'habitude et à ignorer les signes avant-coureurs6.
        Biais de présentéisme — privilégier les facteurs présents est plus économique cognitivement à modéliser que les facteurs absents.
        Biais de proportionnalité — favoriser l'idée potentiellement fausse que si l'on observe une augmentation des manifestations d'un phénomène, c'est que le nombre d'occurrences de ce phénomène croît en effet, sans voir que cette augmentation peut n'être que la conséquence de l'amélioration de l'outil d'observation.
        Biais de statu quo — la nouveauté est vue comme apportant plus de risques que d'avantages possibles et amène une résistance au changement.
        Biais égocentrique — se juger sous un meilleur jour qu'en réalité.
        Biais rétrospectif ou l'effet « je le savais depuis le début » — tendance à juger a posteriori qu'un événement était prévisible.
        Corrélation illusoire — perception d'une corrélation entre deux événements qui n'existe pas ou qui est bien plus faible en réalité.
        Croyance en un monde juste — tendance à considérer que la bonne action d'une personne lui sera nécessairement bénéfique tandis qu'une mauvaise action lui sera nécessairement néfaste.
        Effet d'ambiguïté — tendance à éviter les options pour lesquelles on manque d'information.
        Effet de halo — une perception sélective d'informations allant dans le sens d'une première impression que l'on cherche à confirmer.
        Effet de simple exposition — avoir préalablement été exposé à quelqu'un ou à une situation le/la rend plus positive.
        Effet Dunning-Kruger — les moins compétents dans un domaine surestiment leur compétence, alors que les plus compétents ont tendance à sous-estimer leur compétence.
        Effet Ikea — tendance pour les consommateurs à accorder une valeur supérieure aux produits qu'ils ont partiellement créés.
        Effet moins-c'est-mieux — tendance à effectuer un choix a priori moins avantageux objectivement (par exemple apprécier plus une coupe de glace de moindre quantité mais mieux remplie).
        Effet Stroop — incapacité d'ignorer une information non pertinente.
        Effet râteau — exagérer la régularité du hasard.
        Illusion de fréquence — tendance, après avoir remarqué une chose pour la première fois, à la remarquer plus souvent et à la croire plus fréquente.
        Erreur fondamentale d'attribution (ou biais d'internalité) — accorder plus d'importance aux facteurs internes à l'orateur (intentions, émotions) qu'à son discours ou à ses actes (faits tangibles). Couramment utilisé pour discréditer les éléments rationnels par des éléments émotionnels, qui sont en pratique souvent imaginés et attribués sans preuve à l'orateur puisque ses émotions internes sont difficilement discernables a priori.[réf. nécessaire]
        Illusion de savoir — dans une situation en apparence identique à une situation commune, réagir de manière habituelle, sans éprouver le besoin de rechercher les informations complémentaires qui auraient mis en évidence une différence par rapport à la situation habituelle. Il peut ainsi faire état d'une mauvaise croyance face à la réalité.
        Illusion monétaire — confusion d'un agent économique entre variation du niveau général des prix et variation des prix relatifs.
        Illusion de transparence et illusion de connaissance asymétrique.
        Loi de l'instrument (ou marteau de Maslow) — tentation qui consiste à travestir la réalité d'un problème en le transformant en fonction des réponses (les outils) dont on dispose.
        Sophisme génétique — tendance à juger le contenu en fonction du contenant, le message en fonction du messager, le fond suivant la forme.
        Supériorité illusoire — surestimation de ses propres qualités et capacités.
        Tache aveugle à l'égard des préjugés — tendance à ne pas percevoir les biais cognitifs à l'œuvre dans ses propres jugements ou décisions, et ce, aux dépens d'informations plus objectives.
        
        Biais de raisonnement
        Biais de confirmation d'hypothèse — préférer les éléments qui confirment plutôt que ceux qui infirment une hypothèse.
        Biais d'évaluation de probabilités.
        Biais de représentativité — considérer un ou certains éléments comme représentatifs d'une population.
        Biais de disponibilité — ne pas chercher d'autres informations que celles immédiatement disponibles.
        Biais d'appariement — se focaliser sur les éléments contenus dans l'énoncé d'un problème.
        Biais du survivant — se focaliser sur les éléments ayant passé avec succès un processus de sélection pour en tirer des conclusions sur la totalité des éléments.
        Réduction de la dissonance cognitive — réinterpréter une situation pour éliminer les contradictions.
        Effet rebond (assimilable à l'effet Streisand) — une pensée que l'on cherche à inhiber devient plus saillante.
        Illusion des séries — percevoir à tort des coïncidences dans des données au hasard.
        Perception sélective — interpréter de manière sélective des informations en fonction de sa propre expérience.
        Réification du savoir — considérer les connaissances comme des objets immuables et extérieurs.
        Effet de domination asymétrique ou effet leurre — choisir pour un consommateur entre deux options celle qui est la plus proche d'une troisième option malgré la forte asymétrie d'information.
        Coût irrécupérable — considérer les coûts déjà engagés dans une décision.
        Oubli de la fréquence de base — oublier la fréquence de base de l'occurrence d'un événement dont on cherche à évaluer la probabilité.
        
        Biais liés à la personnalité
        Biais d'optimisme — optimisme dispositionnel7, optimisme irréaliste8, parfois présenté comme un « non-pessimisme dispositionnel »9 et d'optimisme comparatif10,11 qui semble très ancrée chez l'être humain ; il s'agit d'une croyance individuelle qui est que le sujet se juge moins exposé à la plupart des risques qu'autrui12,13. On peut évaluer le degré d'adhésion à cette croyance en demandant au sujet d’évaluer son risque de rencontrer un événement négatif en comparaison de celui d’autrui13. Cette croyance aggrave certaines prises de risques et est souvent impliquée dans l'accidentologie routière (le conducteur s'estimant à tort plus habile que les autres pour éviter les accidents, même quand il ne respecte pas le code de la route, en raison d'une surestimation infondée et irréaliste de ses capacités)14,15,16,17.
        Effet Barnum — accepter une vague description de la personnalité comme s'appliquant spécifiquement à soi-même (ex. : horoscope).

        S'il n'y a pas de biais, respectez le format demandé et indiquez qu'aucun biais n'a été détecté.
        """

        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system__prompt},
                {"role": "user", "content": objective_text}
            ],
            temperature=0.5,
            max_tokens=800,
            response_format=BiasAnalysisResponse
        )
        
        # Obtenir la réponse structurée
        response_content = completion.choices[0].message.parsed
        return response_content.dict()

    except Exception as e:
        print("Error during bias analysis:", str(e))
        return {"error": str(e)}

# Optimiser la génération d'image pour utiliser directement l'URL
def generate_persona_image(first_name, last_name, age, gender, persona_description,
                           skin_color, eye_color, hair_style, hair_color, facial_features,
                           facial_expression, posture,
                           clothing_style, accessories,
                           background, lighting):
    if not first_name or not last_name or not age or not gender:
        return "Veuillez remplir tous les champs pour générer l'image du persona."
    
    prompt = f"{first_name} {last_name}, {gender}, {age} years old."
    
    # Ajouter les nouvelles informations au prompt
    if skin_color:
        prompt += f" Skin tone: {skin_color}."
    if eye_color:
        prompt += f" Eye color: {eye_color}."
    if hair_style:
        prompt += f" Hairstyle: {hair_style}."
    if hair_color:
        prompt += f" Hair color: {hair_color}."
    if facial_features:
        prompt += f" Facial features: {facial_features}."
    if facial_expression:
        facial_expression_eng = facial_expression_mapping.get(facial_expression, facial_expression)
        prompt += f" Facial expression: {facial_expression_eng}."
    if posture:
        posture_eng = posture_mapping.get(posture, posture)
        prompt += f" Posture: {posture_eng}."
    if clothing_style:
        prompt += f" Clothing style: {clothing_style}."
    if accessories:
        prompt += f" Accessories: {accessories}."
    if background:
        prompt += f" Background: {background}."
    if lighting:
        prompt += f" Lighting: {lighting}."
    if artistic_style:
        prompt += f" Artistic style: {artistic_style}."
    if angle:
        prompt += f" Angle and framing: {angle}."
    
    prompt += f" {persona_description}."
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        n=1,
    )
    image_url = response.data[0].url
    
    # Télécharger l'image et l'enregistrer temporairement
    response = requests.get(image_url)
    temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    with open(temp_image.name, 'wb') as f:
        f.write(response.content)

    # déclarer une variable globale pour l'image temporaire
    global temp_image_path
    temp_image_path = temp_image.name

    return temp_image.name

# Function to assist in creating the detailed profile
def assist_persona_creation(first_name, last_name, age):
    prompt = f"""
    Vous êtes un assistant IA aidant à créer des personas marketing détaillés.
    Basé sur les informations fournies, proposez des suggestions pour améliorer le profil du persona et identifiez les biais potentiels.

    Informations du persona :
    Nom : {first_name} {last_name}
    Âge : {age}

    Fournissez vos suggestions sous forme de points clairs.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500,
    )
    suggestions = response.choices[0]['message']['content'].strip()
    return suggestions

# Remplacer la fonction generate_pdf pour utiliser reportlab
def generate_pdf(first_name, last_name, age, image_url):
    try:
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        c = canvas.Canvas(temp_pdf.name, pagesize=A4)
        width, height = A4

        # Ajouter l'image du persona
        if image_url:
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
            temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            image.save(temp_image.name, format="PNG")
            c.drawImage(temp_image.name, 50, height - 200, width=150, height=150)
            temp_image.close()
            os.unlink(temp_image.name)
        else:
            c.drawString(50, height - 200, "Image non disponible")

        # Ajouter les informations du persona
        c.setFont("Helvetica-Bold", 16)
        c.drawString(220, height - 100, f'{first_name} {last_name}, Âge: {age}')

        c.setFont("Helvetica", 12)
        y = height - 130

        c.save()
        return temp_pdf.name

    except Exception as e:
        print(f"Erreur lors de la génération du PDF : {e}")
        return None

def generate_pdf_wrapper(first_name, last_name, age, image_url):
    pdf_file = generate_pdf(first_name, last_name, age, image_url)
    if pdf_file:
        return pdf_file
    else:
        return "Erreur lors de la génération du PDF."

# Function to review the persona details
def review_persona(first_name, last_name, age, image_url):
    html_content = f"""
    <h2>{first_name} {last_name}, Age: {age}</h2>
    <img src="{image_url}" alt="Persona Image" width="200">
    """
    return html_content

# Fonction pour affiner les contributions de l'utilisateur et de l'IA
def refine_persona_details(first_name, last_name, age, field_name, field_value):
    prompt = f"""
    Vous êtes un assistant IA aidant à affiner les détails d'un seul aspect persona marketing.
    Ne traitez que le champ suivant : {field_name}
    Basé sur les informations fournies, proposez des suggestions pour améliorer le profil du persona.
    S'il n'y a pas d'informations spécifiques, indiquez qu'il faudrait plus de détails.

    Informations du persona :
    Nom : {first_name} {last_name}
    Âge : {age}
    {field_name} : {field_value}
    # TODO : Inclure les biais identifiés pour affiner les suggestions
    # TODO : Inclure les objectifs marketing pour guider les suggestions
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500,
    )
    suggestions = response.choices[0].message.content.strip()
    return suggestions

# Ajouter les dictionnaires de correspondance
posture_mapping = {
    "Debout": "standing up",
    "Assis": "sitting",
    "Allongé": "lying down",
    "Accroupi": "crouching",
    "En mouvement": "moving",
    "Reposé": "resting"
}

facial_expression_mapping = {

    "Souriant": "smiling",
    "Sérieux": "serious",
    "Triste": "sad",
    "En colère": "angry",
    "Surpris": "surprised",
    "Pensif": "thoughtful"
}

skin_color_mapping = {
    "Clair": "light",
    "Moyen": "medium",
    "Foncé": "dark"
}

eye_color_mapping = {
    "Bleu": "blue",
    "Vert": "green",
    "Marron": "brown"
}

hair_style_mapping = {
    "Court": "short",
    "Long": "long",
    "Bouclé": "curly"
}

hair_color_mapping = {
    "Blond": "blonde",
    "Brun": "brown",
    "Noir": "black"
}

clothing_style_mapping = {
    "Décontracté": "casual",
    "Professionnel": "professional",
    "Sportif": "sporty"
}

accessories_mapping = {
    "Lunettes": "glasses",
    "Montre": "watch",
    "Chapeau": "hat"
}

background_mapping = {
    "Bureau": "office",
    "Extérieur": "outdoor",
    "Maison": "home"
}

lighting_mapping = {
    "Naturel": "natural",
    "Artificiel": "artificial",
    "Faible": "dim"
}

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
        objective_input = gr.Textbox(label="Quel est votre objectif pour la création de ce persona ?", lines=3)
        analyze_button = gr.Button("Analyser les biais")
        bias_analysis_output = gr.Markdown()
        word_count_state = gr.State(0)  # Ajout d'un état pour le nombre de mots
        realtime_analysis = gr.Radio(label="Analyse en temps réel", choices=["Activée", "Désactivée"], value="Désactivée")
        word_count_display = gr.Markdown()  # Ajout d'un affichage pour le compteur de mots

        # Définir les scénarios de suggestion
        suggestion1 = "Je souhaite créer un persona pour promouvoir un nouveau service de livraison écologique destiné aux jeunes professionnels urbains soucieux de l'environnement. Nous avons réalisé une étude de marché et identifié un besoin pour des solutions de livraison plus durables et rapides. Pour cela, nous voulons créer un persona qui incarne ces valeurs et besoins. Plus spécifiquement, nous ciblons les personnes âgées de 25 à 35 ans, vivant dans des zones urbaines, travaillant à temps plein et ayant un intérêt pour les questions environnementales."
        suggestion2 = "J'envisage de développer une application mobile de fitness personnalisée pour les seniors actifs qui cherchent à maintenir une vie saine et sociale. L'application proposera des programmes d'entraînement adaptés aux besoins et aux capacités des seniors, ainsi que des fonctionnalités pour suivre les progrès et rester motivé. Le persona devrait refléter les besoins et les préférences des seniors actifs, en mettant l'accent sur la facilité d'utilisation, la convivialité et la personnalisation. Nous visons à créer une expérience positive et engageante pour les utilisateurs."

        # Ajouter les boutons de suggestion
        with gr.Row():
            suggestion_button1 = gr.Button("Suggestion 1")
            suggestion_button2 = gr.Button("Suggestion 2")

        # Définir les actions des boutons pour remplir le champ objective_input
        suggestion_button1.click(fn=lambda: suggestion1, inputs=[], outputs=objective_input)
        suggestion_button2.click(fn=lambda: suggestion2, inputs=[], outputs=objective_input)

        # Fonction pour afficher dynamiquement les biais et les conseils
        def display_biases_and_advice(objective_text, previous_count, realtime):
            current_count = len(objective_text.split())
            if realtime == "Activée" and current_count - previous_count >= 10:
                analysis_result = analyze_biases(objective_text)
                if "error" in analysis_result:
                    return f"Erreur: {analysis_result['error']}", current_count, f"Nombre de mots : {current_count}"
                
                biases = analysis_result.get("biases", [])
                advice = analysis_result.get("advice", [])
                
                if not biases and not advice:
                    return "Aucun biais détecté ou conseils disponibles.", current_count, f"Nombre de mots : {current_count}"
                
                content = "<div style='display: flex; flex-wrap: wrap;'>"
                for bias, adv in zip(biases, advice):
                    content += f"""
                    <div style='flex: 1; min-width: 300px; padding: 10px; text-align: center; border: 1px solid lightgray; border-radius: 20px; margin: 5px;'>
                        <strong>{bias.upper()}</strong><br><br>{adv}
                    </div>
                    """
                content += "</div>"
                return content, current_count, f"Nombre de mots : {current_count}"
            return gr.update(), previous_count, f"Nombre de mots : {current_count}"  # Conserver l'état précédent sans changement

        # Utilisation du bouton pour déclencher l'analyse des biais
        def analyze_button_click(objective_text, previous_count, realtime):
            current_count = len(objective_text.split())
            analysis_result = analyze_biases(objective_text)
            if "error" in analysis_result:
                return f"Erreur: {analysis_result['error']}", current_count, f"Nombre de mots : {current_count}"
            
            biases = analysis_result.get("biases", [])
            advice = analysis_result.get("advice", [])
            
            if not biases and not advice:
                return "Aucun biais détecté ou conseils disponibles.", current_count, f"Nombre de mots : {current_count}"
            
            content = "<div style='display: flex; flex-wrap: wrap;'>"
            for bias, adv in zip(biases, advice):
                content += f"""
                <div style='flex: 1; min-width: 300px; padding: 10px; text-align: center; border: 1px solid lightgray; border-radius: 20px; margin: 5px;'>
                    <strong>{bias.upper()}</strong><br><br>{adv}
                </div>
                """
            content += "</div>"
            return content, current_count, f"Nombre de mots : {current_count}"

        # Utilisation du bouton pour déclencher l'analyse des biais
        analyze_button.click(
            fn=analyze_button_click,
            inputs=[objective_input, word_count_state, realtime_analysis],
            outputs=[bias_analysis_output, word_count_state, word_count_display]
        )

        # Utilisation de l'analyse en temps réel
        objective_input.change(
            fn=display_biases_and_advice,
            inputs=[objective_input, word_count_state, realtime_analysis],
            outputs=[bias_analysis_output, word_count_state, word_count_display]
        )

        # Afficher le compteur de mots
        objective_input.change(
            fn=lambda text: f"Nombre de mots : {len(text.split())}",
            inputs=objective_input,
            outputs=word_count_display
        )

    # Autres étapes comme avant (image, révision et PDF)

    with gr.Tab("Étape 2: Image du persona et informations de base"):
        with gr.Row():
            with gr.Column(scale=1):
                first_name_input = gr.Textbox(label="Prénom")
                last_name_input = gr.Textbox(label="Nom de famille")
                age_input = gr.Slider(label="Âge", minimum=18, maximum=100, step=1)
                gender_input = gr.Radio(label="Genre", choices=["homme", "femme"], value="homme")
                persona_description_input = gr.Textbox(label="Description du persona (en anglais)", lines=1)
                generate_image_button = gr.Button("Générer l'image du persona")
            with gr.Column(scale=1):
                persona_image_output = gr.Image(label="Image du persona")
        
        # Ajouter une liste accordéon pour les détails du prompt DALL-E 3
        with gr.Accordion("Détails du prompt DALL-E 3"):
            # Section 1: Caractéristiques physiques
            with gr.Accordion("1. Caractéristiques physiques", open=False):
                skin_color_input = gr.Dropdown(label="Teint de la peau", choices=list(skin_color_mapping.keys()), value="")
                eye_color_input = gr.Dropdown(label="Couleur des yeux", choices=list(eye_color_mapping.keys()), value="")
                hair_style_input = gr.Dropdown(label="Coiffure", choices=list(hair_style_mapping.keys()), value="")
                hair_color_input = gr.Dropdown(label="Couleur des cheveux", choices=list(hair_color_mapping.keys()), value="")
                facial_features_input = gr.Textbox(label="Traits du visage", value="")
            
            # Section 2: Expressions faciales et posture
            with gr.Accordion("2. Expressions faciales et posture", open=False):
                facial_expression_input = gr.Dropdown(label="Expression faciale", choices=list(facial_expression_mapping.keys()), value="")
                posture_input = gr.Dropdown(label="Posture", choices=list(posture_mapping.keys()), value="")
            
            # Section 3: Style vestimentaire
            with gr.Accordion("3. Style vestimentaire", open=False):
                clothing_style_input = gr.Dropdown(label="Style de vêtements", choices=list(clothing_style_mapping.keys()), value="")
                accessories_input = gr.Dropdown(label="Accessoires", choices=list(accessories_mapping.keys()), value="")
            
            # Section 4: Contexte et éclairage
            with gr.Accordion("4. Contexte et éclairage", open=False):
                background_input = gr.Dropdown(label="Arrière-plan", choices=list(background_mapping.keys()), value="")
                lighting_input = gr.Dropdown(label="Éclairage", choices=list(lighting_mapping.keys()), value="")
        
        generate_image_button.click(
            fn=generate_persona_image,
            inputs=[
                first_name_input, last_name_input, age_input, gender_input, persona_description_input,
                skin_color_input, eye_color_input, hair_style_input, hair_color_input, facial_features_input,
                facial_expression_input, posture_input,
                clothing_style_input, accessories_input,
                background_input, lighting_input
            ],
            outputs=persona_image_output
        )

    with gr.Tab("Étape 3: Profil détaillé du persona"):
        gr.Markdown("### Étape 3: Profil détaillé du persona")

        # Section 1: Informations de base
        with gr.Accordion("1. Informations de base", open=True):
            with gr.Row():
                marital_status_input = gr.Dropdown(label="État civil", choices=["Célibataire", "En couple", "Marié(e)", "Divorcé(e)", "Veuf(ve)"])
                refine_marital_status_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                education_level_input = gr.Dropdown(label="Niveau d'éducation", choices=["Études secondaires", "Bachelier", "Master", "Doctorat", "Autre"])
                refine_education_level_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                profession_input = gr.Textbox(label="Profession")
                refine_profession_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                income_input = gr.Number(label="Revenus annuels (€)")
                refine_income_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                personality_traits_input = gr.Textbox(
                    label="Traits de personnalité (introverti/extraverti, etc.)",
                    lines=2,
                    info="Ensemble des caractéristiques qui définissent l'individualité d'une personne, incluant ses comportements stables et uniques."
                )
                refine_personality_traits_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                values_beliefs_input = gr.Textbox(label="Valeurs et croyances", lines=2)
                refine_values_beliefs_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                motivations_input = gr.Textbox(
                    label="Motivations intrinsèques",
                    lines=2,
                    info="[Motivations internes qui poussent une personne à agir par plaisir ou satisfaction personnelle](https://fr.wikipedia.org/wiki/Motivation), sans attendre de récompenses externes."
                )
                refine_motivations_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                hobbies_interests_input = gr.Textbox(label="Hobbies et intérêts", lines=2)
                refine_hobbies_interests_button = gr.Button("Affiner", scale=0.2)

        # Section 2: Informations liées au design
        with gr.Accordion("2. Informations liées au design", open=False):
            with gr.Row():
                main_responsibilities_input = gr.Textbox(label="Responsabilités principales", lines=2)
                refine_main_responsibilities_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                daily_activities_input = gr.Textbox(label="Activités journalières", lines=2)
                refine_daily_activities_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                technology_relationship_input = gr.Textbox(label="Relation avec la technologie", lines=2)
                refine_technology_relationship_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                product_related_activities_input = gr.Textbox(label="Tâches liées au produit", lines=2)
                refine_product_related_activities_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                pain_points_input = gr.Textbox(
                    label="Points de douleur (pain points)",
                    lines=2,
                    info="Problèmes ou frustrations auxquels un client peut être confronté lors de son parcours d'achat, tels qu'un mauvais service ou des délais d'attente excessifs."
                )
                refine_pain_points_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                product_goals_input = gr.Textbox(label="Objectifs d’utilisation du produit", lines=2)
                refine_product_goals_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                usage_scenarios_input = gr.Textbox(label="Scénarios d’utilisation", lines=2)
                refine_usage_scenarios_button = gr.Button("Affiner", scale=0.2)

        # Section 3: Informations marketing et commerciales
        with gr.Accordion("3. Informations marketing et commerciales", open=False):
            with gr.Row():
                brand_relationship_input = gr.Textbox(label="Relation avec la marque", lines=2)
                refine_brand_relationship_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                market_segment_input = gr.Textbox(label="Segment de marché", lines=2)
                refine_market_segment_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                commercial_objectives_input = gr.Textbox(
                    label="Objectifs commerciaux",
                    lines=2,
                    info="Objectifs clairs et mesurables que l'on souhaite atteindre, souvent décrits selon la méthode [SMART](https://fr.wikipedia.org/wiki/Objectifs_et_indicateurs_SMART) pour assurer leur réalisabilité."
                )
                refine_commercial_objectives_button = gr.Button("Affiner", scale=0.2)

        # Section 4: Graphismes et accessibilité
        with gr.Accordion("4. Graphismes et accessibilité", open=False):
            with gr.Row():
                visual_codes_input = gr.Textbox(label="Graphiques et codes visuels", lines=2)
                refine_visual_codes_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                special_considerations_input = gr.Textbox(label="Considérations spéciales (accessibilité)", lines=2)
                refine_special_considerations_button = gr.Button("Affiner", scale=0.2)

        # Section 5: Dimensions supplémentaires
        with gr.Accordion("5. Dimensions supplémentaires", open=False):
            with gr.Row():
                daily_life_input = gr.Textbox(label="Une journée dans la vie", lines=3)
                refine_daily_life_button = gr.Button("Affiner", scale=0.2)
            with gr.Row():
                references_input = gr.Textbox(label="Références (sources de données)", lines=2)
                refine_references_button = gr.Button("Affiner", scale=0.2)

        # Zone de sortie pour les suggestions affinées
        refined_suggestions_output = gr.Markdown(label="Suggestions affinées")

        # Associer les boutons à la fonction de traitement
        refine_marital_status_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "État civil", value),
            inputs=[first_name_input, last_name_input, age_input, marital_status_input],
            outputs=refined_suggestions_output
        )
        refine_education_level_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Niveau d'éducation", value),
            inputs=[first_name_input, last_name_input, age_input, education_level_input],
            outputs=refined_suggestions_output
        )
        refine_profession_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Profession", value),
            inputs=[first_name_input, last_name_input, age_input, profession_input],
            outputs=refined_suggestions_output
        )
        refine_income_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Revenus annuels", value),
            inputs=[first_name_input, last_name_input, age_input, income_input],
            outputs=refined_suggestions_output
        )
        refine_personality_traits_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Traits de personnalité", value),
            inputs=[first_name_input, last_name_input, age_input, personality_traits_input],
            outputs=refined_suggestions_output
        )
        refine_values_beliefs_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Valeurs et croyances", value),
            inputs=[first_name_input, last_name_input, age_input, values_beliefs_input],
            outputs=refined_suggestions_output
        )
        refine_motivations_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Motivations intrinsèques", value),
            inputs=[first_name_input, last_name_input, age_input, motivations_input],
            outputs=refined_suggestions_output
        )
        refine_hobbies_interests_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Hobbies et intérêts", value),
            inputs=[first_name_input, last_name_input, age_input, hobbies_interests_input],
            outputs=refined_suggestions_output
        )
        refine_main_responsibilities_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Responsabilités principales", value),
            inputs=[first_name_input, last_name_input, age_input, main_responsibilities_input],
            outputs=refined_suggestions_output
        )
        refine_daily_activities_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Activités journalières", value),
            inputs=[first_name_input, last_name_input, age_input, daily_activities_input],
            outputs=refined_suggestions_output
        )
        refine_technology_relationship_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Relation avec la technologie", value),
            inputs=[first_name_input, last_name_input, age_input, technology_relationship_input],
            outputs=refined_suggestions_output
        )
        refine_product_related_activities_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Tâches liées au produit", value),
            inputs=[first_name_input, last_name_input, age_input, product_related_activities_input],
            outputs=refined_suggestions_output
        )
        refine_pain_points_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Points de douleur", value),
            inputs=[first_name_input, last_name_input, age_input, pain_points_input],
            outputs=refined_suggestions_output
        )
        refine_product_goals_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Objectifs d’utilisation du produit", value),
            inputs=[first_name_input, last_name_input, age_input, product_goals_input],
            outputs=refined_suggestions_output
        )
        refine_usage_scenarios_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Scénarios d’utilisation", value),
            inputs=[first_name_input, last_name_input, age_input, usage_scenarios_input],
            outputs=refined_suggestions_output
        )
        refine_brand_relationship_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Relation avec la marque", value),
            inputs=[first_name_input, last_name_input, age_input, brand_relationship_input],
            outputs=refined_suggestions_output
        )
        refine_market_segment_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Segment de marché", value),
            inputs=[first_name_input, last_name_input, age_input, market_segment_input],
            outputs=refined_suggestions_output
        )
        refine_commercial_objectives_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Objectifs commerciaux", value),
            inputs=[first_name_input, last_name_input, age_input, commercial_objectives_input],
            outputs=refined_suggestions_output
        )
        refine_visual_codes_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Graphiques et codes visuels", value),
            inputs=[first_name_input, last_name_input, age_input, visual_codes_input],
            outputs=refined_suggestions_output
        )
        refine_special_considerations_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Considérations spéciales", value),
            inputs=[first_name_input, last_name_input, age_input, special_considerations_input],
            outputs=refined_suggestions_output
        )
        refine_daily_life_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Une journée dans la vie", value),
            inputs=[first_name_input, last_name_input, age_input, daily_life_input],
            outputs=refined_suggestions_output
        )
        refine_references_button.click(
            fn=lambda first_name, last_name, age, value: refine_persona_details(first_name, last_name, age, "Références", value),
            inputs=[first_name_input, last_name_input, age_input, references_input],
            outputs=refined_suggestions_output
        )

    # Ajout du nouvel onglet "Résumé et export du persona"
    with gr.Tab("Résumé et export du persona"):
        gr.Markdown("### Résumé et export du persona")
        
        # Bouton pour afficher le résumé du persona
        generate_summary_button = gr.Button("Afficher le résumé du persona")
        
        # Zone de sortie pour l'aperçu du persona
        persona_output = gr.HTML(label="Aperçu du persona")
        
        # Fonction pour traiter et afficher le profil du persona
        def process_persona_wrapper(
            persona_image_output, first_name_input, last_name_input, age_input, gender_input, marital_status_input,
            education_level_input, profession_input, income_input, personality_traits_input, values_beliefs_input,
            motivations_input, hobbies_interests_input, main_responsibilities_input, daily_activities_input,
            technology_relationship_input, product_related_activities_input, pain_points_input, product_goals_input,
            usage_scenarios_input, brand_relationship_input, market_segment_input, commercial_objectives_input,
            visual_codes_input, special_considerations_input, daily_life_input, references_input
        ):
            persona_profile = process_persona(
                persona_image_output, first_name_input, last_name_input, age_input, gender_input, marital_status_input,
                education_level_input, profession_input, income_input, personality_traits_input, values_beliefs_input,
                motivations_input, hobbies_interests_input, main_responsibilities_input, daily_activities_input,
                technology_relationship_input, product_related_activities_input, pain_points_input, product_goals_input,
                usage_scenarios_input, brand_relationship_input, market_segment_input, commercial_objectives_input,
                visual_codes_input, special_considerations_input, daily_life_input, references_input
            )
            return persona_profile
        
        generate_summary_button.click(
            fn=process_persona_wrapper,
            inputs=[
                persona_image_output, first_name_input, last_name_input, age_input, gender_input, marital_status_input,
                education_level_input, profession_input, income_input, personality_traits_input, values_beliefs_input,
                motivations_input, hobbies_interests_input, main_responsibilities_input, daily_activities_input,
                technology_relationship_input, product_related_activities_input, pain_points_input, product_goals_input,
                usage_scenarios_input, brand_relationship_input, market_segment_input, commercial_objectives_input,
                visual_codes_input, special_considerations_input, daily_life_input, references_input
            ],
            outputs=persona_output
        )
        
        # Bouton pour exporter le persona en PDF
        export_pdf_button = gr.Button("Exporter en PDF")
        
        # Fonction pour exporter le persona en PDF
        def export_pdf_button_click(
            first_name_input, last_name_input, age_input, persona_image_output
        ):
            pdf_file = generate_pdf_wrapper(
                first_name_input, last_name_input, age_input, persona_image_output
            )
            return pdf_file
        
        export_pdf_button.click(
            fn=export_pdf_button_click,
            inputs=[first_name_input, last_name_input, age_input, persona_image_output],
            outputs=gr.File(label="Télécharger le PDF")
        )
        
        # Affichage du résumé du persona
        persona_output

# Fonction pour traiter et afficher le profil du persona
def process_persona(
    persona_image_output, first_name_input, last_name_input, age_input, gender_input, marital_status_input,
    education_level_input, profession_input, income_input, personality_traits_input, values_beliefs_input,
    motivations_input, hobbies_interests_input, main_responsibilities_input, daily_activities_input,
    technology_relationship_input, product_related_activities_input, pain_points_input, product_goals_input,
    usage_scenarios_input, brand_relationship_input, market_segment_input, commercial_objectives_input,
    visual_codes_input, special_considerations_input, daily_life_input, references_input
):
    # Construire le profil du persona à partir des champs saisis
    persona_profile = f"""
    <h2>Profil du Persona</h2>
    <h3>1. Informations de base</h3>
    <ul>
    <img src="{persona_image_output}" alt="Persona Image" width="200">
        <li><strong>Prénom:</strong> {first_name_input}</li>
        <li><strong>Nom de famille:</strong> {last_name_input}</li>
        <li><strong>Âge:</strong> {age_input}</li>
        <li><strong>Genre:</strong> {gender_input}</li>
        <li><strong>État civil:</strong> {marital_status_input}</li>
        <li><strong>Niveau d'éducation:</strong> {education_level_input}</li>
        <li><strong>Profession:</strong> {profession_input}</li>
        <li><strong>Revenus annuels:</strong> {income_input} €</li>
        <li><strong>Traits de personnalité:</strong> {personality_traits_input}</li>
        <li><strong>Valeurs et croyances:</strong> {values_beliefs_input}</li>
        <li><strong>Motivations intrinsèques:</strong> {motivations_input}</li>
        <li><strong>Hobbies et intérêts:</strong> {hobbies_interests_input}</li>
    </ul>
    <h3>2. Informations liées au design</h3>
    <ul>
        <li><strong>Responsabilités principales:</strong> {main_responsibilities_input}</li>
        <li><strong>Activités journalières:</strong> {daily_activities_input}</li>
        <li><strong>Relation avec la technologie:</strong> {technology_relationship_input}</li>
        <li><strong>Tâches liées au produit:</strong> {product_related_activities_input}</li>
        <li><strong>Points de douleur:</strong> {pain_points_input}</li>
        <li><strong>Objectifs d’utilisation du produit:</strong> {product_goals_input}</li>
        <li><strong>Scénarios d’utilisation:</strong> {usage_scenarios_input}</li>
    </ul>
    <h3>3. Informations marketing et commerciales</h3>
    <ul>
        <li><strong>Relation avec la marque:</strong> {brand_relationship_input}</li>
        <li><strong>Segment de marché:</strong> {market_segment_input}</li>
        <li><strong>Objectifs commerciaux:</strong> {commercial_objectives_input}</li>
    </ul>
    <h3>4. Graphismes et accessibilité</h3>
    <ul>
        <li><strong>Graphiques et codes visuels:</strong> {visual_codes_input}</li>
        <li><strong>Considérations spéciales:</strong> {special_considerations_input}</li>
    </ul>
    <h3>5. Dimensions supplémentaires</h3>
    <ul>
        <li><strong>Une journée dans la vie:</strong> {daily_life_input}</li>
        <li><strong>Références:</strong> {references_input}</li>
    </ul>
    """
    return persona_profile

demo.launch(debug=True)