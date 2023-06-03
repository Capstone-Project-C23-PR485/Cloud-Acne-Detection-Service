import os;
import cv2;
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
from flask_cors import cross_origin, CORS
from Analysis import detect_acne, get_bounding_box
from keras.models import load_model
from google.cloud import pubsub_v1


app = Flask(__name__)
cors = CORS(app)

app.config['ML_MODEL_PATH'] = 'gs://public-picture-media-bucket/ml_models/model_mobilenetv2_V1.h5'
app.config['IMAGE_UPLOADED_FOLDER'] = 'gs://public-picture-media-bucket/image_uploaded'
app.config['IMAGE_RESULT_FOLDER'] = 'gs://public-picture-media-bucket/image_result'

# app.config['UPLOAD_FOLDER'] = 'static/' # google storage bucket link

subscriber = pubsub_v1.SubscriberClient()

# TODO(developer)
project_id = "capstone-skincheckai"
subscription_id = "image-uploaded-subs"
timeout = 10.0
subscription_path = subscriber.subscription_path(project_id, subscription_id)

# load model
model = load_model(app.config['ML_MODEL_PATH']) #TODO ubah jadi path ke cloud storage bucket

@app.route('/report-analyses', methods=['POST'])
@cross_origin()
def index():
    image = request.files["image"]
    filename = secure_filename(image.filename)
    image_path = image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) # TODO arahkan ke cloud storage bucket 

    image_result, acne_class, confidence = detect_acne(image_path, model, 0.5)
    image_result = cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'result.jpg'), image_result)
    # upload image_result ke Google Cloud Storage
    # provide link result Google Cloud Storage
    response = jsonify({
        "message" : 'success',
        "data" : {
            # Id
            "image_result" : image_result,
            "acne_type" : acne_class,
            "confidence" : confidence
        }
    })
    response.headers.add("Access-Control-Allow-Origin", "*")

    return response

if __name__ == '__main__':
    app.run(debug=True)
