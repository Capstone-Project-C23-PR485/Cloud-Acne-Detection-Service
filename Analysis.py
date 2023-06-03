import cv2
import numpy as np
import matplotlib.pyplot as plt
from keras.applications.mobilenet_v2 import preprocess_input



def get_bounding_box(image, threshold):
    # Placeholder implementation
    # Replace this with your actual bounding box calculation logic
    height, width, _ = image.shape
    xmin = int(width * 0.25)
    ymin = int(height * 0.25)
    xmax = int(width * 0.75)
    ymax = int(height * 0.75)
    return xmin, ymin, xmax, ymax

def detect_acne(image_path, model, threshold):
    result = {}

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
            # print(f"Type of acne: {acne_class}, Confidence: {confidence:.3f}")

        return image_result, acne_class, confidence
    else:
        return "congrats you dont have acne!!!"