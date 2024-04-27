import cv2
import numpy as np


def greyFilter(image_bytes):
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed_image_bytes = cv2.imencode('.jpg', processed_image)[1].tobytes()
    return processed_image_bytes


def edgeDetection(image_bytes):
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray_image, 100, 200)
    edges_bytes = cv2.imencode('.jpg', edges)[1].tobytes()
    return edges_bytes


def imageFiltering(image_bytes):
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
    kernel_sharpening = np.array([[-1, -1, -1],
                                [-1, 9, -1],
                                [-1, -1, -1]])
    sharpened_image = cv2.filter2D(blurred_image, -1, kernel_sharpening)
    filtered_image_bytes = cv2.imencode('.jpg', sharpened_image)[1].tobytes()
    return filtered_image_bytes
