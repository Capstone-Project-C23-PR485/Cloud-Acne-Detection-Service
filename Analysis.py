import cv2
import os
import numpy as np
import requests
import urllib.request
from keras.applications.mobilenet_v2 import preprocess_input
# from keras.models import load_model # for testing purposes
from google.cloud import storage

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
    file_path = data['name']
    # TODO pisahkah prefix image-uploaded nya
    file_name = file_path.split('/')[1]
    bucket_name = data['bucket']

    image_path = f"https://storage.googleapis.com/{bucket_name}/{file_path}"

    # Read the input image using OpenCV
    req = urllib.request.urlopen(image_path)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    image = cv2.imdecode(arr, -1) # 'Load it as it is'

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
    
    # post_response = post_request(file_name=file_name, confidence=confidence, acne_class=acne_class)
    upload_response = upload_to_gcs(bucket_name, image_result, file_name)
    return upload_response

    
    
def upload_to_gcs(bucket_name, image_result, file_name):
    # gcs_bucket_name = 'public-picture-media-bucket'
    image_result = cv2.imwrite(f'static/{file_name}', image_result)

    destination_blob_name = f'images_result/{file_name}'
    storage_client = storage.Client(os.getenv('PROJECT_ID'))
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(f'static/{file_name}')
    os.remove(f'static/{file_name}')

def post_request(file_name, confidence, acne_class):
    gcs_bucket_url = f"{os.getenv('BUCKET_URL')}/images_result"
    data = {
      "id": file_name,
      "data": {"confidence": confidence, "detectnedAcne": acne_class},
      "image": f"{gcs_bucket_url}/{file_name}",
      "model": "acne"
    }

    response = requests.post('https://skincheckai-api-b6zefxgbfa-et.a.run.app/machine-learning/report-analyses', data=data)

    return response;


# for testing purposes
# data = {
#     'name' : 'download.jpg',
#     'bucket' : 'public-picture-media-bucket'
# }

# model = load_model('model.h5')

# detect_acne(data, model, 0.5)