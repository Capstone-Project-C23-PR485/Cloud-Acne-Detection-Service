import cv2
import os
import numpy as np
import requests
import matplotlib.pyplot as plt
from keras.applications.mobilenet_v2 import preprocess_input
from google.cloud import storage


# TODO upload image result to cloud storage

def get_bounding_box(image, threshold):
    # Placeholder implementation
    # Replace this with your actual bounding box calculation logic
    height, width, _ = image.shape
    xmin = int(width * 0.25)
    ymin = int(height * 0.25)
    xmax = int(width * 0.75)
    ymax = int(height * 0.75)
    return xmin, ymin, xmax, ymax

def detect_acne(data, model, threshold):
    file_name = data['name']
    bucket_name = data['bucket']

    image_path = f"gs://{bucket_name}/{file_name}"

    # Read the input image using OpenCV
    image = cv2.imread(image_path)

    # Resize the image to the required dimensions
    if image is None:
      return ('Wrong path:', image_path)
    else:
      image = cv2.resize(image, dsize=(224,224))


    # Preprocess the image for model prediction
    input_data = preprocess_input(np.expand_dims(image, axis=0))

    # Perform the prediction using the loaded model
    predictions = model.predict(input_data)

    # Extract the acne instances and their class labels
    detections = []
    acne_labels = {
        0: 'papules',
        1: 'nodules',
        2: 'pustules',
        3: 'comedones'
    }

    for i, prediction in enumerate(predictions[0]):
        if prediction > threshold:
            acne_class = acne_labels[i]
            confidence = float(prediction)

            detections.append({
                'class': acne_class,
                'confidence': confidence
            })

    # Draw bounding boxes on the image for detected acne instances
    if len(detections) > 0:
        for detection in detections:
            acne_class = detection['class']
            confidence = detection['confidence']

            # Get the predicted bounding box coordinates
            xmin, ymin, xmax, ymax = get_bounding_box(image, threshold)

            # Draw the bounding box on the image with purple-red color
            color = (203, 0, 203)  # Purple-red color (BGR format)
            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)

        # Display the output image with bounding boxes
        image_result = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # print("You have acne.")
        for detection in detections:
            acne_class = detection['class']
            confidence = detection['confidence']
    else:
        image_result = image
        acne_class = None
        confidence = None
    
    post_response = post_request(file_name=file_name, confidence=confidence, acne_class=acne_class)
    upload_response = upload_to_gcs(bucket_name, image_result, file_name)
    return post_response, upload_response

    
    
def upload_to_gcs(bucket_name, image_result, file_name):
    # gcs_bucket_name = 'public-picture-media-bucket'
    image_result = cv2.imwrite(f'static/{file_name}', image_result)

    destination_blob_name = f'images_result/{file_name}'
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(f'static/{file_name}')
    os.remove(f'static/{file_name}')

def post_request(file_name, confidence, acne_class):
    gcs_bucket_url = 'gs://public-picture-media-bucket/images_result'
    data = {
      "id": 2,
      "data": {"confidence": confidence, "detectnedAcne": acne_class},
      "image": f"{gcs_bucket_url}/{file_name}",
      "model": "acne"
    }

    response = requests.post('https://skincheckai-api-b6zefxgbfa-et.a.run.app', data=data)

    return response;