import socket
from PIL import Image
import io

def send_image(conn, imagePath):
    with open(imagePath, 'rb') as f:
        image_bytes = f.read()
    # print(image_bytes)
    # Send the length of the image first
    conn.sendall(len(image_bytes).to_bytes(4, byteorder='big'))
    # Send the image bytes
    conn.sendall(image_bytes)

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

def display_image_from_bytes(image_bytes):
    # Create a BytesIO object to read the image bytes
    image_stream = io.BytesIO(image_bytes)
    # Open the image using PIL (Python Imaging Library)
    image = Image.open(image_stream)
    # Display the image
    image.show()

imagePath="depositphotos_49418809-stock-photo-frog-on-the-leaf.jpg"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Replace 'server_public_ip' with the public IP of the server
server_public_ip = 'localhost'
port = 12348
# Connect to the server
client_socket.connect((server_public_ip, port))
client_socket.send("ed".encode('utf-8'))
send_image(client_socket,imagePath)
imageBytes,_=receive_image(client_socket)
display_image_from_bytes(imageBytes)
