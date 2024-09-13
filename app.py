from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from gradio_client import Client, file
import shutil
import boto3
import io


s3_client = boto3.client(
    's3',
    aws_access_key_id='AKIAZQ3DTG4U7QOPUJPC',
    aws_secret_access_key='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',
    region_name='us-east-1'
)
bucket_name = 'fptvton'


# Initialize the Flask app
app = Flask(__name__)


import secrets
import string

def generate_private_key(length=25):
    # Xác định các ký tự có thể xuất hiện trong khóa
    characters = string.ascii_letters + string.digits
    # Tạo khóa ngẫu nhiên với độ dài đã cho
    private_key = ''.join(secrets.choice(characters) for _ in range(length))
    return private_key





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
            return result_img, segmentation_img



        if model_image and cloth_image:

            key2 = generate_private_key()
            # Upload to S3
            s3_client.upload_fileobj(model_image, bucket_name, f'static/uploads/{key2}/image_model.png')
            s3_client.upload_fileobj(cloth_image, bucket_name, f'static/uploads/{key2}/image_cloth.png')
            model_image_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/uploads/{key2}/image_model.png'
            cloth_image_url =f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/uploads/{key2}/image_cloth.png'


            # Here you would call your model processing function to generate the output
            result_img, segmentation_img = process_images(model_image_url,cloth_image_url)
    

            key1 = generate_private_key()
            s3_client.upload_file(result_img, bucket_name, f'static/result/{key1}/img_result.png')
            s3_client.upload_file(segmentation_img, bucket_name, f'static/segmentation/{key1}/img_segmentation.png')

            segmentation_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/segmentation/{key1}/img_segmentation.png'
            result_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/result/{key1}/img_result.png'

            # Pass the results to the result page
            return render_template('result.html', segmentation_img_url=segmentation_img_url, result_img_url=result_img_url)

    return render_template('index.html')


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True,port= 5007)
