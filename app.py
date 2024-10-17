import gradio as gr
import openai
from fpdf import FPDF
import tempfile
import requests
import os
import tempfile
import pydantic

# Function to set the OpenAI API key
def set_openai_api_key(api_key):
    openai.api_key = api_key
    return "La clé de l'API OpenAI a été définie avec succès."

# Function to analyze biases in the objective text
def analyze_biases(objective_text):
    prompt = f"""
  Vous êtes un assistant IA formé à l'analyse de textes pour y déceler des biais cognitifs.
  Analysez le texte suivant à la recherche de biais cognitifs potentiels et donnez des conseils sur la manière de les atténuer.
  
  Texte :
  {objectif_texte}
  
  Fournissez votre analyse dans un langage clair et concis.
  """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500,
    )
    analysis = response.choices[0].message.content.strip()
    return analysis

# Function to generate the persona image using OpenAI's Image API
def generate_persona_image_wrapper(first_name, last_name, age, description):
    prompt = f"{description}. The person's name is {first_name} {last_name}, age {age}."
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    
    # Download the image and save it in a temporary file
    response = requests.get(image_url)
    
    # Create a temporary directory to store the image
    temp_dir = tempfile.gettempdir()
    temp_image_path = os.path.join(temp_dir, f"{first_name}_{last_name}_persona.png")
    
    # Save the image with exception handling
    try:
        with open(temp_image_path, 'wb') as f:
            f.write(response.content)
    except IOError as e:
        return f"Error saving image: {e}"
    
    return temp_image_path

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
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500,
    )
    suggestions = response.choices[0].message.content.strip()
    return suggestions

# Function to generate the PDF of the persona
def generate_pdf(first_name, last_name, age, personal_history, consumption_preferences, behaviors_habits, image_url):
    pdf = FPDF()
    pdf.add_page()

    # Download the image to a temporary file
    response = requests.get(image_url)
    temp_image = tempfile.NamedTemporaryFile(delete=True, suffix='.png')
    try:
        with open(temp_image.name, 'wb') as f:
            f.write(response.content)
    except IOError as e:
        return f"Error saving image to PDF: {e}"

    # Add the image to the PDF
    pdf.image(temp_image.name, x=10, y=8, w=50)

    # Remove the temporary image file
    os.unlink(temp_image.name)

    pdf.set_xy(70, 10)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'{first_name} {last_name}, Age: {age}', ln=True)

    pdf.set_font('Arial', '', 12)
    pdf.ln(20)
    pdf.multi_cell(0, 10, f'**Personal History:**\n{personal_history}')
    pdf.ln(5)
    pdf.multi_cell(0, 10, f'**Consumption Preferences:**\n{consumption_preferences}')
    pdf.ln(5)
    pdf.multi_cell(0, 10, f'**Behaviors and Habits:**\n{behaviors_habits}')

    # Save the PDF to a temporary file and return the file path
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    try:
        pdf.output(temp_pdf.name)
    except IOError as e:
        return f"Error saving PDF: {e}"
    
    return temp_pdf.name

def generate_pdf_wrapper(first_name, last_name, age, personal_history, consumption_preferences, behaviors_habits, image_url):
    pdf_file = generate_pdf(first_name, last_name, age, personal_history, consumption_preferences, behaviors_habits, image_url)
    return pdf_file

# Function to review the persona details
def review_persona(first_name, last_name, age, personal_history, consumption_preferences, behaviors_habits, image_url):
    html_content = f"""
    <h2>{first_name} {last_name}, Age: {age}</h2>
    <img src="{image_url}" alt="Persona Image" width="200">
    <h3>Personal History</h3>
    <p>{personal_history}</p>
    <h3>Consumption Preferences</h3>
    <p>{consumption_preferences}</p>
    <h3>Behaviors and Habits</h3>
    <p>{behaviors_habits}</p>
    """
    return html_content

# Cyborg Mode: Analyzing user input dynamically for cognitive biases
with gr.Blocks() as demo:
    gr.Markdown("# Persona Creation Assistant")
    gr.Markdown("Please enter your OpenAI API key to proceed.")
    api_key_input = gr.Textbox(label="Enter your OpenAI API key", type="password")
    api_key_button = gr.Button("Set API Key")
    api_key_status = gr.Textbox(label="API Key Status", interactive=False)

    api_key_button.click(fn=set_openai_api_key, inputs=api_key_input, outputs=api_key_status)

    with gr.Tab("Step 1: Objective"):
        objective_input = gr.Textbox(label="Describe the objective of your persona", lines=5)
        analyze_button = gr.Button("Analyze for Cognitive Biases")
        analysis_output = gr.Textbox(label="Bias Analysis", interactive=False)

        analyze_button.click(fn=analyze_biases, inputs=objective_input, outputs=analysis_output)

        # Dynamic Bias Analysis Assistance in Cyborg Mode
        @gr.render(inputs=objective_input)
        def dynamic_bias_analysis(text):
            word_count = len(text.split())
            if word_count > 40 and word_count % 10 == 0:
                analysis = analyze_biases(text)
                gr.Markdown(f"### Dynamic Analysis Suggestion:\n{analysis}")

    with gr.Tab("Step 2: Basic Information and Image"):
        first_name_input = gr.Textbox(label="First Name")
        last_name_input = gr.Textbox(label="Last Name")
        age_input = gr.Number(label="Age", precision=0)
        persona_description_input = gr.Textbox(label="Describe how the persona should look", lines=3)
        generate_image_button = gr.Button("Generate Persona Image")
        persona_image_output = gr.Image(label="Persona Image")

        generate_image_button.click(
            fn=generate_persona_image_wrapper,
            inputs=[first_name_input, last_name_input, age_input, persona_description_input],
            outputs=persona_image_output
        )

    with gr.Tab("Step 3: Detailed Profile"):
        personal_history_input = gr.Textbox(label="Personal History", lines=3)
        consumption_preferences_input = gr.Textbox(label="Consumption Preferences", lines=3)
        behaviors_habits_input = gr.Textbox(label="Behaviors and Habits", lines=3)
        assist_button = gr.Button("Get AI Assistance")
        assistance_output = gr.Textbox(label="AI Suggestions", interactive=False)

        assist_button.click(
            fn=assist_persona_creation,
            inputs=[first_name_input, last_name_input, age_input, personal_history_input, consumption_preferences_input, behaviors_habits_input],
            outputs=assistance_output
        )

    with gr.Tab("Step 4: Review and Export"):
        gr.Markdown("### Review Your Persona")
        review_output = gr.HTML()
        review_button = gr.Button("Review Persona")
        review_button.click(
            fn=review_persona,
            inputs=[first_name_input, last_name_input, age_input, personal_history_input, consumption_preferences_input, behaviors_habits_input, persona_image_output],
            outputs=review_output
        )

        generate_pdf_button = gr.Button("Generate PDF")
        pdf_output = gr.File(label="Download Persona PDF")

        generate_pdf_button.click(
            fn=generate_pdf_wrapper,
            inputs=[first_name_input, last_name_input, age_input, personal_history_input, consumption_preferences_input, behaviors_habits_input, persona_image_output],
            outputs=pdf_output
        )

demo.launch(debug=True)