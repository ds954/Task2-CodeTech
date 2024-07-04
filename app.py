!pip install pyngrok
!pip install diffusers
!pip install accelerate
!pip install flask-ngrok

# Importing required libraries
import os
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import logging
from flask import Flask, render_template, request
from flask_ngrok import run_with_ngrok
from pyngrok import ngrok

port = 5000
# Initialize Flask application
app = Flask(__name__, template_folder="/content/Task2/templates", static_folder="/content/Task2/static")
logging.basicConfig(level=logging.DEBUG)

# Set ngrok auth token and connect to ngrok
ngrok.set_auth_token("2ikEqx2vkMg7BrP2tyhnN9ox1rt_7ggHEXBcQiKrxzEKVU7Ze")
public_url = ngrok.connect(port).public_url

app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'generated_images')

# Load Stable Diffusion model
pipeline = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", torch_dtype=torch.float16)
pipeline = pipeline.to('cuda')  # Move pipeline to GPU

# Function to generate images based on prompts
def generate_images(n_images, prompt_text='a girl in rain'):
    prompt = [prompt_text] * n_images
    images = pipeline(prompt).images
    return images

# Route to display form for entering prompt
@app.route('/')
def index():
    return render_template("index.html")

# Route to generate and display images
@app.route('/generate', methods=["POST"])
def generate():
    prompt_text = request.form['prompt']
    n_images = 6  # Number of images to generate
    images = generate_images(n_images, prompt_text)

    image_paths = []
    for i, img in enumerate(images):
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'generated_image_{i}.png')
        img.save(image_path)
        image_paths.append(f'generated_images/generated_image_{i}.png')

    # Render HTML template with the generated images
    return render_template("result.html", image_paths=image_paths)

# Run the Flask application
if __name__ == '__main__':
    print(f"To access the app, go to: {public_url}")
    app.run(port=port)
