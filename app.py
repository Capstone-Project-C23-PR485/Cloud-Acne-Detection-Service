from flask import Flask, request
import json
import base64
from keras.models import load_model
from Analysis import detect_acne

app = Flask(__name__)
model = load_model('gs://public-picture-media-bucket/ml_models/model_mobilenetv2_V1.h5')

@app.route('/', methods=['POST'])
def index():
    """ Receive and parse pubsub request"""
    payload = request.get_json()

    # check the pubsub request payload
    if not payload:
        msg = "no pubsub payload received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400
    
    if not isinstance(payload, dict):
        msg = "invalid payload format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400
    
    # decode pubsub message
    pubsub_message = payload["message"]

    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        try:
            data = json.loads(base64.b64decode(pubsub_message["data"]).decode())
        except Exception as e:
            msg = (
                "Invalid Pub/Sub message: "
                "data property is not valid base64 encoded JSON"
            )
            print(f"error: {msg}")
            return f"Bad Request: {msg}", 400
        
        if not data["name"] or not data["bucket"]:
            msg = (
                "Invalid Cloud Storage notification: "
                "expected name and bucket properties"
            )
            print(f"error: {msg}")
            return f"Bad Request: {msg}", 400
        
        try:
            detect_acne(data, model, 0.5)
            return ("", 204)
        except Exception as e:
            print(f"error: {e}")
            return ("", 500)
        
    return ("", 500)