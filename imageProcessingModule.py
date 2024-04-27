import cv2
import numpy as np

def greyFilter(image_bytes):
    # display_image_from_bytes(image_bytes)
    # send_image_knownbytes(client_socket,(image_bytes,length))
    # Perform image processing
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    # Example: Convert image to grayscale
    processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Optionally, send the processed image back to the client
    # convert processed image back to bytes
    processed_image_bytes = cv2.imencode('.jpg', processed_image)[1].tobytes()
    return processed_image_bytes

def edgeDetection(image_bytes):
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    # Convert image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Perform Canny edge detection
    edges = cv2.Canny(gray_image, 100, 200)  # Adjust the threshold values as needed
    # Display the detected edges
    # Optionally, send the detected edges back to the client
    # Convert edges to bytes
    edges_bytes = cv2.imencode('.jpg', edges)[1].tobytes()
    return edges_bytes


def imageFiltering(image_bytes):
    # Perform image filtering
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

    # Apply Gaussian blur
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)

    # Apply sharpening filter
    kernel_sharpening = np.array([[-1, -1, -1],
                                [-1, 9, -1],
                                [-1, -1, -1]])
    sharpened_image = cv2.filter2D(blurred_image, -1, kernel_sharpening)
    # Optionally, send the filtered image back to the client
    # Convert filtered image to bytes
    filtered_image_bytes = cv2.imencode('.jpg', sharpened_image)[1].tobytes()
    return filtered_image_bytes
