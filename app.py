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
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        global client
        client = OpenAI(api_key=api_key)
        return "Clé API définie avec succès !"
    else:
        return "La clé API est requise !"

# Fonction pour analyser les biais dans le texte de l'objectif
def analyze_biases(objective_text):
    try:
        prompt = f"""
        Le texte est écrit par un professionnel du marketing qui essaie de créer un persona.
        Analysez le texte suivant à la recherche de biais cognitifs potentiels et donnez des conseils sur la manière de les atténuer.
        Répondez dans le même langage de l'utilisateur.
        Texte :
        {objective_text}

        Fournissez votre analyse dans un langage clair et très concis, en deux parties : 
        1. Analyse des biais cognitifs.
        2. Conseils pour atténuer ces biais.
        """
        system__prompt = f"""
        Vous êtes un assistant d'analyse de biais cognitifs qui aide les professionnels du marketing à identifier et à atténuer les biais dans leurs objectifs de création de persona.
        Choisir un biais cognitif dans le texte suivant et fournir un conseil spécifique pour atténuer ce biais.
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
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
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
def generate_persona_image(first_name, last_name, age, gender, persona_description, mode):
    if not first_name or not last_name or not age or not gender:
        return "Veuillez remplir tous les champs pour générer l'image du persona."

    prompt = f"A portrait photograph of a {gender} persona named {first_name} {last_name}, a {age}-year-old individual. {persona_description}. High-quality portrait, natural lighting, neutral background, genuine expression."
    
    if mode == "OpenAI":
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            print("Generated image URL:", image_url)
            
            # Télécharger l'image et l'enregistrer temporairement
            response = requests.get(image_url)
            temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            with open(temp_image.name, 'wb') as f:
                f.write(response.content)
            return temp_image.name
        except Exception as e:
            return {"error": str(e)}
    elif mode == "Temps réel":
        return generate_real_time_image(prompt)

# Function to assist in creating the detailed profile
def assist_persona_creation(first_name, last_name, age, personal_history, consumption_preferences, behaviors_habits, assistance_level):
    prompt = f"""
    Vous êtes un assistant IA aidant à créer des personas marketing détaillés.
    Basé sur les informations fournies, proposez des suggestions pour améliorer le profil du persona et identifiez les biais potentiels.

    Informations du persona :
    Nom : {first_name} {last_name}
    Âge : {age}
    Histoire personnelle : {personal_history}
    Préférences de consommation : {consumption_preferences}
    Comportements et habitudes : {behaviors_habits}

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
def generate_pdf(first_name, last_name, age, personal_history, consumption_preferences, behaviors_habits, image_url):
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
        c.drawString(50, y, "Histoire personnelle:")
        y -= 20
        c.drawString(50, y, personal_history)
        y -= 40
        c.drawString(50, y, "Préférences de consommation:")
        y -= 20
        c.drawString(50, y, ", ".join(consumption_preferences))
        y -= 40
        c.drawString(50, y, "Comportements et habitudes:")
        y -= 20
        c.drawString(50, y, ", ".join(behaviors_habits))

        c.save()
        return temp_pdf.name

    except Exception as e:
        return f"Erreur lors de la génération du PDF : {e}"

def generate_pdf_wrapper(first_name, last_name, age, personal_history, consumption_preferences, behaviors_habits, image_url):
    pdf_file = generate_pdf(first_name, last_name, age, personal_history, consumption_preferences, behaviors_habits, image_url)
    return pdf_file

# Function to review the persona details
def review_persona(first_name, last_name, age, personal_history, consumption_preferences, behaviors_habits, image_url):
    html_content = f"""
    <h2>{first_name} {last_name}, Age: {age}</h2>
    <img src="{image_url}" alt="Persona Image" width="200">
    <h3>Histoire personnelle</h3>
    <p>{personal_history}</p>
    <h3>Préférences de consommation</h3>
    <p>{consumption_preferences}</p>
    <h3>Comportements et habitudes</h3>
    <p>{behaviors_habits}</p>
    """
    return html_content

