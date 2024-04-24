import socket
import numpy as np
from PIL import Image
import io
import matplotlib.pyplot as plt

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

def display_image_from_bytes(image_bytes):
    # Create a BytesIO object to read the image bytes
    image_stream = io.BytesIO(image_bytes)
    # Open the image using PIL (Python Imaging Library)
    image = Image.open(image_stream)
    # Display the image
    image.show()


# Send the image
image_path = "1200px-2019_Toyota_Corolla_Icon_Tech_VVT-i_Hybrid_1.8.jpg"  # Replace with the actual image path
# Open the image file and read its bytes
with open(image_path, 'rb') as f:
        image_bytes = f.read()



# processed_segments_bytes = []
# for segment in segments:
#     processed_segment_bytes= segment
#     display_image_from_bytes(processed_segment_bytes)
#     processed_segments_bytes.append(processed_segment_bytes)
# # Concatenate all processed segments to form the processed image
# processed_image_bytes = b"".join(processed_segments_bytes)

# # Display the processed image
# display_image_from_bytes(processed_image_bytes)
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

# Combine the segments to form the processed image and return as bytes

# Combine the segments to form the processed image
segments = split_image(5, image_bytes)
combined_image_path = combine_segments_to_bytes(segments)
display_image_from_bytes(combined_image_path)
# Combine the segments to form the processed image


