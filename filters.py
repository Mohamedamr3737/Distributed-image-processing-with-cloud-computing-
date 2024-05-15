import cv2
import numpy as np

def gaussian_blur(byte_image, kernel_size=(31, 31)):
    """Apply Gaussian blur to the byte image"""
    image = np.frombuffer(byte_image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)  # Read the image in color
    blurred_image = cv2.GaussianBlur(image, kernel_size, 0)
    _, img_encoded = cv2.imencode('.jpg', blurred_image)
    return img_encoded.tobytes()

def adjust_brightness_contrast(byte_image, alpha=1.0, beta=0):
    """Adjust brightness and contrast of the byte image"""
    image = np.frombuffer(byte_image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    adjusted_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    _, img_encoded = cv2.imencode('.jpg', adjusted_image)
    return img_encoded.tobytes()

def split_channels(byte_image):
    """Split the image into individual color channels"""
    image = np.frombuffer(byte_image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    b, g, r = cv2.split(image)
    bgr_channels = [b, g, r]
    channel_images = [cv2.merge([c, np.zeros_like(c), np.zeros_like(c)]) for c in bgr_channels]
    encoded_images = [cv2.imencode('.jpg', img)[1].tobytes() for img in channel_images]
    return encoded_images

def histogram_equalization(byte_image):
    """Apply histogram equalization to the byte image"""
    image = np.frombuffer(byte_image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)
    equalized_image = cv2.equalizeHist(image)
    _, img_encoded = cv2.imencode('.jpg', equalized_image)
    return img_encoded.tobytes()

def convert_color_space(byte_image, target_color_space=cv2.COLOR_BGR2HSV):
    """Convert the color space of the byte image"""
    image = np.frombuffer(byte_image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    converted_image = cv2.cvtColor(image, target_color_space)
    _, img_encoded = cv2.imencode('.jpg', converted_image)
    return img_encoded.tobytes()

# def apply_heat_filter(byte_image):
#     """Apply a heat filter to the byte image"""
#     image = np.frombuffer(byte_image, dtype=np.uint8)
#     image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    
#     # Increase the intensity of red and orange channels
#     image[:,:,2] += 50  # Red channel
#     image[:,:,1] += 20  # Green channel (a little boost for yellowish tones)
    
#     # Clip values to ensure they remain within the valid range [0, 255]
#     image = np.clip(image, 0, 255)
    
#     _, img_encoded = cv2.imencode('.jpg', image)
#     return img_encoded.tobytes()
def apply_heat_filter(byte_image):
    """Apply a heat map filter to the byte image"""
    image = np.frombuffer(byte_image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)
    
    # Apply a colormap (e.g., 'jet') to the grayscale image
    heatmap = cv2.applyColorMap(image, cv2.COLORMAP_JET)
    
    _, img_encoded = cv2.imencode('.jpg', heatmap)
    return img_encoded.tobytes()
def test_color_manipulation(byte_image):
    """Test various color manipulation functions"""
    # Apply Gaussian blur
    blurred_img = gaussian_blur(byte_image)
    # Adjust brightness and contrast
    adjusted_img = adjust_brightness_contrast(byte_image, alpha=1.5, beta=50)
    # Split color channels
    channel_images = split_channels(byte_image)
    # Apply histogram equalization
    equalized_img = histogram_equalization(byte_image)
    # Convert color space (e.g., BGR to HSV)
    converted_img = convert_color_space(byte_image, target_color_space=cv2.COLOR_BGR2HSV)
    # Apply heat filter
    heat_filtered_img = apply_heat_filter(byte_image)

    # Display the results
    cv2.imshow('Original Image', cv2.imdecode(np.frombuffer(byte_image, dtype=np.uint8), cv2.IMREAD_COLOR))
    cv2.imshow('Blurred Image', cv2.imdecode(np.frombuffer(blurred_img, dtype=np.uint8), cv2.IMREAD_COLOR))
    cv2.imshow('Adjusted Image', cv2.imdecode(np.frombuffer(adjusted_img, dtype=np.uint8), cv2.IMREAD_COLOR))
    for i, img in enumerate(channel_images):
        cv2.imshow(f'Channel {i+1}', cv2.imdecode(np.frombuffer(img, dtype=np.uint8), cv2.IMREAD_COLOR))
    cv2.imshow('Equalized Image', cv2.imdecode(np.frombuffer(equalized_img, dtype=np.uint8), cv2.IMREAD_COLOR))
    cv2.imshow('Converted Image', cv2.imdecode(np.frombuffer(converted_img, dtype=np.uint8), cv2.IMREAD_COLOR))
    cv2.imshow('Heat Filtered Image', cv2.imdecode(np.frombuffer(heat_filtered_img, dtype=np.uint8), cv2.IMREAD_COLOR))

    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage:
# Load an image as bytes
with open('1200px-2019_Toyota_Corolla_Icon_Tech_VVT-i_Hybrid_1.8.jpg', 'rb') as f:
    byte_img = f.read()

# Test various color manipulation functions
test_color_manipulation(byte_img)