# Initialiser le client pour l'API de génération d'image en temps réel
image_client = None
try:
    image_client = Client("cbensimon/Real-Time-Text-to-Image-SDXL-Lightning")
    image_client_initialized = True
except Exception as e:
    print(f"Erreur lors de l'initialisation du client Gradio: {e}")
    image_client_initialized = False

# Fonction pour générer une image en temps réel
def generate_real_time_image(prompt_text, seed=0):
    if not image_client_initialized:
        return {"error": "Le client Gradio n'a pas pu être initialisé. Veuillez vérifier votre configuration."}
    try:
        result = image_client.predict(prompt_text, seed, api_name="/predict")
        image_path = result  # Le résultat est un chemin de fichier
        print("Generated lightning image path:", image_path)
        
        # Lire l'image depuis le chemin de fichier et l'enregistrer temporairement
        with open(image_path, 'rb') as f:
            image_data = f.read()
        temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        with open(temp_image.name, 'wb') as f:
            f.write(image_data)
        return temp_image.name
    except Exception as e:
        error_message = str(e)
        if "exceeded your GPU quota" in error_message:
            return {"error": "Vous avez dépassé votre quota GPU. Veuillez réessayer plus tard."}
        print("Error in generate_real_time_image:", error_message)
        return {"error": error_message}

# Fonction pour générer l'image du persona en fonction du mode sélectionné
def generate_persona_image(first_name, last_name, age, gender, persona_description, mode):
    if not first_name or not last_name or not age or not gender:
        return "Veuillez remplir tous les champs pour générer l'image du persona."

    prompt = f"A portrait photograph of a {gender} persona named {first_name} {last_name}, a {age}-year-old individual. {persona_description}. High-quality portrait, natural lighting, neutral background, genuine expression."
    
    if mode == "OpenAI":
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            print("Generated image URL:", image_url)
            
            # Télécharger l'image et l'enregistrer temporairement
            response = requests.get(image_url)
            temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            with open(temp_image.name, 'wb') as f:
                f.write(response.content)
            return temp_image.name
        except Exception as e:
            return {"error": str(e)}
    elif mode == "Temps réel":
        return generate_real_time_image(prompt)

