import io
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

def split_image(num_segments, image_bytes):
    img = np.array(Image.open(io.BytesIO(image_bytes)))
    height, width, _ = img.shape
    segment_height = height // num_segments
    segments = []
    for i in range(num_segments):
        start = i * segment_height
        end = start + segment_height
        if i == num_segments - 1:
            end = height
        segment = img[start:end, :, :]
        
        # Convert segment to bytes
        segment_bytes = io.BytesIO()
        Image.fromarray(segment).save(segment_bytes, format='JPEG')
        segment_bytes.seek(0)
        
        segments.append(segment_bytes.read())
    return segments


def combine_segments_to_bytes(segments):
    # Read the first segment to get the image dimensions
    first_segment = Image.open(io.BytesIO(segments[0]))
    width, height = first_segment.size
    
    # Create a new image with the same dimensions
    combined_image = Image.new("RGB", (width, height * len(segments)))
    
    # Paste each segment onto the combined image
    for i, segment_bytes in enumerate(segments):
        segment = Image.open(io.BytesIO(segment_bytes))
        combined_image.paste(segment, (0, i * height))
    
    # Save the combined image to a BytesIO object
    combined_image_bytes = io.BytesIO()
    combined_image.save(combined_image_bytes, format='JPEG')
    combined_image_bytes.seek(0)
    
    return combined_image_bytes.read()



def display_image_from_bytes(image_bytes):
    # Create a BytesIO object to read the image bytes
    image_stream = io.BytesIO(image_bytes)
    # Open the image using PIL (Python Imaging Library)
    image = Image.open(image_stream)
    # Display the image
    image.show()


def receive_image(conn):
    # Receive the length of the image
    length = int.from_bytes(conn.recv(4), byteorder='big')
    if length !=0:
        # Receive the image bytes
        image_bytes = b''
        while len(image_bytes) < length:
            data = conn.recv(length - len(image_bytes))
            if not data:
                break
            image_bytes += data
        return image_bytes,length
    
    
def send_image(conn, imagePath):
    with open(imagePath, 'rb') as f:
        image_bytes = f.read()
    # print(image_bytes)
    # Send the length of the image first
    conn.sendall(len(image_bytes).to_bytes(4, byteorder='big'))
    # Send the image bytes
    conn.sendall(image_bytes)


def send_image_segments(conn, image_bytes):
    # print(image_bytes)
    # Send the length of the image first
    conn.sendall(len(image_bytes).to_bytes(4, byteorder='big'))
    # Send the image bytes
    conn.sendall(image_bytes)


def send_image_knownbytes(conn, image):
    image_bytes = image[1] 
    # print(image_bytes)
    # Send the length of the image first
    conn.sendall(image_bytes.to_bytes(4, byteorder='big'))
    # Send the image bytes
    conn.sendall(image[0])