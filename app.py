from flask import Flask, render_template, url_for, request, redirect, flash, send_from_directory
from flask_bootstrap import Bootstrap
from flask_colorpicker import colorpicker
import os
import model
import blend

app = Flask(__name__, template_folder='Template')
app.secret_key = os.urandom(12)
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
Bootstrap(app)
colorpicker(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def rgb_to_bgr(tuble_color):
    return tuple([tuble_color[2], tuble_color[1], tuble_color[0]])


"""
Routes
"""


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        output_path = 'static'
        uploaded_image = request.files['image']
        uploaded_effect = request.files['effect']
        uploaded_color = request.form.get('color')
        uploaded_color = uploaded_color[4:-1]
        color = [int(c) for c in uploaded_color.split(',')]
        color = tuple(color)
        color = rgb_to_bgr(color)
        # color = (178, 192, 192)
        if uploaded_image and allowed_file(uploaded_image.filename):
            if uploaded_effect and allowed_file(uploaded_effect.filename):
                image_path = os.path.join('static', uploaded_image.filename)
                uploaded_image.save(image_path)
                # print(image_path)

                effect_path = os.path.join('static', uploaded_effect.filename)
                uploaded_effect.save(effect_path)

                mask = model.get_mask(image_path, output_path)
                mask_path = os.path.join(output_path, mask)
                print(mask_path)

                blending = blend.blending(image_path, effect_path, mask_path, color, 0.5)
                blending = blend.fit_screen(blending, 1920, 1080)
                blend_name = blend.save('static', blending)
                output = url_for(output_path, filename=blend_name)
                print(output)

                return render_template('result.html', result=output)
        if uploaded_image.filename == '' or uploaded_effect == '':
            flash('No image selected for uploading')
            return render_template('error.html', Error='There is no file to upload')
        else:
            return render_template('error.html', Error='Wrong file format')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
