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

def gaussian_blur(byte_image, kernel_size=(31, 31)):
    image = np.frombuffer(byte_image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    blurred_image = cv2.GaussianBlur(image, kernel_size, 0)
    _, img_encoded = cv2.imencode('.jpg', blurred_image)
    return img_encoded.tobytes()

def laplacian(byte_image):
    image = np.frombuffer(byte_image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)
    laplacian_image = cv2.Laplacian(image, cv2.CV_64F)
    laplacian_image = np.uint8(np.absolute(laplacian_image))
    _, img_encoded = cv2.imencode('.jpg', laplacian_image)
    return img_encoded.tobytes()

def invert_colors(byte_image):
    image = np.frombuffer(byte_image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    inverted_image = cv2.bitwise_not(image)
    _, img_encoded = cv2.imencode('.jpg', inverted_image)
    return img_encoded.tobytes()

def apply_red_filter(byte_image):
    image = np.frombuffer(byte_image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    filtered_image = np.zeros_like(image)
    filtered_image[:,:,2] = image[:,:,2]
    _, img_encoded = cv2.imencode('.jpg', filtered_image)
    return img_encoded.tobytes()

def apply_green_filter(byte_image):
    image = np.frombuffer(byte_image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    filtered_image = np.zeros_like(image)
    filtered_image[:,:,1] = image[:,:,1]
    _, img_encoded = cv2.imencode('.jpg', filtered_image)
    return img_encoded.tobytes()

def apply_blue_filter(byte_image):
    image = np.frombuffer(byte_image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    filtered_image = np.zeros_like(image)
    filtered_image[:,:,0] = image[:,:,0] 
    _, img_encoded = cv2.imencode('.jpg', filtered_image)
    return img_encoded.tobytes()

def adjust_brightness_contrast(byte_image, alpha=1.5, beta=40):
    image = np.frombuffer(byte_image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    adjusted_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    _, img_encoded = cv2.imencode('.jpg', adjusted_image)
    return img_encoded.tobytes()

def convert_color_space(byte_image, target_color_space=cv2.COLOR_BGR2HSV):
    image = np.frombuffer(byte_image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    converted_image = cv2.cvtColor(image, target_color_space)
    _, img_encoded = cv2.imencode('.jpg', converted_image)
    return img_encoded.tobytes()

def apply_heat_filter(byte_image):
    image = np.frombuffer(byte_image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)
    heatmap = cv2.applyColorMap(image, cv2.COLORMAP_JET)
    
    _, img_encoded = cv2.imencode('.jpg', heatmap)
    return img_encoded.tobytes()