# Fonction pour remplir automatiquement les champs avec l'IA
def auto_fill_persona_fields(first_name, last_name, age):
    prompt = f"""
    Vous êtes un assistant IA qui génère des informations détaillées pour un persona marketing.

    Générer l'histoire personnelle, les préférences de consommation, et les comportements et habitudes pour un persona nommé {first_name} {last_name}, âgé de {age} ans.

    Fournissez les informations sous le format suivant:

    Histoire personnelle:
    [texte]

    Préférences de consommation:
    [texte]

    Comportements et habitudes:
    [texte]
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500,
    )
    content = response.choices[0]['message']['content'].strip()
    # Traitement de la réponse pour extraire les sections
    result = {
        'personal_history': '',
        'consumption_preferences': '',
        'behaviors_habits': ''
    }
    sections = content.split('\n\n')
    for section in sections:
        if "Histoire personnelle:" in section:
            result['personal_history'] = section.replace("Histoire personnelle:", "").strip()
        elif "Préférences de consommation:" in section:
            result['consumption_preferences'] = section.replace("Préférences de consommation:", "").strip()
        elif "Comportements et habitudes:" in section:
            result['behaviors_habits'] = section.replace("Comportements et habitudes:", "").strip()
    return result

# Fonction pour mettre à jour l'interface en fonction du niveau d'assistance
def update_step3_ui(assistance_level, first_name, last_name, age):
    if assistance_level == "Manuel":
        return {
            generate_suggestions_button: gr.update(visible=False),
            personal_history_input: gr.update(value="", interactive=True),
            consumption_preferences_input: gr.update(value="", interactive=True),
            behaviors_habits_input: gr.update(value="", interactive=True)
        }
    elif assistance_level == "Semi-guidé":
        return {
            generate_suggestions_button: gr.update(visible=True),
            personal_history_input: gr.update(interactive=True),
            consumption_preferences_input: gr.update(interactive=True),
            behaviors_habits_input: gr.update(interactive=True)
        }
    elif assistance_level == "Entièrement guidé":
        auto_fill_values = auto_fill_persona_fields(first_name, last_name, age)
        return {
            generate_suggestions_button: gr.update(visible=False),
            personal_history_input: gr.update(value=auto_fill_values['personal_history'], interactive=False),
            consumption_preferences_input: gr.update(value=auto_fill_values['consumption_preferences'], interactive=False),
            behaviors_habits_input: gr.update(value=auto_fill_values['behaviors_habits'], interactive=False)
        }

# Fonction pour sauvegarder les informations du persona
def sauvegarder(personal_history, consumption_preferences, behaviors_habits):
    # Implémentation de la sauvegarde (par exemple, enregistrement dans un fichier)
    # Pour cet exemple, nous renvoyons simplement un message de confirmation
    return "Les informations ont été sauvegardées avec succès."

# Interface utilisateur Gradio avec des blocs dynamiques pour les biais et la génération d'image en temps réel
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

        # Fonction pour afficher dynamiquement les biais et les conseils
        def display_biases_and_advice(objective_text, previous_count, realtime):
            current_count = len(objective_text.split())
            if realtime == "Activée" and current_count - previous_count >= 10:
                analysis_result = analyze_biases(objective_text)
                if "error" in analysis_result:
                    return f"Erreur: {analysis_result['error']}", previous_count, f"Nombre de mots : {current_count}"
                
                biases = analysis_result.get("biases", [])
                advice = analysis_result.get("advice", [])
                
                if not biases or not advice:
                    return "Aucun biais détecté ou conseils disponibles.", current_count, f"Nombre de mots : {current_count}"
                
                content = ""
                for bias, adv in zip(biases, advice):
                    content += f"{bias}\n\n**Conseil:** {adv}\n\n"
                return content, current_count, f"Nombre de mots : {current_count}"
            return bias_analysis_output, previous_count, f"Nombre de mots : {current_count}"  # Conserver l'état précédent sans changement

        # Utilisation du bouton pour déclencher l'analyse des biais
        def analyze_button_click(objective_text, previous_count, realtime):
            current_count = len(objective_text.split())
            analysis_result = analyze_biases(objective_text)
            if "error" in analysis_result:
                return f"Erreur: {analysis_result['error']}", previous_count, f"Nombre de mots : {current_count}"
            
            biases = analysis_result.get("biases", [])
            advice = analysis_result.get("advice", [])
            
            if not biases or not advice:
                return "Aucun biais détecté ou conseils disponibles.", previous_count, f"Nombre de mots : {current_count}"
            
            content = ""
            for bias, adv in zip(biases, advice):
                content += f"{bias}\n\n**Conseil:** {adv}\n\n"
            return content, previous_count, f"Nombre de mots : {current_count}"

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
                persona_description_input = gr.Textbox(label="Description du persona", lines=3)
                image_mode = gr.Radio(label="Mode de génération d'image", choices=["OpenAI", "Temps réel"], value="OpenAI")
                generate_image_button = gr.Button("Générer l'image du persona")
            with gr.Column(scale=1):
                persona_image_output = gr.Image(label="Image du persona")
        
        generate_image_button.click(
            fn=generate_persona_image,
            inputs=[first_name_input, last_name_input, age_input, gender_input, persona_description_input, image_mode],
            outputs=persona_image_output
        )

        # Génération d'image en temps réel tous les deux mots ajoutés
        def generate_image_realtime(first_name, last_name, age, gender, persona_description, previous_count, mode):
            current_count = len(persona_description.split())
            if current_count - previous_count >= 2:
                image_url = generate_persona_image(first_name, last_name, age, gender, persona_description, mode)
                return image_url, current_count
            return persona_image_output, previous_count

        persona_description_input.change(
            fn=generate_image_realtime,
            inputs=[first_name_input, last_name_input, age_input, gender_input, persona_description_input, word_count_state, image_mode],
            outputs=[persona_image_output, word_count_state]
        )

    with gr.Tab("Étape 3: Profil détaillé du Persona"):
        assistance_level = gr.Radio(
            label="Niveau d'assistance de l'IA",
            choices=["Entièrement guidé", "Semi-guidé", "Manuel"],
            value="Semi-guidé"
        )
        with gr.Row():
            with gr.Column():
                personal_history_input = gr.Textbox(label="Histoire personnelle", lines=3)
                consumption_preferences_input = gr.Textbox(label="Préférences de consommation", lines=2)
                behaviors_habits_input = gr.Textbox(label="Comportements et habitudes", lines=2)
                generate_suggestions_button = gr.Button("Générer des suggestions")
                sauvegarder_button = gr.Button("Sauvegarder")  # Bouton "Sauvegarder" ajouté
            with gr.Column():
                persona_visualization_output = gr.HTML(label="Visualisation du Persona")
        
        # Statut de la sauvegarde
        sauvegarde_statut = gr.Textbox(label="Statut", interactive=False)

        # Mise à jour de l'interface lors du changement du niveau d'assistance
        assistance_level.change(
            fn=update_step3_ui,
            inputs=[assistance_level, first_name_input, last_name_input, age_input],
            outputs=[generate_suggestions_button, personal_history_input, consumption_preferences_input, behaviors_habits_input]
        )

        # Utiliser un DataFrame pour afficher les suggestions
        suggestions_output = gr.Dataframe(headers=["Suggestion"], label="Suggestions de l'IA")
        bias_highlight_output = gr.HTML(label="Biais détectés")

        # Fonction pour générer les suggestions et gérer les biais
        def generate_and_display_suggestions(first_name, last_name, age, personal_history, consumption_preferences, behaviors_habits, assistance_level):
            data = {
                'first_name': first_name,
                'last_name': last_name,
                'age': age,
                'personal_history': personal_history,
                'consumption_preferences': consumption_preferences,
                'behaviors_habits': behaviors_habits
            }
            suggestions = assist_persona_creation(
                first_name, last_name, age,
                personal_history, consumption_preferences, behaviors_habits,
                assistance_level
            )
            biases = detect_biases(suggestions)
            highlighted_suggestions = highlight_biases(suggestions, biases)
            # Préparation des suggestions pour affichage
            suggestions_list = []
            for suggestion in suggestions.split('\n'):
                if suggestion.strip():
                    suggestions_list.append([suggestion.strip()])
            suggestions_df = pd.DataFrame(suggestions_list, columns=["Suggestion"])
            visualization = generate_persona_visualization(data)
            return suggestions_df, highlighted_suggestions, visualization

        generate_suggestions_button.click(
            fn=generate_and_display_suggestions,
            inputs=[
                first_name_input, last_name_input, age_input,
                personal_history_input, consumption_preferences_input, behaviors_habits_input,
                assistance_level
            ],
            outputs=[suggestions_output, bias_highlight_output, persona_visualization_output]
        )

        # Action du bouton "Sauvegarder"
        sauvegarder_button.click(
            fn=sauvegarder,
            inputs=[personal_history_input, consumption_preferences_input, behaviors_habits_input],
            outputs=sauvegarde_statut
        )

    with gr.Tab("Étape 4: Génération du PDF"):
        gr.Markdown("### Génération du PDF du persona")
        generate_pdf_button = gr.Button("Générer le PDF")
        pdf_output = gr.File(label="Télécharger le PDF")
        generate_pdf_button.click(
            fn=generate_pdf_wrapper,
            inputs=[first_name_input, last_name_input, age_input, personal_history_input, consumption_preferences_input, behaviors_habits_input, persona_image_output],
            outputs=pdf_output
        )



demo.launch(debug=True)