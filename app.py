from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from gradio_client import Client, file
import shutil
# Initialize the Flask app
app = Flask(__name__)


# Folder to store uploaded images
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Home route to upload images
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the files from the form
        model_image = request.files['model_image']
        cloth_image = request.files['cloth_image']

        def process_images(model_img_path, cloth_img_path):
            # Load model and perform segmentation + virtual try-on
            # Return paths to segmentation image and try-on result

            client = Client("yisol/IDM-VTON")
            result = client.predict(
                dict={"background": file(
                    model_img_path), "layers": [],
                      "composite": None},
                garm_img=file(cloth_img_path),
                garment_des="Hello!!",
                is_checked=True,
                is_checked_crop=False,
                denoise_steps=30,
                seed=42,
                api_name="/tryon"
            )
            result_img, segmentation_img = result

            # Define the destination paths in the Flask static folder
            segmentation_output_path = os.path.join('static/result/segment/', os.path.basename(segmentation_img))
            result_output_path = os.path.join('static/result/result/', os.path.basename(result_img))

            # Copy the processed images from the temp folder to static/uploads
            shutil.copy(segmentation_img, segmentation_output_path)
            shutil.copy(result_img, result_output_path)

            return segmentation_output_path, result_output_path

        # Save the files
        if model_image and cloth_image:
            model_img_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(model_image.filename))
            cloth_img_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(cloth_image.filename))

            model_image.save(model_img_path)
            cloth_image.save(cloth_img_path)

            # Here you would call your model processing function to generate the output


            segmentation_img, result_img = process_images(model_img_path, cloth_img_path)


            # Pass the results to the result page
            return render_template('result.html', segmentation_img=segmentation_img, result_img=result_img)

    return render_template('index.html')


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
