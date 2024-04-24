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


# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Replace 'server_public_ip' with the public IP of the server
server_public_ip = 'localhost'
port = 12345

# Connect to the server
client_socket.connect((server_public_ip, port))

# Send the image
image_path = "1200px-2019_Toyota_Corolla_Icon_Tech_VVT-i_Hybrid_1.8.jpg"  # Replace with the actual image path
# Open the image file and read its bytes
with open(image_path, 'rb') as f:
        image_bytes = f.read()




# Send the image
# segments=split_image(4,image_bytes)
# for s in segments:
#     client_socket.send("ed".encode('utf-8'))
#     send_image_segments(client_socket,s)

# while True:

#     user_input = input("Enter the operation: ")
#     client_socket.send(user_input.encode('utf-8'))
#     # send_image(client_socket, image_path)
#     send_image_segments(client_socket,image_bytes)
#     image=receive_image(client_socket)                                            
#     display_image_from_bytes(image[0])
#     user_input = input("do you want to quit Y/N: ")
#     if user_input=="Y":
#         client_socket.send("q".encode('utf-8'))
#         break
#     else:continue



    # Send the image
    #######################################################
# processed_image_bytes = b''
# segments=split_image(4,image_bytes)
# for s in segments:
#     client_socket.send("ed".encode('utf-8'))
#     send_image_segments(client_socket, s)
#     processed_segment_bytes= receive_image(client_socket)[0]
#     processed_image_bytes = processed_image_bytes+processed_segment_bytes    
#     # display_image_from_bytes(processed_segment_bytes)       
#     display_image_from_bytes(processed_image_bytes)                        
# display_image_from_bytes(processed_image_bytes)
######################################
# Send the image
segments = split_image(2, image_bytes)
processed_segments_bytes = []
for segment in segments:
    client_socket.send("ed".encode('utf-8'))
    send_image_segments(client_socket, segment)
    processed_segment_bytes, _ = receive_image(client_socket)
    display_image_from_bytes(processed_segment_bytes)
    processed_segments_bytes.append(processed_segment_bytes)
# Concatenate all processed segments to form the processed image
processed_image_bytes = b"".join(processed_segments_bytes)

# Display the processed image
display_image_from_bytes(processed_image_bytes)


# Close the connection with the server
client_socket.close()