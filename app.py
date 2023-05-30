import os;
import cv2;
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
from flask_cors import cross_origin, CORS
from Analysis import detect_acne, get_bounding_box
from keras.models import load_model


app = Flask(__name__)
cors = CORS(app)

app.config['UPLOAD_FOLDER'] = 'static/'

# load model
model = load_model('models/model_mobilenetv2_V1.h5')

@app.route('/', methods=['POST'])
@cross_origin()
def index():
    image = request.files["image"]
    filename = secure_filename(image.filename)
    image_path = image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    image_result, acne_class, confidence = detect_acne(image_path, model, 0.5)
    image_result = cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'result.jpg'), image_result)
    response = jsonify({
        "message" : 'success',
        "data" : {
            "image_result" : image_result,
            "acne_type" : acne_class,
            "confidence" : confidence
        }
    })
    response.headers.add("Access-Control-Allow-Origin", "*")

    return response

if __name__ == '__main__':
    app.run(debug=True)
